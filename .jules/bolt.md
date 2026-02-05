## 2024-05-23 - Sequential LLM Calls in Scene Generation
**Learning:** The `ManimCodeGenerator` service was processing scenes sequentially, leading to linear latency growth with the number of scenes (e.g., 5 scenes * 5s = 25s).
**Action:** Parallelized scene generation using `asyncio.gather`. This reduces total generation time to the duration of the longest single LLM call (approx O(1) instead of O(N)). Important to wrap individual tasks in try/except blocks to ensure partial failures don't crash the entire batch.
