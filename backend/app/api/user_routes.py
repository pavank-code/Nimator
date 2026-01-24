"""
API routes for user data management.
Handles user history, chat sessions, videos, and topic studies.
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import redis
import uuid

from app.config import settings
from app.services.user_data_service import UserDataService, get_user_data_service

router = APIRouter(prefix="/user", tags=["user"])

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# Initialize service
user_data_service = UserDataService(redis_client)


def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """
    Get user ID from header or generate a new one.
    In production, this would use proper authentication.
    """
    if x_user_id:
        return x_user_id
    # Generate anonymous user ID
    return str(uuid.uuid4())


# ==================== REQUEST/RESPONSE MODELS ====================

class CreateChatRequest(BaseModel):
    message: str = Field(..., description="Initial message to start chat")
    topic: Optional[str] = Field(None, description="Topic category")


class AddMessageRequest(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class ChatSessionResponse(BaseModel):
    session_id: str
    title: Optional[str]
    topic: Optional[str]
    message_count: int
    created_at: str
    updated_at: str
    job_id: Optional[str]
    video_url: Optional[str]


class VideoRecordResponse(BaseModel):
    video_id: str
    job_id: str
    prompt: str
    topic: str
    video_url: Optional[str]
    status: str
    duration_seconds: int
    scene_count: int
    created_at: str
    completed_at: Optional[str]


class TopicStudyResponse(BaseModel):
    topic_id: str
    topic_name: str
    category: str
    video_count: int
    prompts_count: int
    last_studied: str
    first_studied: str


class UserDashboardResponse(BaseModel):
    user_id: str
    stats: Dict[str, int]
    recent_videos: List[Dict[str, Any]]
    topics: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    recent_chats: List[Dict[str, Any]]


# ==================== USER ENDPOINTS ====================

@router.get("/me")
async def get_current_user(user_id: str = Depends(get_user_id)):
    """Get or create current user and return their info."""
    user = user_data_service.get_or_create_user(user_id)
    return user.model_dump()


@router.get("/dashboard", response_model=UserDashboardResponse)
async def get_dashboard(user_id: str = Depends(get_user_id)):
    """Get user dashboard with stats and recent activity."""
    user_data_service.get_or_create_user(user_id)
    dashboard = user_data_service.get_user_dashboard(user_id)
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserDashboardResponse(
        user_id=user_id,
        stats=dashboard.get("stats", {}),
        recent_videos=dashboard.get("recent_videos", []),
        topics=dashboard.get("topics", []),
        recent_activities=dashboard.get("recent_activities", []),
        recent_chats=dashboard.get("recent_chats", [])
    )


# ==================== CHAT HISTORY ENDPOINTS ====================

@router.post("/chat")
async def create_chat_session(
    request: CreateChatRequest,
    user_id: str = Depends(get_user_id)
):
    """Create a new chat session."""
    user_data_service.get_or_create_user(user_id)
    session = user_data_service.create_chat_session(
        user_id=user_id,
        first_message=request.message,
        topic=request.topic
    )
    return {
        "session_id": session.session_id,
        "title": session.title,
        "messages": [m.model_dump() for m in session.messages]
    }


@router.get("/chat/history")
async def get_chat_history(
    limit: int = 50,
    user_id: str = Depends(get_user_id)
):
    """Get all chat sessions for the current user."""
    sessions = user_data_service.get_user_chat_sessions(user_id, limit)
    return {
        "sessions": [
            ChatSessionResponse(
                session_id=s.session_id,
                title=s.title,
                topic=s.topic,
                message_count=len(s.messages),
                created_at=s.created_at.isoformat() if s.created_at else "",
                updated_at=s.updated_at.isoformat() if s.updated_at else "",
                job_id=s.job_id,
                video_url=s.video_url
            ).model_dump()
            for s in sessions
        ],
        "total": len(sessions)
    }


@router.get("/chat/{session_id}")
async def get_chat_session(
    session_id: str,
    user_id: str = Depends(get_user_id)
):
    """Get a specific chat session with all messages."""
    session = user_data_service.get_chat_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "session_id": session.session_id,
        "title": session.title,
        "topic": session.topic,
        "messages": [m.model_dump() for m in session.messages],
        "job_id": session.job_id,
        "video_url": session.video_url,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None
    }


@router.post("/chat/{session_id}/message")
async def add_message(
    session_id: str,
    request: AddMessageRequest,
    user_id: str = Depends(get_user_id)
):
    """Add a message to a chat session."""
    session = user_data_service.get_chat_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    message = user_data_service.add_message_to_session(
        session_id=session_id,
        role=request.role,
        content=request.content,
        metadata=request.metadata
    )
    
    return message.model_dump() if message else None


@router.put("/chat/{session_id}/link-video")
async def link_video_to_chat(
    session_id: str,
    job_id: str,
    video_url: Optional[str] = None,
    user_id: str = Depends(get_user_id)
):
    """Link a generated video to a chat session."""
    session = user_data_service.get_chat_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    if session.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user_data_service.link_video_to_session(session_id, job_id, video_url)
    return {"status": "linked", "job_id": job_id}


# ==================== VIDEO HISTORY ENDPOINTS ====================

@router.get("/videos")
async def get_video_history(
    limit: int = 50,
    user_id: str = Depends(get_user_id)
):
    """Get all videos generated by the user."""
    videos = user_data_service.get_user_videos(user_id, limit)
    return {
        "videos": [
            VideoRecordResponse(
                video_id=v.video_id,
                job_id=v.job_id,
                prompt=v.prompt,
                topic=v.topic,
                video_url=v.video_url,
                status=v.status,
                duration_seconds=v.duration_seconds,
                scene_count=v.scene_count,
                created_at=v.created_at.isoformat() if v.created_at else "",
                completed_at=v.completed_at.isoformat() if v.completed_at else None
            ).model_dump()
            for v in videos
        ],
        "total": len(videos)
    }


@router.get("/videos/{video_id}")
async def get_video_record(
    video_id: str,
    user_id: str = Depends(get_user_id)
):
    """Get a specific video record."""
    record = user_data_service.get_video_record(video_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if record.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return record.model_dump()


# ==================== TOPIC STUDIES ENDPOINTS ====================

@router.get("/topics")
async def get_topic_studies(user_id: str = Depends(get_user_id)):
    """Get all topics studied by the user."""
    studies = user_data_service.get_user_topic_studies(user_id)
    return {
        "topics": [
            TopicStudyResponse(
                topic_id=s.topic_id,
                topic_name=s.topic_name,
                category=s.category,
                video_count=s.video_count,
                prompts_count=len(s.prompts_asked),
                last_studied=s.last_studied.isoformat() if s.last_studied else "",
                first_studied=s.first_studied.isoformat() if s.first_studied else ""
            ).model_dump()
            for s in studies
        ],
        "total": len(studies)
    }


@router.get("/topics/{topic_name}")
async def get_topic_detail(
    topic_name: str,
    user_id: str = Depends(get_user_id)
):
    """Get detailed information about a specific topic study."""
    study = user_data_service.get_topic_study(user_id, topic_name)
    
    if not study:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get videos for this topic
    videos = [
        user_data_service.get_video_record(vid)
        for vid in study.videos_generated
    ]
    videos = [v for v in videos if v is not None]
    
    return {
        "topic": study.model_dump(),
        "videos": [v.model_dump() for v in videos],
        "prompts": study.prompts_asked
    }


# ==================== ACTIVITY ENDPOINTS ====================

@router.get("/activities")
async def get_activities(
    limit: int = 20,
    user_id: str = Depends(get_user_id)
):
    """Get recent user activities."""
    activities = user_data_service.get_user_activities(user_id, limit)
    return {
        "activities": [a.model_dump() for a in activities],
        "total": len(activities)
    }


@router.post("/activities")
async def log_activity(
    activity_type: str,
    description: str,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: str = Depends(get_user_id)
):
    """Log a user activity."""
    activity = user_data_service.log_activity(
        user_id=user_id,
        activity_type=activity_type,
        description=description,
        metadata=metadata or {}
    )
    return activity.model_dump()
