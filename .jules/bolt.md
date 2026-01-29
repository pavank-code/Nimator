## 2024-05-22 - Redis N+1 Query Antipattern
**Learning:** Found N+1 query pattern where `smembers` returns keys and a loop calls `get` for each. This causes high network overhead.
**Action:** Use `mget` to batch fetch values when keys are known or returned from a collection scan.
