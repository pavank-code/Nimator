from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class SceneType(str, Enum):
    GRAPH_2D = "graph_2d"
    VECTOR_ARROWS = "vector_arrows"
    DOTS_PATHS = "dots_paths"
    TEXT_LABELS = "text_labels"


class Scene(BaseModel):
    """Base model for a scene."""
    scene_type: SceneType
    title: Optional[str] = None
    narration: str = Field(..., max_length=500)
    
    # graph_2d fields
    function: Optional[str] = None
    x_range: Optional[List[float]] = None
    y_range: Optional[List[float]] = None
    show_derivative: Optional[bool] = False
    moving_dot: Optional[bool] = False
    start_x: Optional[float] = None
    
    # vector_arrows fields
    vectors: Optional[List[List[float]]] = None
    labels: Optional[List[str]] = None
    origin: Optional[List[float]] = None
    colors: Optional[List[str]] = None
    
    # dots_paths fields
    start_point: Optional[List[float]] = None
    end_point: Optional[List[float]] = None
    path_type: Optional[str] = None
    
    # text_labels fields
    text: Optional[str] = None
    math_mode: Optional[bool] = False
    position: Optional[List[float]] = None
    font_size: Optional[int] = None


class ScenePlan(BaseModel):
    """Model for a complete scene plan."""
    topic: str
    summary: Optional[str] = None
    scenes: List[Dict[str, Any]] = Field(..., min_length=3, max_length=6)