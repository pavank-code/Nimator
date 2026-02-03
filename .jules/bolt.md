## 2026-02-03 - Synchronous Redis in Async FastAPI
**Learning:** Using synchronous `redis-py` client in async FastAPI routes blocks the event loop, severely degrading concurrency.
**Action:** Use `redis.asyncio` and `await` all Redis operations in async paths.
