## 2024-05-23 - TutorPage Re-render Bottleneck
**Learning:** The `TutorPage` managed the chat input state directly, causing the entire message list (and heavy children like `VideoPanel`) to re-render on every keystroke. This is a common React anti-pattern but was particularly expensive here due to the complexity of the rendered tree.
**Action:** Extracted the input logic into a self-contained `ChatInput` component. Future complex pages should isolate frequent state updates (like typing) from the main page layout.
