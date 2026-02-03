"""
Orchestrated Tutor API - Synced DeepSeek + Qwen Pipeline

This endpoint uses the SessionOrchestrator to:
1. Process user messages with DeepSeek (tutoring)
2. Generate videos with Qwen (Manim code)
3. Return synced explanation + video generation status
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import redis.asyncio as redis
import json

from app.config import settings
from app.services.session_orchestrator import get_orchestrator

router = APIRouter(prefix="/tutor", tags=["Orchestrated Tutor"])


# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)


class ChatRequest(BaseModel):
    """Request for chat message."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class VisualObjectResponse(BaseModel):
    """A visual object in the scene."""
    object_id: str
    object_type: str
    display_name: str
    color: str


class ChatResponse(BaseModel):
    """Response from orchestrated chat."""
    session_id: str
    explanation: str
    video_generating: bool
    video_job_id: Optional[str] = None
    video_url: Optional[str] = None
    visual_objects: List[Dict[str, Any]] = []
    scene_spec: Optional[Dict[str, Any]] = None


class VideoStatusResponse(BaseModel):
    """Status of video generation job."""
    job_id: str
    status: str
    progress: int = 0
    video_url: Optional[str] = None
    error_message: Optional[str] = None


class SessionStateResponse(BaseModel):
    """Full session state for debugging."""
    session_id: str
    topic_root: str
    message_count: int
    scene_count: int
    visual_object_count: int
    current_branch_depth: int
    state: Dict[str, Any]


@router.post("/chat", response_model=ChatResponse)
async def orchestrated_chat(request: ChatRequest):
    """
    Process a chat message through the DeepSeek → Qwen pipeline.
    
    Flow:
    1. DeepSeek analyzes message and generates explanation
    2. If video needed, DeepSeek provides video intent
    3. Orchestrator converts intent to scene spec
    4. Qwen generates Manim code
    5. Renderer is triggered
    6. Returns explanation + video job status
    """
    orchestrator = get_orchestrator()
    
    try:
        result = await orchestrator.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        # Check if video is ready (for previously generated videos)
        video_url = None
        if result.get("video_job_id"):
            job_data = await redis_client.get(f"job:{result['video_job_id']}")
            if job_data:
                job = json.loads(job_data)
                if job.get("status") == "completed":
                    video_url = f"/videos/{result['video_job_id']}.mp4"
        
        return ChatResponse(
            session_id=result["session_id"],
            explanation=result["explanation"],
            video_generating=result["video_generating"],
            video_job_id=result.get("video_job_id"),
            video_url=video_url,
            visual_objects=result.get("visual_objects", []),
            scene_spec=result.get("scene_spec")
        )
        
    except Exception as e:
        print(f"Orchestrated chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/video/{job_id}", response_model=VideoStatusResponse)
async def get_video_status(job_id: str):
    """
    Get the status of a video generation job.
    
    Poll this endpoint to check when video is ready.
    """
    job_data = await redis_client.get(f"job:{job_id}")
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = json.loads(job_data)
    
    video_url = None
    if job["status"] == "completed":
        video_url = f"/videos/{job_id}.mp4"
    
    return VideoStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0),
        video_url=video_url,
        error_message=job.get("error_message")
    )


@router.get("/session/{session_id}", response_model=SessionStateResponse)
async def get_session_state(session_id: str):
    """
    Get the full session state for debugging/inspection.
    
    Shows all messages, scenes, visual objects, and branches.
    """
    orchestrator = get_orchestrator()
    state = orchestrator.get_session_state(session_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionStateResponse(
        session_id=state["session_id"],
        topic_root=state["topic_root"],
        message_count=len(state["messages"]),
        scene_count=len(state["scenes"]),
        visual_object_count=len(state["visual_objects"]),
        current_branch_depth=len([
            b for b in state["branches"].values() 
            if b["status"] == "active"
        ]),
        state=state
    )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session and start fresh."""
    orchestrator = get_orchestrator()
    
    if session_id in orchestrator.sessions:
        del orchestrator.sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    
    raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    orchestrator = get_orchestrator()
    
    sessions = []
    for session_id, state in orchestrator.sessions.items():
        sessions.append({
            "session_id": session_id,
            "topic": state.topic_root,
            "message_count": len(state.messages),
            "created_at": state.created_at.isoformat(),
            "last_activity": state.last_activity.isoformat()
        })
    
    return {"sessions": sessions, "count": len(sessions)}
