from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import redis.asyncio as redis
import json

from app.config import settings
from app.services.topic_classifier import TopicClassifier
from app.services.scene_planner import ScenePlanner
from app.services.scene_validator import validate_scenes
from app.services.math_validator import validate_scene as validate_math
from app.services.cache_manager import get_cache_manager
from app.api.tutor import router as tutor_router

router = APIRouter()
router.include_router(tutor_router)

# Include tutor routes
router.include_router(tutor_router)

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# Initialize services
topic_classifier = TopicClassifier()
scene_planner = ScenePlanner()


class VideoGenerationRequest(BaseModel):
    prompt: str = Field(..., max_length=1000, description="The prompt to generate a video from")
    sample_mode: bool = Field(False, description="Generate a 30-second sample instead of full video")
    duration_seconds: int = Field(180, description="Target video duration in seconds", ge=30, le=900)


class VideoGenerationResponse(BaseModel):
    job_id: str
    message: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: Optional[int] = None
    video_url: Optional[str] = None
    error_message: Optional[str] = None


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """
    Start video generation from a prompt.
    Returns a job_id to track progress.
    """
    prompt = request.prompt.strip()
    
    # Validate prompt length
    if len(prompt) > settings.MAX_PROMPT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Prompt exceeds maximum length of {settings.MAX_PROMPT_LENGTH} characters"
        )
    
    if len(prompt) < 10:
        raise HTTPException(
            status_code=400,
            detail="Prompt is too short. Please provide more details."
        )
    
    # Step 1: Topic classification (informational - always accept)
    classification = await topic_classifier.classify(prompt)
    topic = classification.get('topic', 'General')
    # Always mark as valid - we generate videos for any topic
    classification['is_valid'] = True
    
    # Determine if sample mode based on duration
    is_sample = request.sample_mode or request.duration_seconds <= 60
    
    # Step 2: Generate scene plan
    try:
        scene_plan = await scene_planner.plan(
            prompt, 
            topic,
            sample_mode=is_sample,
            duration_seconds=request.duration_seconds
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate scene plan: {str(e)}"
        )
    
    # Step 3: Validate scenes (reduced requirement for sample mode)
    validated_scenes = validate_scenes(scene_plan.get("scenes", []))
    min_scenes = 2 if is_sample else settings.MIN_SCENES_REQUIRED
    if validated_scenes is None or len(validated_scenes) < min_scenes:
        raise HTTPException(
            status_code=400,
            detail=f"Could not generate enough valid scenes. Need at least {min_scenes}."
        )
    
    # Step 4: Validate math expressions
    for scene in validated_scenes:
        if not validate_math(scene):
            raise HTTPException(
                status_code=400,
                detail="Invalid mathematical expression in generated scenes."
            )
    
    # Step 5: Create job and queue for rendering
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "prompt": prompt,
        "topic": classification["topic"],
        "scenes": validated_scenes,
        "status": "queued",
        "progress": 0
    }
    
    # Store job in Redis
    await redis_client.set(f"job:{job_id}", json.dumps(job_data))
    await redis_client.expire(f"job:{job_id}", 3600)  # 1 hour TTL
    
    # Add to render queue
    await redis_client.lpush("render_queue", json.dumps(job_data))
    
    return VideoGenerationResponse(
        job_id=job_id,
        message="Video generation started successfully",
        status="queued"
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a video generation job.
    """
    job_data = await redis_client.get(f"job:{job_id}")
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = json.loads(job_data)
    
    video_url = None
    if job["status"] == "completed":
        video_url = f"/videos/{job_id}.mp4"
    
    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0),
        video_url=video_url,
        error_message=job.get("error_message")
    )


@router.get("/video/{job_id}")
async def get_video(job_id: str):
    """
    Get video details for a completed job.
    """
    job_data = await redis_client.get(f"job:{job_id}")
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = json.loads(job_data)
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Video not ready. Current status: {job['status']}"
        )
    
    return {
        "job_id": job_id,
        "video_url": f"/videos/{job_id}.mp4",
        "topic": job.get("topic"),
        "prompt": job.get("prompt")
    }


# ============= CACHE ENDPOINTS =============

@router.get("/cache/list")
async def list_cached_videos():
    """List all cached videos ready for instant playback."""
    cache_manager = get_cache_manager()
    cached_videos = cache_manager.list_cached_videos()
    stats = cache_manager.get_cache_stats()
    
    return {
        "cached_count": len(cached_videos),
        "videos": cached_videos,
        "stats": stats
    }


@router.get("/cache/check/{topic}")
async def check_cache(topic: str):
    """Check if a video is cached for a topic."""
    cache_manager = get_cache_manager()
    cached = cache_manager.is_cached(topic)
    
    if cached:
        video_data = cache_manager.get_cached_video(topic)
        return {
            "topic": topic,
            "cached": True,
            "video": video_data
        }
    else:
        return {
            "topic": topic,
            "cached": False,
            "message": "Video not in cache - will generate on demand"
        }


@router.post("/cache/clear")
async def clear_all_cache():
    """Clear all cached videos."""
    cache_manager = get_cache_manager()
    deleted = cache_manager.clear_cache()
    
    return {
        "status": "cleared",
        "entries_deleted": deleted
    }


@router.delete("/cache/{topic}")
async def clear_topic_cache(topic: str):
    """Clear cache for a specific topic."""
    cache_manager = get_cache_manager()
    deleted = cache_manager.clear_cache(topic)
    
    if deleted > 0:
        return {
            "status": "deleted",
            "topic": topic,
            "entries_deleted": deleted
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No cache found for topic: {topic}"
        )