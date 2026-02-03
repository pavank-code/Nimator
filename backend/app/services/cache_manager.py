"""
Redis Cache Manager for Pre-generated Videos

Manages caching of video outputs for instant demo playback.
Pre-caches existing videos and manages cache operations.
"""
from typing import Dict, Any, Optional, List
import json
import redis.asyncio as redis
from datetime import datetime, timedelta
from app.config import settings


class VideoCacheManager:
    """
    Manages video caching in Redis.
    
    Cache structure:
    - video:topic:{topic_hash} → full video data
    - video:list → list of all cached videos
    """
    
    CACHE_TTL_SECONDS = 86400 * 30  # 30 days
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
    
    async def cache_video(
        self,
        topic: str,
        prompt: str,
        video_id: str,
        video_path: str,
        scenes: List[Dict[str, Any]],
        status: str = "completed"
    ) -> bool:
        """
        Cache a video with metadata.
        
        Args:
            topic: Topic/category of the video
            prompt: Original user prompt
            video_id: Unique video ID
            video_path: Path to video file
            scenes: List of scenes in the video
            status: Job status (completed, processing, etc)
        """
        cache_key = f"video:topic:{topic.lower().replace(' ', '_')}"
        
        cache_data = {
            "video_id": video_id,
            "topic": topic,
            "prompt": prompt,
            "video_path": video_path,
            "scenes_count": len(scenes),
            "cached_at": datetime.utcnow().isoformat(),
            "status": status,
            "scene_types": list(set(s.get("scene_type", "unknown") for s in scenes))
        }
        
        # Store the cache entry
        await self.redis_client.setex(
            cache_key,
            self.CACHE_TTL_SECONDS,
            json.dumps(cache_data)
        )
        
        # Add to video list
        video_list_key = "video:list"
        await self.redis_client.sadd(video_list_key, cache_key)
        
        print(f"✅ Cached video: {topic} (ID: {video_id})")
        return True
    
    async def get_cached_video(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached video for a topic.
        
        Returns None if not cached.
        """
        cache_key = f"video:topic:{topic.lower().replace(' ', '_')}"
        cached_data = await self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def list_cached_videos(self) -> List[Dict[str, Any]]:
        """List all cached videos."""
        video_list_key = "video:list"
        cache_keys = await self.redis_client.smembers(video_list_key)
        
        videos = []
        for key in cache_keys:
            data = await self.redis_client.get(key)
            if data:
                videos.append(json.loads(data))
        
        return videos
    
    async def clear_cache(self, topic: Optional[str] = None) -> int:
        """
        Clear cache for a specific topic or all cache.
        
        Returns: Number of entries deleted
        """
        if topic:
            cache_key = f"video:topic:{topic.lower().replace(' ', '_')}"
            deleted = await self.redis_client.delete(cache_key)
            await self.redis_client.srem("video:list", cache_key)
            return deleted
        else:
            # Clear all
            video_list_key = "video:list"
            cache_keys = await self.redis_client.smembers(video_list_key)
            deleted = 0
            for key in cache_keys:
                deleted += await self.redis_client.delete(key)
            await self.redis_client.delete(video_list_key)
            return deleted
    
    async def is_cached(self, topic: str) -> bool:
        """Check if a video is cached."""
        return await self.get_cached_video(topic) is not None
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        video_list_key = "video:list"
        cache_keys = await self.redis_client.smembers(video_list_key)
        
        stats = {
            "total_cached_videos": len(cache_keys),
            "cached_topics": [],
            "cache_size_approx": 0
        }
        
        for key in cache_keys:
            data = await self.redis_client.get(key)
            if data:
                cache_entry = json.loads(data)
                stats["cached_topics"].append(cache_entry["topic"])
                stats["cache_size_approx"] += len(data)
        
        stats["cache_size_mb"] = round(stats["cache_size_approx"] / 1024 / 1024, 2)
        
        return stats


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> VideoCacheManager:
    """Get or create the global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = VideoCacheManager()
    return _cache_manager
