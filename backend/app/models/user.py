"""
User model for per-user data management.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    """Model for a user."""
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: Optional[str] = None
    email: Optional[str] = None
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    
    # User preferences
    preferred_duration: int = 180  # Default video duration
    preferred_topics: List[str] = Field(default_factory=list)


class ChatMessage(BaseModel):
    """Model for a single chat message."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatSession(BaseModel):
    """Model for a chat session (conversation)."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: Optional[str] = None  # Auto-generated from first message
    messages: List[ChatMessage] = Field(default_factory=list)
    topic: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Associated video job (if any)
    job_id: Optional[str] = None
    video_url: Optional[str] = None


class VideoRecord(BaseModel):
    """Model for a video record in user's history."""
    video_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    job_id: str
    prompt: str
    topic: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: int = 0
    status: str = "pending"  # pending, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Scene information
    scene_count: int = 0
    scenes_summary: List[str] = Field(default_factory=list)


class TopicStudy(BaseModel):
    """Model for tracking topic studies."""
    topic_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    topic_name: str
    category: str  # Mathematics, ML, Physics, etc.
    subtopics: List[str] = Field(default_factory=list)
    video_count: int = 0
    total_study_time: int = 0  # in seconds
    last_studied: datetime = Field(default_factory=datetime.utcnow)
    first_studied: datetime = Field(default_factory=datetime.utcnow)
    
    # Progress tracking
    prompts_asked: List[str] = Field(default_factory=list)
    videos_generated: List[str] = Field(default_factory=list)  # video_ids


class UserActivity(BaseModel):
    """Model for tracking user activity."""
    activity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: str  # "prompt", "video_generated", "video_watched", "topic_explored"
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
