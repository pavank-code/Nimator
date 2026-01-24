from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from enum import Enum


class SceneType(str, Enum):
    GRAPH_2D = "graph_2d"
    VECTOR_ARROWS = "vector_arrows"
    DOTS_PATHS = "dots_paths"
    TEXT_LABELS = "text_labels"


class BaseSceneSchema(BaseModel):
    """Base schema for all scene types."""
    scene_type: SceneType
    title: Optional[str] = None
    narration: str = Field(..., max_length=500)


class Graph2DSceneSchema(BaseSceneSchema):
    """Schema for 2D graph scenes."""
    scene_type: SceneType = SceneType.GRAPH_2D
    function: str = Field(..., description="Math function in Python/SymPy format")
    x_range: Optional[List[float]] = Field(default=[-4, 4, 1])
    y_range: Optional[List[float]] = Field(default=[-2, 10, 1])
    show_derivative: bool = False
    moving_dot: bool = False
    start_x: Optional[float] = None


class VectorArrowsSceneSchema(BaseSceneSchema):
    """Schema for vector arrow scenes."""
    scene_type: SceneType = SceneType.VECTOR_ARROWS
    vectors: List[List[float]] = Field(..., min_length=1, max_length=10)
    labels: Optional[List[str]] = None
    origin: Optional[List[float]] = Field(default=[0, 0])
    colors: Optional[List[str]] = None


class DotsPathsSceneSchema(BaseSceneSchema):
    """Schema for dots and paths scenes."""
    scene_type: SceneType = SceneType.DOTS_PATHS
    start_point: List[float] = Field(..., min_length=2, max_length=2)
    end_point: List[float] = Field(..., min_length=2, max_length=2)
    path_type: str = Field(default="line", pattern="^(line|curve|parabola|bezier)$")
    color: Optional[str] = None


class TextLabelsSceneSchema(BaseSceneSchema):
    """Schema for text and label scenes."""
    scene_type: SceneType = SceneType.TEXT_LABELS
    text: str = Field(..., max_length=500)
    math_mode: bool = False
    position: Optional[List[float]] = None
    font_size: Optional[int] = None


# Union of all scene types
SceneSchema = Union[
    Graph2DSceneSchema,
    VectorArrowsSceneSchema,
    DotsPathsSceneSchema,
    TextLabelsSceneSchema
]


class VideoPlanSchema(BaseModel):
    """Schema for a complete video plan."""
    topic: str = Field(..., max_length=100)
    summary: Optional[str] = None
    scenes: List[Dict[str, Any]] = Field(..., min_length=3, max_length=6)