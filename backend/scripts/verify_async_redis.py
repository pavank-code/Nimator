import sys
import os
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock, patch

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock dependencies
sys.modules["fastapi"] = MagicMock()
sys.modules["uvicorn"] = MagicMock()
sys.modules["httpx"] = MagicMock()
sys.modules["manim"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["sympy"] = MagicMock()

# Mock redis.asyncio BEFORE importing app modules
mock_redis = MagicMock()
mock_async_redis = MagicMock()
mock_redis_client = AsyncMock()
mock_async_redis.Redis.return_value = mock_redis_client

# Patch sys.modules
with patch.dict(sys.modules, {'redis': mock_redis, 'redis.asyncio': mock_async_redis}):

    # Also mock app.config
    mock_config = MagicMock()
    mock_config.settings.REDIS_HOST = "localhost"
    mock_config.settings.REDIS_PORT = 6379
    sys.modules["app.config"] = mock_config

    # Now import the class
    from app.services.cache_manager import VideoCacheManager

    async def main():
        print("Testing VideoCacheManager async compatibility...")

        manager = VideoCacheManager()

        # Explicitly ensure methods are AsyncMock
        manager.redis_client.setex = AsyncMock()
        manager.redis_client.sadd = AsyncMock()
        manager.redis_client.get = AsyncMock()
        manager.redis_client.smembers = AsyncMock()
        manager.redis_client.delete = AsyncMock()
        manager.redis_client.srem = AsyncMock()

        # Test cache_video
        print("Testing cache_video...")
        await manager.cache_video("topic", "prompt", "vid1", "path", [])

        # Verify setex was awaited and called
        manager.redis_client.setex.assert_awaited()
        print("✅ cache_video awaited redis.setex")

        manager.redis_client.sadd.assert_awaited()
        print("✅ cache_video awaited redis.sadd")

        # Test get_cached_video
        print("\nTesting get_cached_video...")
        manager.redis_client.get.return_value = json.dumps({"video_id": "vid1", "topic": "topic"})
        result = await manager.get_cached_video("topic")

        manager.redis_client.get.assert_awaited()
        print("✅ get_cached_video awaited redis.get")
        if result and result["video_id"] == "vid1":
            print("✅ result parsed correctly")
        else:
            print("❌ result mismatch")

        # Test list_cached_videos
        print("\nTesting list_cached_videos...")
        manager.redis_client.smembers.return_value = {"key1"}
        manager.redis_client.get.return_value = json.dumps({"video_id": "vid1", "topic": "topic"})

        videos = await manager.list_cached_videos()
        manager.redis_client.smembers.assert_awaited()
        print("✅ list_cached_videos awaited redis.smembers")

        # Test clear_cache (all)
        print("\nTesting clear_cache (all)...")
        manager.redis_client.delete.return_value = 1
        manager.redis_client.smembers.return_value = {"key1", "key2"}

        await manager.clear_cache()
        manager.redis_client.smembers.assert_awaited()
        # Should delete keys + list
        assert manager.redis_client.delete.call_count >= 1
        print("✅ clear_cache awaited redis.delete")

        print("\nSUCCESS: VideoCacheManager is using async redis correctly!")

    if __name__ == "__main__":
        asyncio.run(main())
