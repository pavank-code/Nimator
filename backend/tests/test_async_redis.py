import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from pydantic import BaseModel, Field

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

class MockRequest(BaseModel):
    prompt: str = "test prompt"
    sample_mode: bool = False
    duration_seconds: int = 180

class MockBackgroundTasks:
    def add_task(self, func, *args, **kwargs):
        pass

async def verify_structure():
    print("Setting up mocks...")

    # Create the mock instance
    mock_redis_instance = MagicMock()

    # Configure async methods
    mock_redis_instance.setex = AsyncMock(return_value=True)
    mock_redis_instance.sadd = AsyncMock(return_value=1)
    mock_redis_instance.get = AsyncMock(return_value=None)
    mock_redis_instance.delete = AsyncMock(return_value=1)
    mock_redis_instance.smembers = AsyncMock(return_value=[])
    mock_redis_instance.srem = AsyncMock(return_value=1)
    mock_redis_instance.expire = AsyncMock(return_value=True)
    mock_redis_instance.lpush = AsyncMock(return_value=1)
    mock_redis_instance.set = AsyncMock(return_value=True)

    # Also mock TopicClassifier and ScenePlanner to avoid real LLM calls/errors
    with patch('redis.asyncio.Redis', return_value=mock_redis_instance), \
         patch('app.services.topic_classifier.TopicClassifier') as MockClassifier, \
         patch('app.services.scene_planner.ScenePlanner') as MockPlanner, \
         patch('app.services.scene_validator.validate_scenes') as mock_validate_scenes, \
         patch('app.services.math_validator.validate_scene') as mock_validate_math:

        # Configure mocks
        mock_classifier_instance = MockClassifier.return_value
        mock_classifier_instance.classify = AsyncMock(return_value={"topic": "Math", "is_valid": True})

        mock_planner_instance = MockPlanner.return_value
        mock_planner_instance.plan = AsyncMock(return_value={"scenes": [{"scene_type": "graph_2d", "narration": "test"}]})

        # Explicitly set side effect to print when called
        def validate_scenes_side_effect(scenes):
            print(f"DEBUG: validate_scenes called with {len(scenes)} scenes")
            return [{"scene_type": "graph_2d", "narration": "test"}] * 15

        mock_validate_scenes.side_effect = validate_scenes_side_effect
        mock_validate_math.return_value = True

        print("Importing modules...")
        # Clear modules to force re-import with patched dependencies
        if 'app.services.cache_manager' in sys.modules: del sys.modules['app.services.cache_manager']
        if 'app.api.routes' in sys.modules: del sys.modules['app.api.routes']

        from app.services.cache_manager import VideoCacheManager
        from app.api.routes import generate_video, redis_client as routes_redis_client

        # Verify VideoCacheManager
        print("\n--- Verifying VideoCacheManager ---")
        manager = VideoCacheManager()
        await manager.cache_video("test", "test", "123", "path", [])
        mock_redis_instance.setex.assert_awaited()
        print("VideoCacheManager passed.")

        # Verify routes.generate_video
        print("\n--- Verifying routes.generate_video ---")

        req = MockRequest(prompt="Explain calculus longer prompt", duration_seconds=180)
        bg = MockBackgroundTasks()

        try:
            await generate_video(req, bg)
        except Exception as e:
            print(f"generate_video failed: {e}")
            raise

        # Verify await happened on redis calls in generate_video
        mock_redis_instance.set.assert_awaited()
        mock_redis_instance.expire.assert_awaited()
        mock_redis_instance.lpush.assert_awaited()
        print("routes.generate_video passed.")

        print("\nVerification successful!")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(verify_structure())
    finally:
        loop.close()
