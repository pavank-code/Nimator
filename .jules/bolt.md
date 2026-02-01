## 2024-05-23 - Parallelizing LLM Calls
**Learning:** Sequential LLM calls in a loop are a major performance bottleneck for multi-step generation tasks. Converting them to `asyncio.gather` provided a 5x speedup (from 5s to 1s for 5 scenes).
**Action:** Always look for opportunities to parallelize independent IO-bound operations like LLM API calls, but ensure error handling and state updates (like counters) are managed correctly in the gathering phase.
