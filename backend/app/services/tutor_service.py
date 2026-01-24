"""
AI Tutor Service - Conversational AI Tutor with Video Generation Integration

Uses DeepSeek V3.2 for explanations and can trigger Qwen 2.5 Coder for Manim visualizations.
Supports iterative video modification through conversational context.
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
    - Automatic video generation triggering when visual explanation needed
    - Video modification detection and regeneration
    - Deepgram TTS for voice responses
    """
    
    TUTOR_SYSTEM_PROMPT = """You are an expert AI tutor specializing in mathematics, physics, algorithms, and machine learning.
Your role is to explain complex concepts clearly and engagingly.

IMPORTANT RULES:
1. Be conversational and friendly, like a helpful teacher
2. Use markdown formatting for clarity (headers, bullet points, code blocks, LaTeX math)
3. When a concept would benefit from visual explanation, suggest generating a video
4. Keep responses concise but comprehensive
5. Use examples and analogies when helpful
6. For math, use LaTeX notation within $...$ or $$...$$

VISUAL DETECTION:
When the user asks something that would benefit from animation/visualization, include this JSON at the END of your response:
```json
{"should_generate_video": true, "video_prompt": "description for video generation"}
```

VIDEO MODIFICATION DETECTION:
If the user is asking to modify a previously generated video (e.g., "make it slower", "add labels", "more examples"), include:
```json
{"modify_video": true, "modifications": {"speed": "slower", "add_labels": true, "more_examples": true}}
```

Only include the JSON block when appropriate, not for every response."""

    VIDEO_MODIFICATION_PATTERNS = [
        r"make it (slower|faster|longer|shorter)",
        r"add (labels|colors|more examples|annotations)",
        r"change the (speed|color|style|duration)",
        r"(slower|faster) animation",
        r"more (detail|examples|steps)",
        r"remove (labels|colors|text)",
        r"focus on (step|part|section)",
    ]
    
    def __init__(self):
        # DeepSeek for conversational tutoring
        self.llm = LLMClient(agent_type="deepseek")
        self.conversation_history: List[Dict[str, str]] = []
        self.current_video_context: Optional[Dict[str, Any]] = None
    
    async def chat(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return AI response with optional video generation trigger.
        
        Args:
            message: User's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            {
                "response": "AI tutor response text",
                "should_generate_video": bool,
                "video_prompt": Optional[str],
                "modify_video": bool,
                "modifications": Optional[Dict]
            }
        """
        history = conversation_history or self.conversation_history
        
        # Check for video modification request
        modification_detected = self._detect_modification_request(message)
        
        # Build conversation context
        context = self._build_context(message, history)
        
        # Get response from DeepSeek
        try:
            response_text = await self.llm.chat(
                context,
                temperature=0.7,
                max_tokens=2000
            )
            
            if not response_text:
                response_text = "I apologize, but I'm having trouble connecting right now. Could you please try again?"
        except Exception as e:
            print(f"Tutor chat error: {e}")
            response_text = "I encountered an error. Let me try to help you differently. Could you rephrase your question?"
        
        # Parse response for video generation signals
        result = self._parse_response(response_text, modification_detected)
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": result["response"]})
        
        return result
    
    def _build_context(self, message: str, history: List[Dict[str, str]]) -> str:
        """Build the full context prompt for the LLM."""
        context_parts = [self.TUTOR_SYSTEM_PROMPT, "\n\n"]
        
        # Add conversation history (last 10 messages to avoid token limits)
        recent_history = history[-10:] if len(history) > 10 else history
        for msg in recent_history:
            role = "User" if msg["role"] == "user" else "Tutor"
            context_parts.append(f"{role}: {msg['content']}\n\n")
        
        # Add current video context if exists
        if self.current_video_context:
            context_parts.append(f"\n[Current video context: {self.current_video_context.get('prompt', 'N/A')}]\n\n")
        
        # Add current message
        context_parts.append(f"User: {message}\n\nTutor:")
        
        return "".join(context_parts)
    
    def _detect_modification_request(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect if user is requesting modifications to the current video."""
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
        """Parse the LLM response and extract any video generation signals."""
        result = {
            "response": response_text,
            "should_generate_video": False,
            "video_prompt": None,
            "modify_video": False,
            "modifications": None
        }
        
        # Try to extract JSON block from response
        json_match = re.search(r'```json\s*(\{[^`]+\})\s*```', response_text)
        if json_match:
            try:
                signals = json.loads(json_match.group(1))
                
                if signals.get("should_generate_video"):
                    result["should_generate_video"] = True
                    result["video_prompt"] = signals.get("video_prompt", "")
                    # Remove JSON block from response text
                    result["response"] = response_text.replace(json_match.group(0), "").strip()
                
                if signals.get("modify_video"):
                    result["modify_video"] = True
                    result["modifications"] = signals.get("modifications", {})
                    result["response"] = response_text.replace(json_match.group(0), "").strip()
                    
            except json.JSONDecodeError:
                pass
        
        # Override with explicit modification detection
        if modification and modification.get("detected"):
            result["modify_video"] = True
            result["modifications"] = {"detected_change": modification["match"]}
            if modification.get("original_prompt"):
                result["video_prompt"] = modification["original_prompt"]
        
        return result
    
    def set_video_context(self, video_data: Dict[str, Any]):
        """Store the current video context for modification requests."""
        self.current_video_context = video_data
    
    def clear_history(self):
        """Clear conversation history and video context."""
        self.conversation_history = []
        self.current_video_context = None


class DeepgramTTS:
    """
    Deepgram Text-to-Speech service for high-quality voice generation.
    """
    
    DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"
    
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY if hasattr(settings, 'DEEPGRAM_API_KEY') else None
    
    async def synthesize(
        self, 
        text: str, 
        voice: str = "aura-asteria-en",
        encoding: str = "mp3"
    ) -> Optional[bytes]:
        """
        Convert text to speech using Deepgram.
        
        Args:
            text: Text to convert to speech
            voice: Deepgram voice model (e.g., aura-asteria-en, aura-luna-en)
            encoding: Audio encoding (mp3, wav, etc.)
            
        Returns:
            Audio bytes or None if failed
        """
        if not self.api_key:
            print("Deepgram API key not configured")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.DEEPGRAM_TTS_URL}?model={voice}&encoding={encoding}",
                    headers={
                        "Authorization": f"Token {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"text": text}
                )
                
                if response.status_code == 200:
                    return response.content
                else:
                    print(f"Deepgram TTS error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Deepgram TTS failed: {e}")
            return None
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Return list of available Deepgram voices."""
        return [
            {"id": "aura-asteria-en", "name": "Asteria", "gender": "female", "accent": "American"},
            {"id": "aura-luna-en", "name": "Luna", "gender": "female", "accent": "American"},
            {"id": "aura-stella-en", "name": "Stella", "gender": "female", "accent": "American"},
            {"id": "aura-orion-en", "name": "Orion", "gender": "male", "accent": "American"},
            {"id": "aura-arcas-en", "name": "Arcas", "gender": "male", "accent": "American"},
        ]
