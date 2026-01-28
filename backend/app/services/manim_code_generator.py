"""
Manim Code Generator Service - Stage 2 of the Two-Stage Pipeline
Converts synchronized scripts into executable Manim scene specifications.
"""
from typing import Dict, Any, Optional, List
import json
import random
from app.services.topic_classifier import LLMClient


class ManimCodeGenerator:
    """
    Stage 2: Converts script into Manim-compatible scene specifications.
    Takes the synchronized script and generates exact animation parameters.
    """
    
    # Diverse function library for variety
    FUNCTION_LIBRARY = {
        "polynomial": [
            "x**2", "x**3", "-x**2 + 4", "0.5*x**2 - 2*x + 1", 
            "x**4 - 4*x**2", "(x-1)*(x+1)*(x-2)", "x**3 - 3*x"
        ],
        "trigonometric": [
            "sin(x)", "cos(x)", "tan(x)/5", "sin(2*x)", "cos(x/2)",
            "sin(x)*cos(x)", "sin(x)**2", "2*sin(x) + cos(2*x)"
        ],
        "exponential": [
            "exp(-x**2)", "exp(x)/10", "exp(-abs(x))", "2**x/10",
            "exp(-x)*sin(5*x)", "1/(1+exp(-x))"  # sigmoid
        ],
        "logarithmic": [
            "log(x+1)", "log(abs(x)+1)", "-log(x+0.1)", "x*log(x+1)"
        ],
        "rational": [
            "1/(1+x**2)", "x/(1+x**2)", "1/(x**2+0.1)", "(x**2-1)/(x**2+1)"
        ],
        "absolute": [
            "abs(x)", "abs(x-2) + abs(x+2)", "-abs(x) + 3", "abs(sin(x))"
        ],
        "composite": [
            "sin(x) + 0.5*x", "x**2 * exp(-x**2)", "cos(x) * exp(-x**2/4)",
            "sin(x**2)", "x * sin(1/x)" if False else "sin(x)/x"  # sinc-like
        ]
    }
    
    # Color palettes for variety
    COLOR_PALETTES = [
        {"primary": "#FFD700", "secondary": "#4169E1", "accent": "#32CD32"},  # Gold/Blue/Green
        {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#45B7D1"},  # Coral/Teal/Sky
        {"primary": "#A855F7", "secondary": "#EC4899", "accent": "#06B6D4"},  # Purple/Pink/Cyan
        {"primary": "#22C55E", "secondary": "#F59E0B", "accent": "#EF4444"},  # Green/Orange/Red
        {"primary": "#3B82F6", "secondary": "#8B5CF6", "accent": "#F472B6"},  # Blue/Violet/Pink
        {"primary": "#14B8A6", "secondary": "#F97316", "accent": "#6366F1"},  # Teal/Orange/Indigo
    ]

    SCENE_GENERATION_PROMPT = """You are an expert Manim animator. Convert this script scene into precise Manim parameters.

    SCRIPT SCENE:
    Scene Number: {scene_number}
    Voiceover: "{voiceover}"
    Visual Type: {visual_type}
    Visual Description: {visual_description}
    Visual Elements: {visual_elements}
    Duration: {duration_seconds} seconds

    AVAILABLE SCENE TYPES (Choose the best fit):

    1. "graph_2d" - Plots, curves, calculus.
       REQUIRED: function (Python syntax e.g. "x**2")
       Optional: x_range, y_range, show_derivative, moving_dot

    2. "graph_3d" - 3D Surfaces, Terrain.
       REQUIRED: function (Python syntax e.g. "cos(x) + sin(y)")
       Optional: u_range, v_range, rotation_speed

    3. "vector_arrows" - Vectors, Gradients, Fields.
       REQUIRED: vectors (list of [x,y])
       Optional: labels, origin

    4. "geometry_shapes" - Shapes, Polygons, Boolean Ops.
       REQUIRED: shapes (list of "Square", "Circle", etc.)
       Optional: morph (true/false)

    5. "physics_sim" - Pendulums, Gravity, Collisions.
       REQUIRED: sim_type ("pendulum", "gravity", "collision")

    6. "media_display" - Images, Icons.
       REQUIRED: media_type ("image", "svg"), path/url

    7. "dots_paths" - Tracing paths.
    8. "text_labels" - Key text/math.

    CRITICAL RULES:
    1. scene_type MUST be valid (see above).
    2. For graph_2d/3d: function MUST use Python/SymPy syntax (** for power).

    Return ONLY valid JSON:
    {{
        "scene_type": "valid_type",
        "title": "short title",
        "narration": "exact voiceover",
        "color": "hex",
        ...type specific params...
    }}"""

    def __init__(self):
        self.llm = LLMClient()
        self.used_functions = set()
        self.color_index = 0
    
    async def generate_scenes(self, script: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert a complete script into Manim scene specifications.
        Ensures variety and synchronization.
        """
        scenes = []
        script_scenes = script.get("scenes", [])
        
        for i, script_scene in enumerate(script_scenes):
            # Get next color palette for variety
            colors = self.COLOR_PALETTES[self.color_index % len(self.COLOR_PALETTES)]
            self.color_index += 1
            
            try:
                manim_scene = await self._generate_single_scene(script_scene, colors)
                if manim_scene:
                    scenes.append(manim_scene)
            except Exception as e:
                print(f"Scene {i+1} generation failed: {e}")
                # Generate fallback scene
                fallback = self._generate_fallback_scene(script_scene, colors, i)
                scenes.append(fallback)
        
        return scenes
    
    async def _generate_single_scene(
        self, 
        script_scene: Dict[str, Any], 
        colors: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Generate Manim parameters for a single scene."""
        
        if not self.llm.provider:
            return self._generate_fallback_scene(script_scene, colors, script_scene.get("scene_number", 0))
        
        prompt = self.SCENE_GENERATION_PROMPT.format(
            scene_number=script_scene.get("scene_number", 1),
            voiceover=script_scene.get("voiceover", ""),
            visual_type=script_scene.get("visual_type", "graph_2d"),
            visual_description=script_scene.get("visual_description", ""),
            visual_elements=json.dumps(script_scene.get("visual_elements", {})),
            duration_seconds=script_scene.get("duration_seconds", 12),
            colors=json.dumps(colors)
        )
        
        try:
            # Use chat_code for code generation (uses Qwen Coder if available)
            content = await self.llm.chat_code(prompt, temperature=0.3, max_tokens=1500)
            
            if not content:
                return self._generate_fallback_scene(script_scene, colors, script_scene.get("scene_number", 0))
            
            return self._parse_scene_response(content, script_scene, colors)
            
        except Exception as e:
            print(f"LLM scene generation error: {e}")
            return self._generate_fallback_scene(script_scene, colors, script_scene.get("scene_number", 0))
    
    def _parse_scene_response(
        self, 
        content: str, 
        script_scene: Dict[str, Any],
        colors: Dict[str, str]
    ) -> Dict[str, Any]:
        """Parse LLM response into Manim scene spec."""
        try:
            # Clean markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            scene = json.loads(content.strip())
            
            # Ensure narration matches voiceover
            scene["narration"] = script_scene.get("voiceover", scene.get("narration", ""))
            
            # Validate scene type - ONLY 4 valid types
            # Validate scene type
            valid_types = [
                "graph_2d", "graph_3d", "vector_arrows", "dots_paths", 
                "text_labels", "geometry_shapes", "physics_sim", "media_display"
            ]
            if scene.get("scene_type") not in valid_types:
                # Map invalid types to valid ones
                invalid_type = scene.get("scene_type", "")
                type_mapping = {
                    "transformation": "geometry_shapes",
                    "equation_sequence": "text_labels",
                    "comparison": "graph_2d",
                    "vector_field": "vector_arrows",
                    "3d_plot": "graph_3d"
                }
                scene["scene_type"] = type_mapping.get(invalid_type, "graph_2d")
            
            # Fix show_derivative if it's not a boolean
            if "show_derivative" in scene and not isinstance(scene["show_derivative"], bool):
                scene["show_derivative"] = False
            
            # Ensure text_labels has required 'text' field
            if scene["scene_type"] == "text_labels" and "text" not in scene:
                # Use title or narration as text
                scene["text"] = scene.get("title", scene.get("narration", "")[:100])
            
            # Add colors
            if "color" not in scene:
                scene["color"] = colors["primary"]
            
            return scene
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Parse error: {e}")
            return self._generate_fallback_scene(script_scene, colors, script_scene.get("scene_number", 0))
    
    def _generate_fallback_scene(
        self, 
        script_scene: Dict[str, Any], 
        colors: Dict[str, str],
        index: int
    ) -> Dict[str, Any]:
        """Generate a fallback scene with variety."""
        visual_type = script_scene.get("visual_type", "graph_2d")
        voiceover = script_scene.get("voiceover", "")
        
        # Map visual types to VALID scene types only
        type_mapping = {
            "graph_2d": "graph_2d",
            "graph_3d": "graph_3d",
            "vector_field": "vector_arrows",
            "transformation": "geometry_shapes",
            "equation_morph": "text_labels",
            "comparison": "graph_2d",
            "diagram": "vector_arrows",
            "particle_motion": "physics_sim"
        }
        
        scene_type = type_mapping.get(visual_type, "graph_2d")
        
        # Select varied function based on index
        func_categories = list(self.FUNCTION_LIBRARY.keys())
        category = func_categories[index % len(func_categories)]
        functions = self.FUNCTION_LIBRARY[category]
        func = functions[index % len(functions)]
        
        # Track used functions to avoid repetition
        attempts = 0
        while func in self.used_functions and attempts < 10:
            category = random.choice(func_categories)
            func = random.choice(self.FUNCTION_LIBRARY[category])
            attempts += 1
        self.used_functions.add(func)
        
        if scene_type == "graph_2d":
            return {
                "scene_type": "graph_2d",
                "title": script_scene.get("visual_description", "")[:40],
                "narration": voiceover,
                "function": func,
                "x_range": [-5, 5, 1],
                "y_range": [-4, 8, 1],
                "moving_dot": index % 3 == 0,
                "show_derivative": index % 4 == 1,
                "show_tangent": index % 5 == 2,
                "color": colors["primary"]
            }
        elif scene_type == "vector_arrows":
            # Generate varied vectors
            num_vectors = min(3 + (index % 3), 6)
            vectors = []
            for j in range(num_vectors):
                angle = (j * 360 / num_vectors + index * 30) % 360
                import math
                x = round(2 * math.cos(math.radians(angle)), 1)
                y = round(2 * math.sin(math.radians(angle)), 1)
                vectors.append([x, y])
            
            return {
                "scene_type": "vector_arrows",
                "title": script_scene.get("visual_description", "")[:40],
                "narration": voiceover,
                "vectors": vectors,
                "labels": [f"\\\\vec{{v}}_{{{j+1}}}" for j in range(len(vectors))],
                "show_components": index % 2 == 0,
                "color": colors["primary"]
            }
        elif scene_type == "dots_paths":
            path_types = ["line", "curve", "spiral", "bezier"]
            return {
                "scene_type": "dots_paths",
                "title": script_scene.get("visual_description", "")[:40],
                "narration": voiceover,
                "start_point": [-3 + (index % 3), 2 - (index % 2)],
                "end_point": [3 - (index % 2), -1 + (index % 3)],
                "path_type": path_types[index % len(path_types)],
                "num_dots": 2 + (index % 3),
                "color": colors["primary"]
            }
        elif scene_type == "text_labels":
            # Extract math from visual elements if available
            visual_elements = script_scene.get("visual_elements", {})
            math_exprs = visual_elements.get("math_expressions", [])
            text = math_exprs[0] if math_exprs else script_scene.get("visual_description", "Key Concept")
            
            return {
                "scene_type": "text_labels",
                "title": script_scene.get("visual_description", "")[:40],
                "narration": voiceover,
                "text": text,
                "math_mode": True if "=" in text or "\\" in text else False,
                "is_intro": index == 0,
                "color": colors["primary"]
            }
        elif scene_type == "graph_3d":
             return {
                "scene_type": "graph_3d",
                "title": script_scene.get("visual_description", "")[:40],
                "narration": voiceover,
                "function": "cos(x) + sin(y)" if index % 2 == 0 else "x**2 + y**2",
                "u_range": [-2, 2],
                "v_range": [-2, 2],
                "color": colors["primary"]
            }
        elif scene_type == "geometry_shapes":
             return {
                "scene_type": "geometry_shapes",
                "title": script_scene.get("visual_description", "")[:40],
                "narration": voiceover,
                "shapes": ["Square", "Circle"],
                "morph": True,
                "color": colors["primary"]
            }
        elif scene_type == "physics_sim":
             return {
                "scene_type": "physics_sim",
                "title": script_scene.get("visual_description", "")[:40],
                "narration": voiceover,
                "sim_type": "pendulum",
                "color": colors["primary"]
            }
        elif scene_type == "media_display":
             return {
                "scene_type": "text_labels", # Fallback for media is safely text
                "title": "Media Placeholder",
                "narration": voiceover,
                "text": "Image: " + script_scene.get("visual_description", "")[:30],
                "color": colors["primary"]
            }
        else:
            # Default to graph_2d
            return {
                "scene_type": "graph_2d",
                "title": script_scene.get("visual_description", "")[:40],
                "narration": voiceover,
                "function": func,
                "x_range": [-5, 5, 1],
                "y_range": [-4, 8, 1],
                "color": colors["primary"]
            }
