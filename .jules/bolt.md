## 2024-05-23 - Synchronous Redis Blocking FastAPI
**Learning:** Using sync `redis.Redis` client in FastAPI `async def` route handlers blocks the entire event loop, severely limiting concurrency.
**Action:** Always use `redis.asyncio` and `await` calls in async services and routes. Verified with `inspect.iscoroutinefunction` check.
