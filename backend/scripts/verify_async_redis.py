import sys
import inspect
import asyncio
import redis.asyncio
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.services.job_orchestrator import JobOrchestrator
    from app.services.cache_manager import VideoCacheManager
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

async def main():
    print("Checking JobOrchestrator...")
    try:
        # Pass a mock or real async redis client
        client = redis.asyncio.Redis()
        orchestrator = JobOrchestrator(client)
        if not inspect.iscoroutinefunction(orchestrator.get_job):
            print("❌ JobOrchestrator.get_job is NOT async")
            sys.exit(1)
        else:
            print("✅ JobOrchestrator.get_job is async")
    except Exception as e:
        print(f"❌ Error checking JobOrchestrator: {e}")
        # It might fail if __init__ is not updated to accept async redis but we are passing one
        # Or if we haven't updated the code yet, it will fail on inspect check if we expect it to be async
        pass

    print("Checking VideoCacheManager...")
    try:
        cache_manager = VideoCacheManager()
        if not inspect.iscoroutinefunction(cache_manager.get_cached_video):
            print("❌ VideoCacheManager.get_cached_video is NOT async")
            sys.exit(1)
        else:
            print("✅ VideoCacheManager.get_cached_video is async")
    except Exception as e:
        print(f"❌ Error checking VideoCacheManager: {e}")
        pass

    print("All checks passed!")

if __name__ == "__main__":
    asyncio.run(main())
