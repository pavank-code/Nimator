"""
Sync Orchestrator - Ensures Dialogue Drives Visualization

This module enforces the core principle:
"Dialogue drives visualization, visualization confirms dialogue, both are synchronized through an explicit plan."

The orchestrator ensures:
1. Visual intent is extracted from dialogue BEFORE visualization
2. Manim scenes are generated from explicit visual intents
3. State is updated AFTER rendering confirms
4. Narration is ONLY allowed after state confirms object exists
"""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from app.services.visual_state import VisualState, VisualObjectType, get_visual_state


class SyncPhase(str, Enum):
    """Phases of the synchronized explanation loop."""
    VISUAL_ACTION = "visual_action"      # Describe what just appeared
    MATHEMATICAL = "mathematical"         # State the equation/rule
    INTUITION = "intuition"              # Explain the meaning
    TRANSITION = "transition"            # State what comes next


@dataclass
class VisualIntent:
    """
    Represents the visual intent extracted from dialogue.
    
    This is what the tutor WANTS to show, before it's rendered.
    """
    intent_type: str  # e.g., "plot_function", "show_vector", "display_equation"
    description: str  # Natural language description
    parameters: Dict[str, Any]  # Specific parameters for Manim
    dialogue_trigger: str  # The phrase that triggered this intent
    
    def to_scene_spec(self) -> Dict[str, Any]:
        """Convert intent to a Manim scene specification."""
        if self.intent_type == "plot_function":
            return {
                "scene_type": "graph_2d",
                "function": self.parameters.get("function", "x**2"),
                "x_range": self.parameters.get("x_range", [-4, 4, 1]),
                "y_range": self.parameters.get("y_range", [-2, 10, 2]),
                "narration": self.description
            }
        elif self.intent_type == "show_vector":
            return {
                "scene_type": "vector_arrows",
                "vectors": self.parameters.get("vectors", [[1, 1]]),
                "labels": self.parameters.get("labels", []),
                "narration": self.description
            }
        elif self.intent_type == "display_equation":
            return {
                "scene_type": "text_labels",
                "text": self.parameters.get("equation", ""),
                "math_mode": True,
                "narration": self.description
            }
        elif self.intent_type == "show_path":
            return {
                "scene_type": "dots_paths",
                "start_point": self.parameters.get("start", [0, 0]),
                "end_point": self.parameters.get("end", [1, 1]),
                "path_type": self.parameters.get("path_type", "curve"),
                "narration": self.description
            }
        else:
            return {
                "scene_type": "text_labels",
                "text": self.description,
                "math_mode": False,
                "narration": self.description
            }


