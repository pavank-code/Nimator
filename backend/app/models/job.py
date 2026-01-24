from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """Model for a video generation job."""
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

    def is_complete(self) -> bool:
        return self.status == JobStatus.COMPLETED

    def is_failed(self) -> bool:
        return self.status == JobStatus.FAILED