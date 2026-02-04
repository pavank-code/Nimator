from typing import Dict, Any, Optional, List
import json
import uuid
from datetime import datetime
import redis.asyncio as redis


class JobOrchestrator:
    """
    Orchestrates video generation jobs.
    Manages job lifecycle and coordinates with renderer via Redis.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.job_ttl = 3600  # 1 hour
    
    async def create_job(self, prompt: str, topic: str, scenes: List[Dict]) -> str:
        """Create a new job and return job_id."""
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "prompt": prompt,
            "topic": topic,
            "scenes": scenes,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "error_message": None,
            "video_url": None
        }
        
        # Store job in Redis
        await self.redis.set(
            f"job:{job_id}",
            json.dumps(job_data),
            ex=self.job_ttl
        )
        
        return job_id
    
    async def queue_job(self, job_id: str) -> bool:
        """Add job to the render queue."""
        job_data = await self.get_job(job_id)
        if not job_data:
            return False
        
        # Add to render queue
        await self.redis.lpush("render_queue", json.dumps(job_data))
        
        # Update status
        await self.update_job_status(job_id, "queued")
        
        return True
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data by ID."""
        data = await self.redis.get(f"job:{job_id}")
        if data:
            return json.loads(data)
        return None
    
    async def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: int = None,
        error_message: str = None,
        video_url: str = None
    ) -> bool:
        """Update job status."""
        job_data = await self.get_job(job_id)
        if not job_data:
            return False
        
        job_data["status"] = status
        job_data["updated_at"] = datetime.utcnow().isoformat()
        
        if progress is not None:
            job_data["progress"] = progress
        
        if error_message is not None:
            job_data["error_message"] = error_message
        
        if video_url is not None:
            job_data["video_url"] = video_url
        
        await self.redis.set(
            f"job:{job_id}",
            json.dumps(job_data),
            ex=self.job_ttl
        )
        
        return True
    
    async def mark_completed(self, job_id: str, video_url: str) -> bool:
        """Mark job as completed with video URL."""
        return await self.update_job_status(
            job_id,
            status="completed",
            progress=100,
            video_url=video_url
        )
    
    async def mark_failed(self, job_id: str, error_message: str) -> bool:
        """Mark job as failed with error message."""
        return await self.update_job_status(
            job_id,
            status="failed",
            error_message=error_message
        )
    
    async def get_queue_length(self) -> int:
        """Get number of jobs in render queue."""
        return await self.redis.llen("render_queue")
    
    async def get_next_job(self) -> Optional[Dict[str, Any]]:
        """Get next job from render queue (blocking pop)."""
        result = await self.redis.brpop("render_queue", timeout=5)
        if result:
            _, job_data = result
            return json.loads(job_data)
        return None


# Global instance for backward compatibility
_orchestrator = None


def get_orchestrator(redis_client: redis.Redis = None) -> JobOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None and redis_client:
        _orchestrator = JobOrchestrator(redis_client)
    return _orchestrator


async def orchestrate_job(scenes: List[Dict]) -> str:
    """Legacy function for backward compatibility."""
    if _orchestrator:
        return await _orchestrator.create_job("", "", scenes)
    return str(uuid.uuid4())
