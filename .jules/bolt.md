## 2024-05-22 - Async Redis in FastAPI
**Learning:** Using synchronous `redis-py` client in FastAPI `async def` routes blocks the main event loop, severely degrading concurrency.
**Action:** Always use `redis.asyncio` and `await` Redis operations in async FastAPI endpoints.
