"""
Session Orchestrator - The Control Plane

The Orchestrator is the SINGLE SOURCE OF TRUTH for flow control.
It decides:
- Which model to call
- When to call it
- What context to pass

AI models are stateless workers. All continuity comes from State + Orchestrator.
"""
from typing import Dict, Any, Optional, List, Tuple
import json
import uuid
import asyncio
from datetime import datetime

from app.models.session_state import SessionState, VisualObject, Scene, BranchStatus
from app.services.topic_classifier import LLMClient
from app.config import settings


class SessionOrchestrator:
    """
    Orchestrates the DeepSeek → Qwen → Renderer pipeline.
    
    Flow:
    1. User message → DeepSeek (tutor) → Explanation + Video Intent
    2. Video Intent → Orchestrator → Structured Scene Spec
    3. Scene Spec → Qwen (coder) → Manim Code + Visual Objects
    4. Manim Code → Renderer → Video
    5. Result → Frontend (synced explanation + video)
    """
    
    # DeepSeek: Conversational tutor with visual-first pedagogy
    DEEPSEEK_TUTOR_PROMPT = """You are an expert AI tutor using VISUAL-FIRST PEDAGOGY.
Your name is DeepSeek Tutor. You specialize in mathematics, physics, algorithms, and machine learning.

=== YOUR ROLE ===
Explain concepts conversationally to students AND trigger visual explanations when helpful.
You are NOT generating animation code. You are teaching like a human tutor would.

=== VISUAL-FIRST RULES ===
1. When explaining, describe what the student should SEE
2. Reference visuals as you explain: "Look at the curve...", "Notice how the tangent..."
3. If concept needs animation, include video generation intent
4. Ground explanations in visuals, not abstract theory

=== CONVERSATION CONTEXT ===
{conversation_context}

=== CURRENT VISUAL OBJECTS ON SCREEN ===
{visual_objects}

=== OUTPUT FORMAT ===
Respond with valid JSON only:
{{
    "explanation": "Your conversational explanation here (use markdown, LaTeX math in $...$)",
    "should_generate_video": true/false,
    "video_intent": {{
        "concept": "What concept to visualize",
        "visual_focus": ["object1", "object2"],
        "pedagogy": "How to teach it visually (what to show first, second, etc.)",
        "estimated_duration": 10,
        "reuse_objects": ["existing_object_ids to keep on screen"],
        "new_objects": [
            {{
                "type": "curve|point|vector|label|tangent|area",
                "description": "What this object represents",
                "color_hint": "primary|secondary|accent|contrast"
            }}
        ]
    }}
}}

If no video needed, set should_generate_video: false and omit video_intent.

=== USER MESSAGE ===
{user_message}

Respond with JSON:"""

    # Qwen: Deterministic Manim code generator
    QWEN_CODER_PROMPT = """You are a Manim animation specialist called Qwen Coder.
Your job: Convert concept descriptions into precise Manim animation code.

=== YOUR ROLE ===
Generate deterministic Manim Python code from structured scene specifications.
You receive structured specs, NOT free-form prompts.

=== INPUT SPECIFICATION ===
{scene_spec}

=== AVAILABLE SCENE TYPES ===
1. graph_2d - ParametricFunction, axes, curves
2. vector_arrows - Arrow, Vector with labels
3. dots_paths - Dot, TracedPath, ParametricFunction tracing
4. text_labels - MathTex, Text, Title

=== OUTPUT FORMAT ===
Respond with valid JSON only:
{{
    "scene_code": "Complete Manim Python code as a string",
    "visual_objects": [
        {{
            "object_id": "{object_id_prefix}_001",
            "manim_class": "ParametricFunction",
            "manim_variable": "curve_f",
            "display_name": "f(x) = x²",
            "color": "#FFD700",
            "properties": {{}}
        }}
    ],
    "animation_sequence": [
        {{"action": "create", "object": "curve_f", "duration": 2}},
        {{"action": "wait", "duration": 1}}
    ],
    "total_duration_seconds": 10
}}

=== RULES ===
1. Use Python/SymPy syntax for math: ** for power, sin/cos/exp/log
2. Generate syntactically valid Manim code
3. Use the exact object_id_prefix provided
4. Match duration to the specification
5. Create smooth, educational animations
6. Add appropriate labels and annotations

Generate the Manim scene:"""

    # Color palette for visual variety
    COLOR_PALETTE = {
        "primary": "#FFD700",    # Gold
        "secondary": "#4169E1",  # Royal Blue
        "accent": "#32CD32",     # Lime Green
        "contrast": "#FF6B6B",   # Coral
        "highlight": "#A855F7",  # Purple
    }

    def __init__(self):
        # DeepSeek for tutoring/reasoning
        self.deepseek = LLMClient(agent_type="deepseek")
        # Qwen for code generation
        self.qwen = LLMClient(agent_type="qwen")
        # Session states (in-memory for now)
        self.sessions: Dict[str, SessionState] = {}
    
    def get_or_create_session(self, session_id: Optional[str], topic: str) -> SessionState:
        """Get existing session or create new one."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        # Create new session
        state = SessionState.create_new(topic)
        self.sessions[state.session_id] = state
        return state
    
    async def process_message(
        self, 
        message: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: Process user message through the pipeline.
        
        Returns:
        {
            "session_id": str,
            "explanation": str,
            "video_generating": bool,
            "video_job_id": Optional[str],
            "video_url": Optional[str],
            "visual_objects": List[Dict]
        }
        """
        # Step 1: Get or create session
        state = self.get_or_create_session(session_id, message)
        
        # Step 2: Add user message to state
        state.add_message("user", message)
        
        # Step 3: Call DeepSeek for explanation + video intent
        deepseek_response = await self._call_deepseek(state, message)
        
        # Step 4: Parse DeepSeek response
        explanation = deepseek_response.get("explanation", "I'll help you understand this concept.")
        should_generate = deepseek_response.get("should_generate_video", False)
        video_intent = deepseek_response.get("video_intent", None)
        
        # Step 5: Add assistant message
        state.add_message("assistant", explanation)
        
        result = {
            "session_id": state.session_id,
            "explanation": explanation,
            "video_generating": False,
            "video_job_id": None,
            "video_url": None,
            "visual_objects": [obj.to_dict() for obj in state.get_active_objects()]
        }
        
        # Step 6: If video needed, call Qwen and trigger render
        if should_generate and video_intent:
            video_result = await self._generate_video(state, video_intent)
            result["video_generating"] = True
            result["video_job_id"] = video_result.get("job_id")
            result["scene_spec"] = video_result.get("scene_spec")
        
        # Checkpoint state
        state.checkpoint()
        
        return result
    
    async def _call_deepseek(self, state: SessionState, message: str) -> Dict[str, Any]:
        """Call DeepSeek with tutor prompt and parse response."""
        
        # Build conversation context
        recent_messages = state.get_recent_messages(6)
        context_lines = []
        for msg in recent_messages:
            role = "Student" if msg.role == "user" else "Tutor"
            context_lines.append(f"{role}: {msg.content}")
        conversation_context = "\n".join(context_lines) if context_lines else "New conversation"
        
        # Build visual objects context
        active_objects = state.get_active_objects()
        if active_objects:
            obj_descriptions = [
                f"- {obj.display_name} ({obj.object_type}, {obj.color})"
                for obj in active_objects
            ]
            visual_objects = "\n".join(obj_descriptions)
        else:
            visual_objects = "No visual objects on screen yet."
        
        # Format prompt
        prompt = self.DEEPSEEK_TUTOR_PROMPT.format(
            conversation_context=conversation_context,
            visual_objects=visual_objects,
            user_message=message
        )
        
        try:
            response = await self.deepseek.chat(
                prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            if not response:
                return {"explanation": "I'm having trouble thinking right now. Could you rephrase?"}
            
            # Parse JSON response
            return self._parse_json_response(response)
            
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return {"explanation": f"I encountered an issue. Let me try differently: {message}"}
    
    async def _generate_video(self, state: SessionState, video_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video using Qwen for code and renderer for execution."""
        
        # Step 1: Create scene spec from video intent
        scene_spec = self._create_scene_spec(state, video_intent)
        
        # Step 2: Call Qwen for Manim code
        qwen_response = await self._call_qwen(state, scene_spec)
        
        if not qwen_response or "scene_code" not in qwen_response:
            return {"error": "Failed to generate animation code"}
        
        # Step 3: Register visual objects in state
        for obj_data in qwen_response.get("visual_objects", []):
            state.add_visual_object(
                object_type=obj_data.get("manim_class", "unknown"),
                manim_class=obj_data.get("manim_class", "Mobject"),
                display_name=obj_data.get("display_name", "object"),
                color=obj_data.get("color", "#FFFFFF"),
                scene_id=scene_spec["scene_id"],
                properties=obj_data.get("properties", {})
            )
        
        # Step 4: Add scene to state
        scene = state.add_scene(
            concept=video_intent.get("concept", "explanation"),
            narration_text=video_intent.get("pedagogy", ""),
            duration_seconds=qwen_response.get("total_duration_seconds", 10),
            manim_code=qwen_response.get("scene_code")
        )
        
        # Step 5: Queue for rendering (integrate with existing renderer)
        job_id = await self._queue_render_job(state, scene, qwen_response)
        
        return {
            "job_id": job_id,
            "scene_spec": scene_spec,
            "scene_id": scene.scene_id
        }
    
    def _create_scene_spec(self, state: SessionState, video_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DeepSeek's video intent into structured spec for Qwen."""
        
        scene_id = state.generate_scene_id()
        object_id_prefix = f"{state.session_id}_{scene_id}"
        
        # Resolve color hints to actual colors
        new_objects = []
        for obj in video_intent.get("new_objects", []):
            color_hint = obj.get("color_hint", "primary")
            color = self.COLOR_PALETTE.get(color_hint, self.COLOR_PALETTE["primary"])
            new_objects.append({
                "type": obj.get("type", "curve"),
                "description": obj.get("description", ""),
                "color": color,
                "object_id": f"{object_id_prefix}_{len(new_objects)+1:03d}"
            })
        
        return {
            "scene_id": scene_id,
            "object_id_prefix": object_id_prefix,
            "concept": video_intent.get("concept", ""),
            "visual_focus": video_intent.get("visual_focus", []),
            "pedagogy": video_intent.get("pedagogy", ""),
            "estimated_duration": video_intent.get("estimated_duration", 10),
            "reuse_objects": video_intent.get("reuse_objects", []),
            "new_objects": new_objects,
            "existing_objects": [
                obj.to_dict() for obj in state.get_active_objects()
            ]
        }
    
    async def _call_qwen(self, state: SessionState, scene_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Call Qwen with coder prompt to generate Manim code."""
        
        prompt = self.QWEN_CODER_PROMPT.format(
            scene_spec=json.dumps(scene_spec, indent=2),
            object_id_prefix=scene_spec["object_id_prefix"]
        )
        
        try:
            response = await self.qwen.chat(
                prompt,
                temperature=0.3,  # More deterministic for code
                max_tokens=3000
            )
            
            if not response:
                return self._generate_fallback_scene(scene_spec)
            
            return self._parse_json_response(response)
            
        except Exception as e:
            print(f"Qwen error: {e}")
            return self._generate_fallback_scene(scene_spec)
    
    async def _queue_render_job(self, state: SessionState, scene: Scene, qwen_response: Dict[str, Any]) -> str:
        """Queue the scene for rendering via Redis."""
        import redis
        
        job_id = str(uuid.uuid4())
        
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
            
            # Create job data compatible with existing renderer
            job_data = {
                "job_id": job_id,
                "prompt": scene.concept,
                "topic": state.topic_root,
                "scenes": [{
                    "scene_type": "graph_2d",  # Default, can be enhanced
                    "title": scene.concept,
                    "narration": scene.narration_text,
                    "manim_code": scene.manim_code,
                    "duration_seconds": scene.duration_seconds,
                    **self._extract_scene_params(qwen_response)
                }],
                "status": "queued",
                "progress": 0,
                "session_id": state.session_id
            }
            
            # Store job
            redis_client.set(f"job:{job_id}", json.dumps(job_data))
            redis_client.expire(f"job:{job_id}", 3600)
            
            # Add to render queue
            redis_client.lpush("render_queue", json.dumps(job_data))
            
            # Update state
            state.current_video_job_id = job_id
            
            return job_id
            
        except Exception as e:
            print(f"Redis error: {e}")
            return f"failed_{uuid.uuid4().hex[:8]}"
    
    def _extract_scene_params(self, qwen_response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract scene parameters from Qwen response for renderer."""
        # Default params
        params = {
            "function": "x**2",
            "x_range": [-5, 5],
            "y_range": [-3, 3],
            "color": "#FFD700"
        }
        
        # Try to extract from visual objects
        for obj in qwen_response.get("visual_objects", []):
            if obj.get("manim_class") in ["ParametricFunction", "FunctionGraph"]:
                params["color"] = obj.get("color", params["color"])
                break
        
        return params
    
    def _generate_fallback_scene(self, scene_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback scene when Qwen fails."""
        return {
            "scene_code": f'''
from manim import *

class FallbackScene(Scene):
    def construct(self):
        title = Text("{scene_spec.get('concept', 'Concept')}", font_size=48)
        self.play(Write(title))
        self.wait(2)
''',
            "visual_objects": [{
                "object_id": f"{scene_spec['object_id_prefix']}_001",
                "manim_class": "Text",
                "manim_variable": "title",
                "display_name": scene_spec.get("concept", "Concept"),
                "color": "#FFFFFF",
                "properties": {}
            }],
            "animation_sequence": [
                {"action": "write", "object": "title", "duration": 2},
                {"action": "wait", "duration": 2}
            ],
            "total_duration_seconds": 4
        }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        try:
            # Clean markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response was: {response[:500]}")
            return {}
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get serialized session state for debugging/inspection."""
        if session_id in self.sessions:
            return self.sessions[session_id].to_dict()
        return None


# Singleton instance
_orchestrator: Optional[SessionOrchestrator] = None

def get_orchestrator() -> SessionOrchestrator:
    """Get or create the singleton orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SessionOrchestrator()
    return _orchestrator
