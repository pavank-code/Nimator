"""
Visual State Tracker - Core Component for Visual-Synchronized Tutoring

This module maintains the source of truth for what is currently visible on screen.
The tutor CANNOT mention any visual that is not confirmed in this state.

Key Principle: EXPLANATION MUST TRAIL VISUALIZATION, NEVER LEAD IT.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class VisualObjectType(str, Enum):
    """Types of visual objects that can appear on screen."""
    GRAPH_2D = "graph_2d"
    GRAPH_3D = "graph_3d"
    VECTOR = "vector"
    DOT = "dot"
    PATH = "path"
    TEXT = "text"
    EQUATION = "equation"
    AXIS = "axis"
    CURVE = "curve"
    ARROW = "arrow"
    LABEL = "label"
    HIGHLIGHT = "highlight"
    ANIMATION = "animation"


@dataclass
class VisualObject:
    """
    Represents a single visual object currently on screen.
    
    The tutor may ONLY reference objects that exist in the VisualState.
    """
    object_id: str
    object_type: VisualObjectType
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_visible: bool = True
    parent_id: Optional[str] = None  # For grouped objects
    
    # Visual properties the tutor can reference
    color: Optional[str] = None
    position: Optional[List[float]] = None
    label: Optional[str] = None
    math_expression: Optional[str] = None
    
    def to_description(self) -> str:
        """Generate a natural language description for the tutor."""
        parts = [self.description]
        
        if self.color:
            parts.append(f"(colored {self.color})")
        if self.label:
            parts.append(f"labeled '{self.label}'")
        if self.math_expression:
            parts.append(f"showing: {self.math_expression}")
            
        return " ".join(parts)


class VisualState:
    """
    Maintains the ground truth of what is currently visible on screen.
    
    CRITICAL: The tutor service MUST query this state before describing anything.
    If an object is not in this state, it CANNOT be mentioned.
    
    This enforces the non-negotiable rule:
    "The tutor does NOT explain ideas. The tutor explains VISUAL ACTIONS as they happen."
    """
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self._objects: Dict[str, VisualObject] = {}
        self._focus_object_id: Optional[str] = None
        self._scene_history: List[Dict[str, Any]] = []
        self._current_scene_index: int = 0
        self._pending_visuals: List[Dict[str, Any]] = []  # Queued but not rendered
        
    @property
    def visible_objects(self) -> List[VisualObject]:
        """Get all currently visible objects."""
        return [obj for obj in self._objects.values() if obj.is_visible]
    
    @property
    def focus_object(self) -> Optional[VisualObject]:
        """Get the current focus object (what the tutor should emphasize)."""
        if self._focus_object_id:
            return self._objects.get(self._focus_object_id)
        return None
    
    def add_object(
        self,
        object_type: VisualObjectType,
        description: str,
        object_id: str = None,
        **properties
    ) -> VisualObject:
        """
        Add a new visual object to the state.
        Called AFTER Manim has rendered the object.
        """
        obj_id = object_id or str(uuid.uuid4())[:8]
        
        obj = VisualObject(
            object_id=obj_id,
            object_type=object_type,
            description=description,
            properties=properties,
            color=properties.get("color"),
            position=properties.get("position"),
            label=properties.get("label"),
            math_expression=properties.get("math_expression")
        )
        
        self._objects[obj_id] = obj
        return obj
    
    def remove_object(self, object_id: str) -> bool:
        """Mark an object as no longer visible."""
        if object_id in self._objects:
            self._objects[object_id].is_visible = False
            return True
        return False
    
    def clear_screen(self):
        """Clear all visible objects (scene transition)."""
        for obj in self._objects.values():
            obj.is_visible = False
    
    def set_focus(self, object_id: str):
        """Set the current focus object."""
        if object_id in self._objects:
            self._focus_object_id = object_id
    
    def clear_focus(self):
        """Clear the focus object."""
        self._focus_object_id = None
    
    def object_exists(self, object_id: str) -> bool:
        """Check if an object exists and is visible."""
        obj = self._objects.get(object_id)
        return obj is not None and obj.is_visible
    
    def get_state_for_tutor(self) -> Dict[str, Any]:
        """
        Generate the state context that will be injected into the tutor prompt.
        
        This is the ONLY source of truth for what the tutor can describe.
        """
        visible = self.visible_objects
        focus = self.focus_object
        
        return {
            "session_id": self.session_id,
            "current_scene_index": self._current_scene_index,
            "visible_object_count": len(visible),
            "objects": [
                {
                    "id": obj.object_id,
                    "type": obj.object_type.value,
                    "description": obj.to_description(),
                    "color": obj.color,
                    "label": obj.label,
                    "math": obj.math_expression
                }
                for obj in visible
            ],
            "focus_object": {
                "id": focus.object_id,
                "type": focus.object_type.value,
                "description": focus.to_description()
            } if focus else None,
            "can_describe": [obj.object_id for obj in visible]
        }
    
    def generate_visual_context_prompt(self) -> str:
        """
        Generate the visual context section for the tutor's system prompt.
        
        This explicitly lists what the tutor is ALLOWED to describe.
        """
        state = self.get_state_for_tutor()
        
        if not state["objects"]:
            return """