class SyncOrchestrator:
    """
    Orchestrates the synchronized dialogue-visualization loop.
    
    Core responsibilities:
    1. Extract visual intents from tutor dialogue
    2. Generate Manim scenes from intents
    3. Update visual state after rendering
    4. Gate narration based on confirmed state
    """
    
    # Patterns that indicate visual intent
    VISUAL_INTENT_PATTERNS = [
        # Function plotting
        (r"let'?s?\s+(?:visualize|plot|draw|show|see)\s+(?:a\s+)?(?:the\s+)?(.+?)(?:\s+function|\s+curve|\s*$)", "plot_function"),
        (r"(?:visualize|plot|draw|show)\s+(?:the\s+)?(?:function\s+)?(?:y\s*=\s*)?([^\s,\.]+)", "plot_function"),
        (r"(?:here'?s?\s+)?(?:the\s+)?graph\s+of\s+(.+)", "plot_function"),
        
        # Vector operations
        (r"(?:show|draw|visualize)\s+(?:a\s+)?(?:the\s+)?vector\s*(.+)?", "show_vector"),
        (r"(?:the\s+)?gradient\s+(?:vector|points?)", "show_vector"),
        
        # Equations
        (r"(?:the\s+)?(?:update\s+)?(?:rule|equation|formula)\s+(?:is\s+)?(.+)", "display_equation"),
        (r"(?:we\s+)?(?:can\s+)?write\s+(?:this\s+)?(?:as\s+)?(.+)", "display_equation"),
        
        # Paths and movement
        (r"(?:watch|see|notice)\s+(?:how\s+)?(?:the\s+)?(?:point\s+)?(?:moves?|travels?|goes?)", "show_path"),
        (r"(?:convergence|optimization)\s+path", "show_path"),
    ]
    
    # Mathematical expressions to extract
    MATH_PATTERNS = [
        r"y\s*=\s*([^\s,\.]+)",
        r"f\(x\)\s*=\s*([^\s,\.]+)",
        r"\$\$?([^\$]+)\$\$?",
        r"\\frac\{[^}]+\}\{[^}]+\}",
        r"\\(?:sin|cos|tan|exp|log|sqrt)\s*\([^)]+\)",
    ]
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.visual_state = get_visual_state(session_id)
        self.pending_intents: List[VisualIntent] = []
        self.confirmed_visuals: List[str] = []  # Object IDs that are confirmed rendered
        self.current_phase = SyncPhase.VISUAL_ACTION
        
    def extract_visual_intent(self, dialogue: str) -> List[VisualIntent]:
        """
        Extract visual intents from tutor dialogue.
        
        This is called BEFORE the tutor explains, to determine what needs to be rendered.
        """
        intents = []
        dialogue_lower = dialogue.lower()
        
        for pattern, intent_type in self.VISUAL_INTENT_PATTERNS:
            match = re.search(pattern, dialogue_lower)
            if match:
                captured = match.group(1) if match.lastindex else ""
                
                # Extract specific parameters based on intent type
                params = self._extract_parameters(dialogue, intent_type, captured)
                
                intent = VisualIntent(
                    intent_type=intent_type,
                    description=dialogue,
                    parameters=params,
                    dialogue_trigger=match.group(0)
                )
                intents.append(intent)
        
        self.pending_intents.extend(intents)
        return intents
    
    def _extract_parameters(self, dialogue: str, intent_type: str, captured: str) -> Dict[str, Any]:
        """Extract specific parameters for each intent type."""
        params = {}
        
        if intent_type == "plot_function":
            # Try to extract the function
            func_match = re.search(r"(?:sin|cos|tan|exp|log|sqrt|x\*\*\d+|x\^?\d*)", captured.lower())
            if func_match:
                func = func_match.group(0)
                # Convert common notations
                func = func.replace("^", "**")
                params["function"] = func
            else:
                # Try to extract from LaTeX
                latex_match = re.search(r"\$([^\$]+)\$", dialogue)
                if latex_match:
                    params["function"] = self._latex_to_python(latex_match.group(1))
                else:
                    params["function"] = "x**2"  # Default
                    
        elif intent_type == "show_vector":
            # Extract vector components if present
            vec_match = re.search(r"\[?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\]?", dialogue)
            if vec_match:
                params["vectors"] = [[float(vec_match.group(1)), float(vec_match.group(2))]]
            
            # Extract labels
            label_match = re.search(r"\\nabla\s*(\w+)|gradient|\\vec\{?(\w+)\}?", dialogue)
            if label_match:
                label = label_match.group(1) or label_match.group(2) or "v"
                params["labels"] = [f"\\nabla {label}" if "gradient" in dialogue.lower() else label]
                
        elif intent_type == "display_equation":
            # Extract the equation
            latex_match = re.search(r"\$\$?([^\$]+)\$\$?", dialogue)
            if latex_match:
                params["equation"] = latex_match.group(1)
            else:
                params["equation"] = captured
                
        return params
    
    def _latex_to_python(self, latex: str) -> str:
        """Convert LaTeX notation to Python/SymPy format."""
        result = latex.strip()
        result = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1)/(\2)", result)
        result = result.replace("\\sin", "sin")
        result = result.replace("\\cos", "cos")
        result = result.replace("\\tan", "tan")
        result = result.replace("\\exp", "exp")
        result = result.replace("\\log", "log")
        result = result.replace("\\sqrt", "sqrt")
        result = result.replace("^", "**")
        result = result.replace("{", "(").replace("}", ")")
        return result
    
    def confirm_render(self, intent: VisualIntent, object_ids: List[str]):
        """
        Called AFTER Manim has successfully rendered the visual.
        Updates the visual state to allow narration.
        """
        # Add objects to visual state
        scene_spec = intent.to_scene_spec()
        self.visual_state._populate_from_scene(scene_spec)
        
        # Track confirmed visuals
        self.confirmed_visuals.extend(object_ids)
    
    def can_describe(self, object_id: str) -> bool:
        """Check if the tutor is allowed to describe this object."""
        return self.visual_state.object_exists(object_id)
    
    def gate_narration(self, narration: str) -> Tuple[str, List[str]]:
        """
        Gate narration to only include references to confirmed visuals.
        
        Returns:
            Tuple of (filtered_narration, list_of_blocked_references)
        """
        blocked = []
        filtered = narration
        
        # Check for references to non-existent visuals
        visual_refs = [
            (r"the\s+(\w+)\s+curve", "curve"),
            (r"the\s+(\w+)\s+graph", "graph"),
            (r"the\s+(\w+)\s+vector", "vector"),
            (r"the\s+(\w+)\s+point", "dot"),
            (r"the\s+(\w+)\s+line", "path"),
        ]
        
        for pattern, obj_type in visual_refs:
            matches = re.finditer(pattern, narration.lower())
            for match in matches:
                # Check if any object of this type exists
                has_type = any(
                    obj.object_type.value == obj_type or obj.object_type.value == "graph_2d"
                    for obj in self.visual_state.visible_objects
                )
                if not has_type:
                    blocked.append(match.group(0))
        
        # If there are blocked references, add a warning
        if blocked:
            filtered = f"[SYNC WARNING: Some visuals not yet rendered] {narration}"
        
        return filtered, blocked
    
    def generate_sync_prompt(self) -> str:
        """
        Generate the synchronization context for the tutor prompt.
        Includes current phase and what actions are allowed.
        """
        state_prompt = self.visual_state.generate_visual_context_prompt()
        
        phase_guidance = {
            SyncPhase.VISUAL_ACTION: """
CURRENT PHASE: VISUAL ACTION
Your task: Describe exactly what just appeared or changed on the screen.
Use phrases like "Now on the screen, you can see..." or "As this appears..."
""",
            SyncPhase.MATHEMATICAL: """
CURRENT PHASE: MATHEMATICAL EXPRESSION
Your task: State the equation or rule that matches the visual.
Connect the visual to its mathematical representation.
""",
            SyncPhase.INTUITION: """
CURRENT PHASE: INTUITION
Your task: Explain the meaning in simple terms.
Help the learner understand WHY this visual matters.
""",
            SyncPhase.TRANSITION: """
CURRENT PHASE: TRANSITION
Your task: Briefly state what will be visualized next.
Do NOT explain the next visual - just announce it.
"""
        }
        
        return f"""
{state_prompt}

{phase_guidance.get(self.current_phase, "")}
"""
    
    def advance_phase(self):
        """Advance to the next phase of the explanation loop."""
        phases = list(SyncPhase)
        current_idx = phases.index(self.current_phase)
        next_idx = (current_idx + 1) % len(phases)
        self.current_phase = phases[next_idx]
        
        # If we're back to VISUAL_ACTION, we need new visuals
        if self.current_phase == SyncPhase.VISUAL_ACTION:
            return True  # Signal that new visuals should be rendered
        return False


# Session storage for orchestrators
_orchestrators: Dict[str, SyncOrchestrator] = {}


def get_sync_orchestrator(session_id: str) -> SyncOrchestrator:
    """Get or create sync orchestrator for a session."""
    if session_id not in _orchestrators:
        _orchestrators[session_id] = SyncOrchestrator(session_id)
    return _orchestrators[session_id]
