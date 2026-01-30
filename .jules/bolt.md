## 2026-01-30 - Chat Re-renders on Input
**Learning:** The `TutorPage` manages both the chat history state and the input value state. Every keystroke updates `inputValue`, causing the entire page to re-render. Since `ChatMessage` components were not memoized, the entire chat history (potentially long) re-renders on every character typed.
**Action:** Memoized `ChatMessage`. In future, consider splitting `ChatInput` into a separate component or moving state down to isolate re-renders.
