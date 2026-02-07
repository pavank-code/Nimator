## 2024-05-23 - Parallelizing Manim Scene Generation
**Learning:** Found a critical syntax error in `backend/app/services/manim_code_generator.py` where `SCENE_GENERATION_PROMPT` was unindented, causing `IndentationError` on `__init__`. Also discovered that scene generation was sequential, causing N+1 LLM latency.
**Action:** Always verify syntax of critical files even if they seem to be "working" (or untouched). When optimizing, first ensure the code is valid. Parallelization with `asyncio.gather` provided a 10x speedup in simulations.
