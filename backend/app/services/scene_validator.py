from pydantic import BaseModel, ValidationError, field_validator
from typing import List, Optional, Dict, Any, Union


class Graph2DScene(BaseModel):
    scene_type: str = "graph_2d"
    title: Optional[str] = None
    function: str = "x**2"
    show_derivative: bool = False
    moving_dot: bool = False
    start_x: Optional[float] = None
    x_range: Optional[List[float]] = None
    y_range: Optional[List[float]] = None
    narration: str
    
    @field_validator('function')
    @classmethod
    def validate_function(cls, v):
        # Basic validation - ensure it's a valid expression
        if not v or len(v) > 100:
            raise ValueError("Invalid function expression")
        return v


class VectorArrowsScene(BaseModel):
    scene_type: str = "vector_arrows"
    title: Optional[str] = None
    vectors: List[List[float]]
    labels: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    origin: Optional[List[float]] = None
    narration: str
    
    @field_validator('vectors')
    @classmethod
    def validate_vectors(cls, v):
        if not v or len(v) > 10:
            raise ValueError("Must have 1-10 vectors")
        for vec in v:
            if len(vec) != 2:
                raise ValueError("Each vector must have 2 components [x, y]")
        return v


class DotsPathsScene(BaseModel):
    scene_type: str = "dots_paths"
    title: Optional[str] = None
    start_point: List[float] = [-3, 0]
    end_point: List[float] = [3, 0]
    path_type: str = "line"  # line, curve, parabola
    color: Optional[str] = None
    narration: str
    
    @field_validator('path_type')
    @classmethod
    def validate_path_type(cls, v):
        allowed = ["line", "curve", "parabola", "bezier", "spiral", "oscillate"]
        if v not in allowed:
            return "line"  # Default to line
        return v


class TextLabelsScene(BaseModel):
    scene_type: str = "text_labels"
    title: Optional[str] = None
    text: str
    math_mode: bool = False
    position: Optional[List[float]] = None
    font_size: Optional[int] = None
    color: Optional[str] = None
    narration: str
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or len(v) > 500:
            raise ValueError("Text must be 1-500 characters")
        return v


# Scene type mapping
SCENE_VALIDATORS = {
    "graph_2d": Graph2DScene,
    "vector_arrows": VectorArrowsScene,
    "dots_paths": DotsPathsScene,
    "text_labels": TextLabelsScene
}


def validate_scene(scene_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validate a single scene against its schema.
    Returns the validated scene dict or None if invalid.
    """
    try:
        scene_type = scene_data.get("scene_type", "text_labels")
        
        if scene_type not in SCENE_VALIDATORS:
            print(f"Unknown scene type: {scene_type}, defaulting to text_labels")
            scene_type = "text_labels"
            scene_data["scene_type"] = scene_type
        
        # Ensure narration exists
        if "narration" not in scene_data:
            scene_data["narration"] = "..."
        
        validator = SCENE_VALIDATORS[scene_type]
        validated = validator(**scene_data)
        return validated.model_dump()
        
    except ValidationError as e:
        print(f"Scene validation error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected validation error: {e}")
        return None


def validate_scenes(scenes: Union[List[Dict], Dict]) -> Optional[List[Dict[str, Any]]]:
    """
    Validate a list of scenes.
    Returns validated scenes if at least 3 are valid, otherwise None.
    """
    # Handle case where scenes is a dict with a "scenes" key
    if isinstance(scenes, dict):
        scenes = scenes.get("scenes", [])
    
    if not scenes or not isinstance(scenes, list):
        return None
    
    valid_scenes = []
    for scene in scenes:
        validated = validate_scene(scene)
        if validated:
            valid_scenes.append(validated)
    
    # Need at least 3 valid scenes
    if len(valid_scenes) >= 3:
        return valid_scenes  # Return all valid scenes, no cap
    
    return None


class ValidationResult:
    """Result object for scene validation."""
    def __init__(self, is_valid: bool, scenes: List[Dict] = None, errors: List[str] = None):
        self.is_valid = is_valid
        self.scenes = scenes or []
        self.errors = errors or []