"""
AI Tutor Service - Conversational AI Tutor with Video Generation Integration

Uses DeepSeek V3.2 for explanations and can trigger Qwen 2.5 Coder for Manim visualizations.
Supports LaTeX in responses and iterative video modification.
"""
from typing import Dict, Any, Optional, List
import json
import re
import httpx
from app.config import settings
from app.services.topic_classifier import LLMClient


class TutorService:
    """
    AI Tutor service providing conversational tutoring with video generation capabilities.
    
    Features:
    - ChatGPT-style conversation with DeepSeek V3.2
    - LaTeX support in responses (using $...$ and $$...$$ notation)
    - Automatic video generation triggering when visual explanation needed
    - Video modification detection and regeneration
    - Deepgram TTS for voice responses
    """
    
    TUTOR_SYSTEM_PROMPT = """You are an expert AI tutor specializing in mathematics, physics, algorithms, and machine learning.
Your role is to explain complex concepts clearly and engagingly, like a world-class professor.

FORMATTING RULES:
1. Use markdown for structure (headers ##, bold **, lists -)
2. Use LaTeX for ALL mathematical expressions:
   - Inline math: $x^2 + y^2 = r^2$
   - Display math: $$\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}$$
3. Use code blocks with language for code: ```python
4. Be conversational but precise
5. Use examples and analogies
6. Structure complex explanations with clear sections

VISUAL DETECTION:
When the user asks something that would benefit from animation/visualization, include this JSON at the END of your response:
```json
{"should_generate_video": true, "video_prompt": "description for video generation"}
```

VIDEO MODIFICATION DETECTION:
If the user is asking to modify a previously generated video, include:
```json
{"modify_video": true, "modifications": {"speed": "slower", "add_labels": true}}
```

Only include JSON blocks when appropriate. Always use LaTeX for math expressions."""

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
    
    async def chat(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Process a chat message and return AI response."""
        history = conversation_history or self.conversation_history
        modification_detected = self._detect_modification_request(message)
        context = self._build_context(message, history)
        
        try:
            response_text = await self.llm.chat(
                context,
                temperature=0.7,
                max_tokens=2500
            )
            
            if not response_text:
                response_text = "I apologize, but I'm having trouble right now. Could you please try again?"
        except Exception as e:
            print(f"Tutor chat error: {e}")
            response_text = "I encountered an error. Could you rephrase your question?"
        
        result = self._parse_response(response_text, modification_detected)
        
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": result["response"]})
        
        return result
    
    def _build_context(self, message: str, history: List[Dict[str, str]]) -> str:
        context_parts = [self.TUTOR_SYSTEM_PROMPT, "\n\n"]
        
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
