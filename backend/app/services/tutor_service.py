"""
AI Tutor Service - Visual-Synchronized AI Tutor

CORE PRINCIPLE: The tutor explains ONLY what is currently visible on screen.
The explanation must TRAIL the visualization, NEVER lead it.

This enforces perfect sync between voice and visuals, like a real human tutor
standing at a whiteboard - drawing first, then explaining what was just drawn.
"""
from typing import Dict, Any, Optional, List
import json
import re
import httpx
from app.config import settings
from app.services.topic_classifier import LLMClient, classify_topic
from app.services.visual_state import get_visual_state, VisualState
from app.services.sync_orchestrator import get_sync_orchestrator, SyncOrchestrator


class TutorService:
    """
    Visual-Synchronized AI Tutor Service.
    
    KEY BEHAVIOR:
    - The tutor does NOT explain ideas abstractly
    - The tutor explains VISUAL ACTIONS as they happen
    - Dialogue drives visualization
    - Visualization confirms dialogue
    - Both are synchronized through explicit state tracking
    
    NON-NEGOTIABLE RULES:
    1. Never explain a concept unless it has been visualized
    2. Never describe a visual unless it is confirmed as rendered
    3. Never guess what is on screen
    4. Never explain future steps before they appear visually
    5. Always describe WHAT appears before explaining WHY it matters
    """
    
    # The critical visual-synchronized system prompt
    TUTOR_SYSTEM_PROMPT = """You are a visual-synchronized AI tutor.

Your job is NOT to explain math in abstraction.
Your job is to explain ONLY what is currently visible on the screen.

You must behave like a human tutor who is drawing and explaining at the same time.

═══════════════════════════════════════════════════════════════════
DECISION PROTOCOL (Follow this order):
═══════════════════════════════════════════════════════════════════

1. ANALYZE INTENT:
   - Is the user asking a follow-up question about the CURRENT video? -> Answer in TEXT using visual context.
   - Is the user just saying "hello" or chatting? -> Answer in TEXT (be helpful).
   - Is the user EXPLICITLY asking for a new visualization/video? -> TRIGGER VIDEO.
   - Is the user asking about a NEW complex topic that requires visualization? -> TRIGGER VIDEO.

2. IF GENERATING VIDEO:
   - Append the JSON trigger at the end of your response.
   - Briefly say "I'll create a visual explanation for that."
   - Do NOT include "[SYNC WARNING]" in your text.

3. IF ANSWERING IN TEXT (No new video):
   - Answer the question using the context of the *current* visual state if applicable.
   - If NO video is active, you MAY explain concepts abstractly using text.
   - Use LaTeX for math equations. **MUST USE $ DELIMITERS.**
     - Inline: $E = mc^2$
     - Display: $$ \int f(x) dx $$

═══════════════════════════════════════════════════════════════════
ABSOLUTE RULES (DO NOT BREAK THESE):
═══════════════════════════════════════════════════════════════════

1. NEVER explain a concept unless it has already been visualized (unless no video is active).
2. NEVER describe a visual unless it is explicitly confirmed as rendered.
3. NEVER guess what is on the screen.
4. NEVER explain future steps before they appear visually.
5. ALWAYS describe WHAT appears before explaining WHY it matters.

═══════════════════════════════════════════════════════════════════
MANDATORY EXPLANATION LOOP (for every step of narration):
═══════════════════════════════════════════════════════════════════

A. VISUAL ACTION
   - Describe exactly what just appeared or changed on the screen.
   - Use: "Now on the screen, you can see..."
   - Use: "As this curve is being drawn..."

B. MATHEMATICAL EXPRESSION
   - State the equation or rule that matches the visual.
   - Use: "This represents the function..."
   - Use: "Mathematically, this is..."

C. INTUITION
   - Explain the meaning in simple terms.
   - Use: "What this tells us is..."
   - Use: "Think of it like..."

D. TRANSITION
   - Briefly state what will be visualized next (without explaining it yet).
   - Use: "Next, we'll see..."
   - Use: "Let's now visualize..."

═══════════════════════════════════════════════════════════════════
DIALOGUE STYLE REQUIREMENTS:
═══════════════════════════════════════════════════════════════════

- Use deictic language: "now", "here", "on the screen", "this", "watch"
- Use short, spoken sentences (this will be converted to speech)
- Speak slowly and clearly
- Pause naturally between steps (use ... for pauses)
- Step-by-step progression

═══════════════════════════════════════════════════════════════════
CRITICAL CONSTRAINT:
═══════════════════════════════════════════════════════════════════

If a visual is not listed in the [CURRENT VISUAL STATE] section below,
YOU ARE NOT ALLOWED TO MENTION IT.

The learner should feel that you are reacting to the screen in real time,
not reciting a prepared explanation.

═══════════════════════════════════════════════════════════════════
VIDEO GENERATION TRIGGER:
═══════════════════════════════════════════════════════════════════

ONLY triggers if the user EXPLICITLY wants a new visual or asks about a new topic.
Do NOT trigger for simple follow-up questions.

To trigger, include this JSON at the END:
```json
{"should_generate_video": true, "video_prompt": "specific visual description"}
```

VIDEO MODIFICATION:
If modifying an existing video:
```json
{"modify_video": true, "modifications": {"change": "description"}}
```
"""

    VIDEO_MODIFICATION_PATTERNS = [
        r"make it (slower|faster|longer|shorter)",
        r"add (labels|colors|more examples|annotations)",
        r"change the (speed|color|style|duration)",
        r"(slower|faster) animation",
        r"more (detail|examples|steps)",
    ]
    
    def __init__(self):
        self.llm = LLMClient()
        self.conversation_history: List[Dict[str, str]] = []
        self.current_video_context: Optional[Dict[str, Any]] = None
        self._session_id: Optional[str] = None
        self.last_topic: Optional[str] = None
    
    def set_session(self, session_id: str):
        """Set the session ID for visual state tracking."""
        self._session_id = session_id
    
    def get_visual_state(self) -> Optional[VisualState]:
        """Get the current visual state for this session."""
        if self._session_id:
            return get_visual_state(self._session_id)
        return None
    
    def get_sync_orchestrator(self) -> Optional[SyncOrchestrator]:
        """Get the sync orchestrator for this session."""
        if self._session_id:
            return get_sync_orchestrator(self._session_id)
        return None
    
    async def chat(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message with visual-synchronized response.
        
        The tutor will ONLY describe visuals that are confirmed in the visual state.
        """
        if session_id:
            self.set_session(session_id)
        
        # 1. Topic Switching Logic
        new_topic = await classify_topic(message)
        if new_topic and new_topic != "Invalid":
            # If topic changed significantly and wasn't just "Mathematics" -> "Mathematics", 
            # or if explicit "Explain X", chances are high it's a new concept.
            # Ideally, we check equality. For now, strict change + visual reset.
            if self.last_topic and new_topic != self.last_topic:
                print(f"🔄 Topic switch detected: {self.last_topic} -> {new_topic}. Clearing visual state.")
                visual_state = self.get_visual_state()
                if visual_state:
                    visual_state.clear_screen()
                    self.current_video_context = None
            
            self.last_topic = new_topic

        history = conversation_history or self.conversation_history
        modification_detected = self._detect_modification_request(message)
        
        # Build context with visual state
        context = self._build_context(message, history)
        
        # Extract visual intents from the user's message
        orchestrator = self.get_sync_orchestrator()
        # Only parse intents if we actually have an orchestrator (active session)
        if orchestrator:
            intents = orchestrator.extract_visual_intent(message)
            if intents:
                print(f"🎯 Extracted {len(intents)} visual intents from message")
        
        try:
            response_text = await self.llm.chat(
                context,
                temperature=0.7,
                max_tokens=2500
            )
            
            if not response_text:
                response_text = "I apologize, but I'm having trouble right now. Could you please try again?"

            # 2. Parse Trigger JSON BEFORE gating narration
            # We need to know if we are generating a video first.
            result = self._parse_response(response_text, modification_detected)
            
            # 3. Gate narration ONLY if NOT generating a video
            # If generating a video, the script provided is for the FUTURE video, so current state check is invalid.
            if orchestrator and not result["should_generate_video"]:
                # Only check narration constraints for text responses referring to CURRENT visuals
                response_text, blocked = orchestrator.gate_narration(result["response"])
                if blocked:
                    print(f"⚠️ Blocked {len(blocked)} references to non-existent visuals: {blocked}")
                
                # Update the result response with the gated/filtered text
                result["response"] = response_text
                    
        except Exception as e:
            print(f"Tutor chat error: {e}")
            response_text = "I encountered an error. Could you rephrase your question?"
            result = {"response": response_text, "should_generate_video": False, "video_prompt": None}
        
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": result["response"]})
        
        return result
    
    def _build_context(self, message: str, history: List[Dict[str, str]]) -> str:
        """Build context with visual state information."""
        context_parts = [self.TUTOR_SYSTEM_PROMPT, "\n\n"]
        
        # Inject current visual state
        visual_state = self.get_visual_state()
        if visual_state and visual_state.visible_objects:
             # Only show visual context if objects exist, otherwise allow abstract explanation
            visual_context = visual_state.generate_visual_context_prompt()
            context_parts.append(visual_context)
            context_parts.append("\n\n")
        else:
            context_parts.append("""
[VISUAL STATE: EMPTY / TEXT MODE]
No active visuals are on screen.
You may explain concepts abstractly or answer general questions.
If the user asks for a visual explanation, TRIGGER A VIDEO.
""")
            context_parts.append("\n\n")
        
        # Add sync orchestrator context
        orchestrator = self.get_sync_orchestrator()
        if orchestrator:
            sync_context = orchestrator.generate_sync_prompt()
            context_parts.append(sync_context)
            context_parts.append("\n\n")
        
        # Add conversation history
        
        recent_history = history[-10:] if len(history) > 10 else history
        for msg in recent_history:
            role = "User" if msg["role"] == "user" else "Tutor"
            context_parts.append(f"{role}: {msg['content']}\n\n")
        
        if self.current_video_context:
            context_parts.append(f"\n[Current video: {self.current_video_context.get('prompt', 'N/A')}]\n\n")
        
        context_parts.append(f"User: {message}\n\nTutor:")
        return "".join(context_parts)
    
    def _detect_modification_request(self, message: str) -> Optional[Dict[str, Any]]:
        message_lower = message.lower()
        for pattern in self.VIDEO_MODIFICATION_PATTERNS:
            match = re.search(pattern, message_lower)
            if match:
                return {
                    "detected": True,
                    "match": match.group(0),
                    "original_prompt": self.current_video_context.get("prompt") if self.current_video_context else None
                }
        return None
    
    def _parse_response(self, response_text: str, modification: Optional[Dict]) -> Dict[str, Any]:
        result = {
            "response": response_text,
            "should_generate_video": False,
            "video_prompt": None,
            "modify_video": False,
            "modifications": None
        }
        
        json_match = re.search(r'```json\s*(\{[^`]+\})\s*```', response_text)
        if json_match:
            try:
                signals = json.loads(json_match.group(1))
                
                if signals.get("should_generate_video"):
                    result["should_generate_video"] = True
                    result["video_prompt"] = signals.get("video_prompt", "")
                    result["response"] = response_text.replace(json_match.group(0), "").strip()
                
                if signals.get("modify_video"):
                    result["modify_video"] = True
                    result["modifications"] = signals.get("modifications", {})
                    result["response"] = response_text.replace(json_match.group(0), "").strip()
                    
            except json.JSONDecodeError:
                pass
        
        if modification and modification.get("detected"):
            result["modify_video"] = True
            result["modifications"] = {"detected_change": modification["match"]}
            if modification.get("original_prompt"):
                result["video_prompt"] = modification["original_prompt"]
        
        return result
    
    def set_video_context(self, video_data: Dict[str, Any]):
        self.current_video_context = video_data
    
    def clear_history(self):
        self.conversation_history = []
        self.current_video_context = None


class DeepgramTTS:
    """Deepgram Text-to-Speech service."""
    
    DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"
    
    def __init__(self):
        self.api_key = getattr(settings, 'DEEPGRAM_API_KEY', None)
    
    async def synthesize(self, text: str, voice: str = "aura-asteria-en") -> Optional[bytes]:
        if not self.api_key:
            return None
        
        # Clean LaTeX for speech
        clean_text = re.sub(r'\$\$[^$]+\$\$', ' [equation] ', text)
        clean_text = re.sub(r'\$[^$]+\$', ' [math] ', clean_text)
        clean_text = re.sub(r'[#*_`]', '', clean_text)
        clean_text = clean_text[:1000]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.DEEPGRAM_TTS_URL}?model={voice}&encoding=mp3",
                    headers={
                        "Authorization": f"Token {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"text": clean_text}
                )
                return response.content if response.status_code == 200 else None
        except Exception as e:
            print(f"TTS error: {e}")
            return None
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        return [
            {"id": "aura-asteria-en", "name": "Asteria", "gender": "female"},
            {"id": "aura-luna-en", "name": "Luna", "gender": "female"},
            {"id": "aura-orion-en", "name": "Orion", "gender": "male"},
        ]
