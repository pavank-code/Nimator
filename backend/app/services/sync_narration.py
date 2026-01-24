"""
Synchronized Narration Generator

Generates narration that follows the VISUAL-FIRST principle:
1. Describe WHAT appears on screen
2. State the mathematical expression
3. Explain the intuition
4. Transition to the next visual

CRITICAL: Narration must TRAIL visualization, never lead it.
"""
from typing import Dict, Any, List, Optional


class SyncNarrationGenerator:
    """
    Generates visual-synchronized narration for each scene.
    
    The narration follows the mandatory explanation loop:
    A. Visual Action - What just appeared
    B. Mathematical Expression - The equation/rule
    C. Intuition - Simple meaning
    D. Transition - What comes next
    """
    
    # Templates for different visual types
    VISUAL_ACTION_TEMPLATES = {
        "graph_2d": [
            "Now on the screen, you can see a coordinate system with axes.",
            "As this curve is being drawn, watch how it takes shape.",
            "Here we have a graph showing the function.",
            "Notice the curve appearing on the screen.",
        ],
        "vector_arrows": [
            "Now appearing on the screen are arrows - vectors.",
            "Watch as these vectors are drawn from the origin.",
            "Here we have arrows representing directions and magnitudes.",
            "Notice these directional arrows appearing.",
        ],
        "text_labels": [
            "Now appearing on the screen is our key formula.",
            "Here we see the mathematical expression.",
            "Watch as this equation is revealed.",
            "Notice the text appearing center screen.",
        ],
        "dots_paths": [
            "Now on the screen, you can see a starting point.",
            "Watch as a path is traced from one point to another.",
            "Here we have a trajectory being drawn.",
            "Notice the movement from start to end.",
        ],
    }
    
    TRANSITION_TEMPLATES = [
        "Next, we'll see...",
        "Let's now visualize...",
        "Moving on, we'll draw...",
        "The next step will show...",
        "Coming up, you'll see...",
    ]
    
    def __init__(self):
        self._template_index = 0
    
    def generate_narration(
        self,
        scene: Dict[str, Any],
        scene_index: int,
        total_scenes: int,
        next_scene: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate synchronized narration for a scene.
        
        The narration ALWAYS starts by describing what is visible,
        then explains the math, then gives intuition, then transitions.
        """
        scene_type = scene.get("scene_type", "text_labels")
        narration_parts = []
        
        # A. VISUAL ACTION - What just appeared
        visual_action = self._generate_visual_action(scene, scene_type)
        narration_parts.append(visual_action)
        
        # B. MATHEMATICAL EXPRESSION - The equation
        math_expression = self._generate_math_description(scene)
        if math_expression:
            narration_parts.append(math_expression)
        
        # C. INTUITION - Simple meaning
        intuition = self._generate_intuition(scene)
        if intuition:
            narration_parts.append(intuition)
        
        # D. TRANSITION - What comes next (only if not last scene)
        if next_scene and scene_index < total_scenes - 1:
            transition = self._generate_transition(next_scene)
            narration_parts.append(transition)
        
        return " ".join(narration_parts)
    
    def _generate_visual_action(self, scene: Dict[str, Any], scene_type: str) -> str:
        """Generate the visual action description."""
        templates = self.VISUAL_ACTION_TEMPLATES.get(scene_type, self.VISUAL_ACTION_TEMPLATES["text_labels"])
        template = templates[self._template_index % len(templates)]
        self._template_index += 1
        
        # Customize based on scene content
        if scene_type == "graph_2d":
            func = scene.get("function", "x squared")
            func_readable = self._function_to_readable(func)
            return f"Now on the screen, you can see a graph. {func_readable} is being drawn as a curve."
        
        elif scene_type == "vector_arrows":
            vectors = scene.get("vectors", [])
            labels = scene.get("labels", [])
            if labels:
                label_str = ", ".join(labels[:2])
                return f"Now appearing on the screen are vectors labeled {label_str}."
            return "Now appearing on the screen are arrows representing vectors."
        
        elif scene_type == "text_labels":
            text = scene.get("text", "")
            if scene.get("math_mode"):
                return f"Here on the screen, you can see the mathematical expression."
            return f"Now appearing on the screen: {text[:50]}..."
        
        elif scene_type == "dots_paths":
            start = scene.get("start_point", [0, 0])
            end = scene.get("end_point", [1, 1])
            return f"Watch as a path is traced from point ({start[0]}, {start[1]}) to ({end[0]}, {end[1]})."
        
        return template
    
    def _generate_math_description(self, scene: Dict[str, Any]) -> Optional[str]:
        """Generate the mathematical expression description."""
        scene_type = scene.get("scene_type", "")
        
        if scene_type == "graph_2d":
            func = scene.get("function", "")
            if func:
                readable = self._function_to_readable(func)
                return f"Mathematically, this is {readable}."
        
        elif scene_type == "text_labels" and scene.get("math_mode"):
            text = scene.get("text", "")
            return f"This equation shows: {text}."
        
        elif scene_type == "vector_arrows":
            labels = scene.get("labels", [])
            if labels and "nabla" in str(labels).lower():
                return "This represents the gradient, pointing in the direction of steepest ascent."
        
        return None
    
    def _generate_intuition(self, scene: Dict[str, Any]) -> Optional[str]:
        """Generate the intuition explanation."""
        # Use the scene's narration if provided, as it contains the explanation
        narration = scene.get("narration", "")
        if narration:
            # Extract just the intuition part (skip visual descriptions)
            sentences = narration.split(". ")
            intuition_sentences = [s for s in sentences if not any(
                phrase in s.lower() for phrase in 
                ["on the screen", "you can see", "watch", "notice", "appearing"]
            )]
            if intuition_sentences:
                return ". ".join(intuition_sentences[:2]) + "."
        
        return None
    
    def _generate_transition(self, next_scene: Dict[str, Any]) -> str:
        """Generate transition to the next scene."""
        next_type = next_scene.get("scene_type", "")
        template = self.TRANSITION_TEMPLATES[self._template_index % len(self.TRANSITION_TEMPLATES)]
        
        type_descriptions = {
            "graph_2d": "a new graph",
            "vector_arrows": "some vectors",
            "text_labels": "an important formula",
            "dots_paths": "a path of movement",
        }
        
        desc = type_descriptions.get(next_type, "the next concept")
        return f"{template} {desc}."
    
    def _function_to_readable(self, func: str) -> str:
        """Convert a function string to readable speech."""
        readable = func
        readable = readable.replace("**2", " squared")
        readable = readable.replace("**3", " cubed")
        readable = readable.replace("**", " to the power of ")
        readable = readable.replace("*", " times ")
        readable = readable.replace("sin(x)", "sine of x")
        readable = readable.replace("cos(x)", "cosine of x")
        readable = readable.replace("exp(", "e to the ")
        readable = readable.replace("sqrt(", "square root of ")
        readable = readable.replace("log(", "log of ")
        readable = readable.replace("(", "").replace(")", "")
        return f"y equals {readable}"


def generate_sync_narration(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate synchronized narration for all scenes.
    
    Each scene's narration will follow the visual-first principle.
    """
    generator = SyncNarrationGenerator()
    updated_scenes = []
    
    for i, scene in enumerate(scenes):
        next_scene = scenes[i + 1] if i < len(scenes) - 1 else None
        
        # Generate new synchronized narration
        sync_narration = generator.generate_narration(
            scene, 
            scene_index=i,
            total_scenes=len(scenes),
            next_scene=next_scene
        )
        
        # Update scene with synchronized narration
        updated_scene = scene.copy()
        updated_scene["sync_narration"] = sync_narration
        
        # Keep original narration as "explanation" for reference
        if "narration" in scene:
            updated_scene["explanation"] = scene["narration"]
        
        updated_scenes.append(updated_scene)
    
    return updated_scenes
