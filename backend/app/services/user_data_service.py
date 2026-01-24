"""
User data service for managing per-user data in Redis.
Handles chat history, video history, and topic studies.
"""
import json
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from app.models.user import (
    User, ChatSession, ChatMessage, 
    VideoRecord, TopicStudy, UserActivity
)


class UserDataService:
    """
    Service for managing per-user data.
    Uses Redis for storage with structured keys.
    """
    
    # Redis key prefixes
    PREFIX_USER = "user:"
    PREFIX_CHAT = "chat:"
    PREFIX_VIDEO = "video:"
    PREFIX_TOPIC = "topic:"
    PREFIX_ACTIVITY = "activity:"
    
    # TTLs (in seconds)
    USER_TTL = 86400 * 30  # 30 days
    CHAT_TTL = 86400 * 7   # 7 days
    VIDEO_TTL = 86400 * 30  # 30 days
    TOPIC_TTL = 86400 * 90  # 90 days
    ACTIVITY_TTL = 86400 * 7  # 7 days
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    # ==================== USER MANAGEMENT ====================
    
    def create_user(self, username: Optional[str] = None, email: Optional[str] = None) -> User:
        """Create a new user."""
        user = User(username=username, email=email)
        self._save_user(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        data = self.redis.get(f"{self.PREFIX_USER}{user_id}")
        if data:
            return User(**json.loads(data))
        return None
    
    def get_or_create_user(self, user_id: str) -> User:
        """Get existing user or create a new one with the given ID."""
        user = self.get_user(user_id)
        if not user:
            user = User(user_id=user_id)
            self._save_user(user)
        return user
    
    def update_user_activity(self, user_id: str) -> None:
        """Update user's last active timestamp."""
        user = self.get_user(user_id)
        if user:
            user.last_active = datetime.utcnow()
            self._save_user(user)
    
    def _save_user(self, user: User) -> None:
        """Save user to Redis."""
        self.redis.set(
            f"{self.PREFIX_USER}{user.user_id}",
            json.dumps(user.model_dump(), default=str),
            ex=self.USER_TTL
        )
        # Add to user index
        self.redis.sadd("users:all", user.user_id)
    
    # ==================== CHAT HISTORY ====================
    
    def create_chat_session(self, user_id: str, first_message: str, topic: Optional[str] = None) -> ChatSession:
        """Create a new chat session."""
        # Generate title from first message
        title = first_message[:50] + "..." if len(first_message) > 50 else first_message
        
        session = ChatSession(
            user_id=user_id,
            title=title,
            topic=topic
        )
        
        # Add user's first message
        session.messages.append(ChatMessage(
            role="user",
            content=first_message
        ))
        
        self._save_chat_session(session)
        
        # Add to user's chat list
        self.redis.lpush(f"user:{user_id}:chats", session.session_id)
        
        return session
    
    def add_message_to_session(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[ChatMessage]:
        """Add a message to an existing chat session."""
        session = self.get_chat_session(session_id)
        if not session:
            return None
        
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        
        self._save_chat_session(session)
        return message
    
    def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        data = self.redis.get(f"{self.PREFIX_CHAT}{session_id}")
        if data:
            return ChatSession(**json.loads(data))
        return None
    
    def get_user_chat_sessions(self, user_id: str, limit: int = 50) -> List[ChatSession]:
        """Get all chat sessions for a user."""
        session_ids = self.redis.lrange(f"user:{user_id}:chats", 0, limit - 1)
        sessions = []
        for sid in session_ids:
            session = self.get_chat_session(sid)
            if session:
                sessions.append(session)
        return sessions
    
    def link_video_to_session(self, session_id: str, job_id: str, video_url: Optional[str] = None) -> None:
        """Link a video job to a chat session."""
        session = self.get_chat_session(session_id)
        if session:
            session.job_id = job_id
            session.video_url = video_url
            self._save_chat_session(session)
    
    def _save_chat_session(self, session: ChatSession) -> None:
        """Save chat session to Redis."""
        self.redis.set(
            f"{self.PREFIX_CHAT}{session.session_id}",
            json.dumps(session.model_dump(), default=str),
            ex=self.CHAT_TTL
        )
    
    # ==================== VIDEO HISTORY ====================
    
    def create_video_record(
        self, 
        user_id: str, 
        job_id: str, 
        prompt: str, 
        topic: str,
        duration_seconds: int = 0,
        scene_count: int = 0
    ) -> VideoRecord:
        """Create a new video record."""
        record = VideoRecord(
            user_id=user_id,
            job_id=job_id,
            prompt=prompt,
            topic=topic,
            duration_seconds=duration_seconds,
            scene_count=scene_count
        )
        
        self._save_video_record(record)
        
        # Add to user's video list
        self.redis.lpush(f"user:{user_id}:videos", record.video_id)
        
        # Update topic study
        self._update_topic_study(user_id, topic, prompt, record.video_id)
        
        # Log activity
        self.log_activity(user_id, "video_generated", f"Generated video about: {topic}", {
            "job_id": job_id,
            "prompt": prompt
        })
        
        return record
    
    def update_video_status(
        self, 
        video_id: str, 
        status: str, 
        video_url: Optional[str] = None
    ) -> Optional[VideoRecord]:
        """Update video record status."""
        record = self.get_video_record(video_id)
        if not record:
            return None
        
        record.status = status
        if video_url:
            record.video_url = video_url
        if status == "completed":
            record.completed_at = datetime.utcnow()
        
        self._save_video_record(record)
        return record
    
    def get_video_record(self, video_id: str) -> Optional[VideoRecord]:
        """Get video record by ID."""
        data = self.redis.get(f"{self.PREFIX_VIDEO}{video_id}")
        if data:
            return VideoRecord(**json.loads(data))
        return None
    
    def get_video_by_job_id(self, job_id: str) -> Optional[VideoRecord]:
        """Get video record by job ID."""
        # Search in index
        video_id = self.redis.get(f"job_video:{job_id}")
        if video_id:
            return self.get_video_record(video_id)
        return None
    
    def get_user_videos(self, user_id: str, limit: int = 50) -> List[VideoRecord]:
        """Get all video records for a user."""
        video_ids = self.redis.lrange(f"user:{user_id}:videos", 0, limit - 1)
        records = []
        for vid in video_ids:
            record = self.get_video_record(vid)
            if record:
                records.append(record)
        return records
    
    def _save_video_record(self, record: VideoRecord) -> None:
        """Save video record to Redis."""
        self.redis.set(
            f"{self.PREFIX_VIDEO}{record.video_id}",
            json.dumps(record.model_dump(), default=str),
            ex=self.VIDEO_TTL
        )
        # Create job -> video index
        self.redis.set(f"job_video:{record.job_id}", record.video_id, ex=self.VIDEO_TTL)
    
    # ==================== TOPIC STUDIES ====================
    
    def _update_topic_study(self, user_id: str, topic_name: str, prompt: str, video_id: str) -> TopicStudy:
        """Update or create topic study entry."""
        # Try to get existing topic study
        topic_key = f"user:{user_id}:topic:{topic_name.lower().replace(' ', '_')}"
        data = self.redis.get(topic_key)
        
        if data:
            study = TopicStudy(**json.loads(data))
        else:
            study = TopicStudy(
                user_id=user_id,
                topic_name=topic_name,
                category=self._get_topic_category(topic_name)
            )
            # Add to user's topics list
            self.redis.sadd(f"user:{user_id}:topics", topic_name)
        
        # Update study
        study.video_count += 1
        study.last_studied = datetime.utcnow()
        if prompt not in study.prompts_asked:
            study.prompts_asked.append(prompt)
        if video_id not in study.videos_generated:
            study.videos_generated.append(video_id)
        
        # Save updated study
        self.redis.set(
            topic_key,
            json.dumps(study.model_dump(), default=str),
            ex=self.TOPIC_TTL
        )
        
        return study
    
    def get_user_topic_studies(self, user_id: str) -> List[TopicStudy]:
        """Get all topic studies for a user."""
        topic_names = self.redis.smembers(f"user:{user_id}:topics")
        studies = []
        
        for topic_name in topic_names:
            topic_key = f"user:{user_id}:topic:{topic_name.lower().replace(' ', '_')}"
            data = self.redis.get(topic_key)
            if data:
                studies.append(TopicStudy(**json.loads(data)))
        
        # Sort by last studied
        studies.sort(key=lambda x: x.last_studied, reverse=True)
        return studies
    
    def get_topic_study(self, user_id: str, topic_name: str) -> Optional[TopicStudy]:
        """Get specific topic study."""
        topic_key = f"user:{user_id}:topic:{topic_name.lower().replace(' ', '_')}"
        data = self.redis.get(topic_key)
        if data:
            return TopicStudy(**json.loads(data))
        return None
    
    def _get_topic_category(self, topic_name: str) -> str:
        """Determine category from topic name."""
        topic_lower = topic_name.lower()
        
        if any(kw in topic_lower for kw in ['math', 'calculus', 'algebra', 'geometry', 'matrix']):
            return "Mathematics"
        elif any(kw in topic_lower for kw in ['ml', 'machine learning', 'neural', 'deep learning', 'ai']):
            return "Machine Learning"
        elif any(kw in topic_lower for kw in ['algorithm', 'sort', 'search', 'tree', 'graph']):
            return "Algorithms"
        elif any(kw in topic_lower for kw in ['physics', 'quantum', 'mechanics', 'relativity']):
            return "Physics"
        else:
            return "General"
    
    # ==================== ACTIVITY TRACKING ====================
    
    def log_activity(
        self, 
        user_id: str, 
        activity_type: str, 
        description: str,
        metadata: Dict[str, Any] = None
    ) -> UserActivity:
        """Log a user activity."""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            metadata=metadata or {}
        )
        
        # Save activity
        self.redis.lpush(
            f"user:{user_id}:activities",
            json.dumps(activity.model_dump(), default=str)
        )
        # Trim to last 100 activities
        self.redis.ltrim(f"user:{user_id}:activities", 0, 99)
        
        return activity
    
    def get_user_activities(self, user_id: str, limit: int = 20) -> List[UserActivity]:
        """Get recent activities for a user."""
        activities_data = self.redis.lrange(f"user:{user_id}:activities", 0, limit - 1)
        return [UserActivity(**json.loads(data)) for data in activities_data]
    
    # ==================== USER DASHBOARD DATA ====================
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard data for a user."""
        user = self.get_user(user_id)
        if not user:
            return {}
        
        videos = self.get_user_videos(user_id, limit=10)
        topics = self.get_user_topic_studies(user_id)
        activities = self.get_user_activities(user_id, limit=10)
        chat_sessions = self.get_user_chat_sessions(user_id, limit=10)
        
        # Calculate stats
        total_videos = len(self.redis.lrange(f"user:{user_id}:videos", 0, -1))
        total_topics = len(topics)
        completed_videos = sum(1 for v in videos if v.status == "completed")
        
        return {
            "user": user.model_dump(),
            "stats": {
                "total_videos": total_videos,
                "completed_videos": completed_videos,
                "topics_studied": total_topics,
                "recent_activity_count": len(activities)
            },
            "recent_videos": [v.model_dump() for v in videos[:5]],
            "topics": [t.model_dump() for t in topics[:5]],
            "recent_activities": [a.model_dump() for a in activities[:5]],
            "recent_chats": [
                {
                    "session_id": c.session_id,
                    "title": c.title,
                    "topic": c.topic,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                    "message_count": len(c.messages)
                }
                for c in chat_sessions[:5]
            ]
        }


# Global instance
_user_data_service: Optional[UserDataService] = None


def get_user_data_service(redis_client: redis.Redis = None) -> UserDataService:
    """Get or create the global user data service instance."""
    global _user_data_service
    if _user_data_service is None and redis_client:
        _user_data_service = UserDataService(redis_client)
    return _user_data_service
