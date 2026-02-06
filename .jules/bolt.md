## 2024-05-22 - Synchronous Redis in Async Context
**Learning:** Using synchronous `redis.Redis` in `async def` endpoints blocks the entire event loop, negating concurrency benefits of FastAPI. This was found in `routes.py`, `cache_manager.py` and `tutor_orchestrated.py`.
**Action:** Use `redis.asyncio` (aliased as `redis`) and `await` all Redis operations in async functions.