[VISUAL STATE: EMPTY SCREEN]
The screen is currently blank. No visual objects are rendered.
You may ONLY discuss what will be visualized next, NOT what it looks like.
Do NOT describe any visuals until they are confirmed as rendered.
"""
        
        lines = [
            "\n[CURRENT VISUAL STATE - YOU MAY ONLY DESCRIBE THESE OBJECTS]",
            f"Scene {state['current_scene_index'] + 1}",
            f"Visible objects: {state['visible_object_count']}",
            ""
        ]
        
        for i, obj in enumerate(state["objects"], 1):
            lines.append(f"{i}. [{obj['type'].upper()}] {obj['description']}")
            if obj.get("math"):
                lines.append(f"   Math: {obj['math']}")
            if obj.get("color"):
                lines.append(f"   Color: {obj['color']}")
        
        if state["focus_object"]:
            lines.append(f"\n[CURRENT FOCUS]: {state['focus_object']['description']}")
            lines.append("Emphasize this object in your explanation.")
        
        lines.append("\n[CONSTRAINT]: You may ONLY reference the objects listed above.")
        lines.append("Any visual not in this list DOES NOT EXIST on screen.")
        
        return "\n".join(lines)
    
    # Scene management for synchronized playback
    def load_scene_plan(self, scenes: List[Dict[str, Any]]):
        """Load a scene plan for synchronized playback."""
        self._scene_history = scenes
        self._current_scene_index = 0
        self.clear_screen()
    
    def advance_to_scene(self, scene_index: int) -> Dict[str, Any]:
        """
        Advance to a specific scene and update visual state.
        Returns the scene data for the tutor.
        """
        if 0 <= scene_index < len(self._scene_history):
            self._current_scene_index = scene_index
            scene = self._scene_history[scene_index]
            
            # Clear previous objects
            self.clear_screen()
            
            # Add objects from this scene
            self._populate_from_scene(scene)
            
            return scene
        return {}
    
    def _populate_from_scene(self, scene: Dict[str, Any]):
        """Populate visual state from a scene specification."""
        scene_type = scene.get("scene_type", "unknown")
        
        # Add appropriate objects based on scene type
        if scene_type == "graph_2d":
            # Add axes
            self.add_object(
                VisualObjectType.AXIS,
                "2D coordinate axes with x and y labels",
                "axes"
            )
            
            # Add the function curve
            func = scene.get("function", "x**2")
            self.add_object(
                VisualObjectType.CURVE,
                f"A curve showing the function y = {func}",
                "main_curve",
                math_expression=f"y = {func}",
                color=scene.get("color", "blue")
            )
            self.set_focus("main_curve")
            
            # Add derivative if shown
            if scene.get("show_derivative"):
                self.add_object(
                    VisualObjectType.CURVE,
                    "The derivative curve showing the rate of change",
                    "derivative_curve",
                    color="yellow"
                )
            
            # Add moving dot if present
            if scene.get("moving_dot"):
                start_x = scene.get("start_x", 0)
                self.add_object(
                    VisualObjectType.DOT,
                    f"A point moving along the curve, starting at x = {start_x}",
                    "moving_dot",
                    color="red",
                    position=[start_x, 0]
                )
                
        elif scene_type == "vector_arrows":
            vectors = scene.get("vectors", [])
            labels = scene.get("labels", [])
            
            for i, vec in enumerate(vectors):
                label = labels[i] if i < len(labels) else f"v{i+1}"
                self.add_object(
                    VisualObjectType.VECTOR,
                    f"A vector arrow pointing to ({vec[0]}, {vec[1]})",
                    f"vector_{i}",
                    label=label,
                    math_expression=label,
                    position=vec
                )
            
            if vectors:
                self.set_focus("vector_0")
                
        elif scene_type == "text_labels":
            text = scene.get("text", "")
            math_mode = scene.get("math_mode", False)
            
            obj_type = VisualObjectType.EQUATION if math_mode else VisualObjectType.TEXT
            self.add_object(
                obj_type,
                f"Text displaying: {text}",
                "main_text",
                math_expression=text if math_mode else None
            )
            self.set_focus("main_text")
            
        elif scene_type == "dots_paths":
            start = scene.get("start_point", [0, 0])
            end = scene.get("end_point", [1, 1])
            
            self.add_object(
                VisualObjectType.DOT,
                f"Starting point at ({start[0]}, {start[1]})",
                "start_dot",
                color="green",
                position=start
            )
            
            self.add_object(
                VisualObjectType.PATH,
                f"A path from ({start[0]}, {start[1]}) to ({end[0]}, {end[1]})",
                "main_path",
                color=scene.get("color", "yellow")
            )
            
            self.add_object(
                VisualObjectType.DOT,
                f"End point at ({end[0]}, {end[1]})",
                "end_dot",
                color="red",
                position=end
            )
            
            self.set_focus("main_path")


# Global session storage
_visual_states: Dict[str, VisualState] = {}


def get_visual_state(session_id: str) -> VisualState:
    """Get or create visual state for a session."""
    if session_id not in _visual_states:
        _visual_states[session_id] = VisualState(session_id)
    return _visual_states[session_id]


def clear_visual_state(session_id: str):
    """Clear visual state for a session."""
    if session_id in _visual_states:
        del _visual_states[session_id]
