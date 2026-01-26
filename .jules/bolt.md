## 2025-05-22 - [Request Caching]
**Learning:** The application uses LLM-based topic classification for every request, which is expensive. Existing caching was only topic-based and didn't deduplicate identical prompts efficiently.
**Action:** Implemented request-level caching using prompt hash to skip LLM calls for identical requests.
