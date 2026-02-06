"""
Cache Loader - Load existing videos into Redis cache on startup

Scans output directory for existing videos and loads them into cache.
This allows pre-generated videos to be used as cache hits.
"""
import os
import json
from typing import List, Dict, Any
from pathlib import Path
from redis import asyncio as redis
from app.config import settings
from app.services.cache_manager import get_cache_manager


async def load_existing_videos_to_cache() -> Dict[str, Any]:
    """
    Scan output directory and load existing videos into Redis cache.
    Also load from Redis job entries that have completed videos.
    """
    cache_manager = get_cache_manager()
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    
    loaded_count = 0
    videos_loaded = []
    
    print("\n🚀 Loading existing videos into cache...")
    
    # Method 1: Load from Redis job entries
    try:
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor, match="job:*", count=100)
            
            for key in keys:
                job_data_str = await redis_client.get(key)
                if not job_data_str:
                    continue
                
                try:
                    job_data = json.loads(job_data_str)
                    
                    # Only cache completed videos
                    if job_data.get("status") != "completed":
                        continue
                    
                    # Extract topic from job
                    topic = job_data.get("topic", "Unknown")
                    prompt = job_data.get("prompt", "")
                    video_id = job_data.get("job_id", "")
                    video_url = job_data.get("video_url", "")
                    scenes = job_data.get("scenes", [])
                    
                    # Check if already in cache
                    if await cache_manager.is_cached(topic):
                        print(f"⏭️  Already cached: {topic}")
                        continue
                    
                    # Cache the video
                    await cache_manager.cache_video(
                        topic=topic,
                        prompt=prompt,
                        video_id=video_id,
                        video_path=video_url,
                        scenes=scenes,
                        status="completed"
                    )
                    
                    videos_loaded.append({
                        "topic": topic,
                        "video_id": video_id,
                        "scenes": len(scenes)
                    })
                    loaded_count += 1
                    
                except json.JSONDecodeError:
                    continue
            
            if cursor == 0:
                break
    
    except Exception as e:
        print(f"⚠️  Error loading from Redis jobs: {e}")
    
    # Method 2: Load from output directory
    try:
        output_dir = Path(settings.OUTPUT_DIR)
        if output_dir.exists():
            for video_file in output_dir.glob("*.mp4"):
                video_id = video_file.stem  # filename without extension
                
                # Try to find matching job in Redis
                job_key = f"job:{video_id}"
                job_data_str = await redis_client.get(job_key)
                
                if job_data_str:
                    try:
                        job_data = json.loads(job_data_str)
                        topic = job_data.get("topic", "Unknown")
                        
                        # Check if already cached
                        if await cache_manager.is_cached(topic):
                            continue
                        
                        # Cache it
                        await cache_manager.cache_video(
                            topic=topic,
                            prompt=job_data.get("prompt", ""),
                            video_id=video_id,
                            video_path=f"/videos/{video_file.name}",
                            scenes=job_data.get("scenes", []),
                            status="completed"
                        )
                        
                        videos_loaded.append({
                            "topic": topic,
                            "video_id": video_id,
                            "file": video_file.name
                        })
                        loaded_count += 1
                    except json.JSONDecodeError:
                        pass
    
    except Exception as e:
        print(f"⚠️  Error scanning output directory: {e}")
    
    # Print summary
    print(f"\n✅ Cache Loading Summary:")
    print(f"   Videos loaded: {loaded_count}")
    if videos_loaded:
        for video in videos_loaded:
            print(f"   - {video['topic']} (ID: {video['video_id']})")
    
    stats = await cache_manager.get_cache_stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Total cached videos: {stats['total_cached_videos']}")
    print(f"   Cache size: {stats['cache_size_mb']} MB")
    print(f"   Topics: {', '.join(stats['cached_topics'])}")
    
    return {
        "success": True,
        "videos_loaded": loaded_count,
        "videos": videos_loaded,
        "stats": stats
    }


async def preload_demo_videos() -> Dict[str, Any]:
    """
    Preload the 5 demo topics into cache.
    This ensures they're ready for presentation.
    """
    demo_topics = [
        "gradient descent",
        "matrix multiplication",
        "binary search algorithm",
        "performance algorithm",
        "sorting algorithm"
    ]
    
    cache_manager = get_cache_manager()
    preloaded = []
    
    print("\n🎯 Checking for demo video cache...")
    
    for topic in demo_topics:
        if await cache_manager.is_cached(topic):
            cached = await cache_manager.get_cached_video(topic)
            preloaded.append({
                "topic": topic,
                "cached": True,
                "video_id": cached.get("video_id"),
                "cached_at": cached.get("cached_at")
            })
            print(f"✅ {topic.upper()} - CACHED")
        else:
            preloaded.append({
                "topic": topic,
                "cached": False
            })
            print(f"⏳ {topic.upper()} - PENDING (will generate on demand)")
    
    return {
        "demo_topics": demo_topics,
        "preloaded": preloaded,
        "total_cached": sum(1 for p in preloaded if p.get("cached"))
    }
