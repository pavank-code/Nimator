from typing import Dict, List

# Scene templates for rendering different types of scenes in the visual explainer generator.

def create_graph_2d_scene(function: str, moving_dot: bool, narration: str) -> Dict:
    return {
        "scene_type": "graph_2d",
        "axes": True,
        "function": function,
        "moving_dot": moving_dot,
        "narration": narration
    }

def create_vector_arrow_scene(arrow: str, narration: str) -> Dict:
    return {
        "scene_type": "vector_arrow",
        "arrow": arrow,
        "narration": narration
    }

def create_dots_paths_scene(dots: List[Dict], narration: str) -> Dict:
    return {
        "scene_type": "dots_paths",
        "dots": dots,
        "narration": narration
    }

def create_text_label_scene(text: str, position: Dict, narration: str) -> Dict:
    return {
        "scene_type": "text_label",
        "text": text,
        "position": position,
        "narration": narration
    }