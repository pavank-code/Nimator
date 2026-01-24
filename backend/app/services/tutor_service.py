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
from app.services.topic_classifier import LLMClient
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
ABSOLUTE RULES (DO NOT BREAK THESE):
═══════════════════════════════════════════════════════════════════

1. NEVER explain a concept unless it has already been visualized.
2. NEVER describe a visual unless it is explicitly confirmed as rendered.
3. NEVER guess what is on the screen.
4. NEVER explain future steps before they appear visually.
5. ALWAYS describe WHAT appears before explaining WHY it matters.

═══════════════════════════════════════════════════════════════════
MANDATORY EXPLANATION LOOP (for every step):
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

GOOD EXAMPLES:
✓ "Now on the screen, you can see a smooth curve. This is the sine function, oscillating between -1 and 1."
✓ "Watch as the red dot moves along the curve... Notice how it follows the path we just drew."
✓ "Here's our coordinate system. The x-axis runs horizontally, the y-axis vertically."

BAD EXAMPLES (NEVER DO THIS):
✗ "Let me explain gradient descent..." (explaining before visualizing)
✗ "The yellow curve shows..." (if no yellow curve exists in state)
✗ "Imagine a parabola..." (describing non-existent visuals)

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

When the user asks for something that needs visualization, include at the END:
```json
{"should_generate_video": true, "video_prompt": "specific visual description"}
```

This triggers the Manim renderer. Only AFTER rendering completes will you
receive the visual state to describe.

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
        
        history = conversation_history or self.conversation_history
        modification_detected = self._detect_modification_request(message)
        
        # Build context with visual state
        context = self._build_context(message, history)
        
        # Extract visual intents from the user's message
        orchestrator = self.get_sync_orchestrator()
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
            
            # Gate the response through sync orchestrator
            if orchestrator:
                response_text, blocked = orchestrator.gate_narration(response_text)
                if blocked:
                    print(f"⚠️ Blocked {len(blocked)} references to non-existent visuals: {blocked}")
                    
        except Exception as e:
            print(f"Tutor chat error: {e}")
            response_text = "I encountered an error. Could you rephrase your question?"
        
        result = self._parse_response(response_text, modification_detected)
        
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": result["response"]})
        
        return result
    
    def _build_context(self, message: str, history: List[Dict[str, str]]) -> str:
        """Build context with visual state information."""
        context_parts = [self.TUTOR_SYSTEM_PROMPT, "\n\n"]
        
        # Inject current visual state
        visual_state = self.get_visual_state()
        if visual_state:
            visual_context = visual_state.generate_visual_context_prompt()
            context_parts.append(visual_context)
            context_parts.append("\n\n")
        else:
            context_parts.append("""
[VISUAL STATE: NO SESSION]
No visual session is active. When the user asks for a visualization,
trigger video generation. Only describe visuals after they are confirmed.
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
