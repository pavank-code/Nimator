from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobSchema(BaseModel):
    """Schema for a video generation job."""
    job_id: str
    prompt: str = Field(..., max_length=300)
    topic: str
    scenes: List[Dict[str, Any]]
    status: JobStatus = JobStatus.QUEUED
    progress: int = Field(default=0, ge=0, le=100)
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "prompt": "Explain gradient descent visually",
                "topic": "Machine Learning",
                "scenes": [
                    {
                        "scene_type": "text_labels",
                        "title": "Introduction",
                        "text": "Gradient Descent",
                        "narration": "Let's explore gradient descent."
                    }
                ],
                "status": "completed",
                "progress": 100,
                "video_url": "/videos/550e8400-e29b-41d4-a716-446655440000.mp4",
                "error_message": None
            }
        }


class JobCreateRequest(BaseModel):
    """Request schema for creating a new job."""
    prompt: str = Field(..., min_length=10, max_length=300)


class JobCreateResponse(BaseModel):
    """Response schema for job creation."""
    job_id: str
    message: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    """Response schema for job status check."""
    job_id: str
    status: JobStatus
    progress: int
    video_url: Optional[str] = None
    error_message: Optional[str] = None