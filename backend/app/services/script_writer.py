"""
Script Writer Service - Stage 1 of the Two-Stage Pipeline
Generates synchronized educational scripts with detailed animation descriptions.
"""
from typing import Dict, Any, Optional, List
import json
from app.services.topic_classifier import LLMClient


class ScriptWriter:
    """
    Stage 1: Generates a complete synchronized script.
    The script includes:
    - Voiceover text (what to say)
    - Animation descriptions (what to show, synchronized with voiceover)
    - Scene breakdown with timing
    - Visual variety specifications
    """
    
    SCRIPT_GENERATION_PROMPT = """You are a world-class educational content creator like 3Blue1Brown.
Your task: Write a COMPLETE, SYNCHRONIZED educational video script.

CRITICAL REQUIREMENTS:
1. VIDEO LENGTH: Must be 6-8 minutes (360-480 seconds)
2. SCENE COUNT: 25-35 scenes (each ~10-15 seconds with voiceover)
3. SYNCHRONIZATION: Animation MUST match what's being explained
4. VARIETY: Use different visual types - NO repetitive animations

VISUAL VARIETY REQUIREMENTS (CRITICAL - NO REPETITION):
- Use DIFFERENT graph types: parabolas, sine waves, exponentials, logarithms, cubic functions, absolute value, step functions
- Use DIFFERENT coordinate systems: 2D cartesian, polar, 3D spaces
- Use DIFFERENT animation styles: drawing curves, transforming shapes, moving dots, growing vectors, morphing equations
- Use DIFFERENT color schemes for each scene
- Each scene should feel FRESH and DIFFERENT

USER TOPIC: "{prompt}"

SCRIPT FORMAT - Return valid JSON:
{{
    "title": "Video Title",
    "total_duration_seconds": <number 360-480>,
    "summary": "One paragraph description",
    "scenes": [
        {{
            "scene_number": 1,
            "duration_seconds": <10-15>,
            "voiceover": "Exactly what the narrator says (60-100 words, natural speech)",
            "visual_description": "Detailed description of what's shown on screen",
            "visual_type": "one of: graph_2d, graph_3d, vector_field, transformation, equation_morph, comparison, diagram, particle_motion",
            "visual_elements": {{
                "primary": "main visual element description",
                "secondary": "supporting elements",
                "animation_sequence": ["step 1", "step 2", "step 3"],
                "math_expressions": ["latex expression 1", "latex expression 2"],
                "colors": {{"primary": "#hex", "secondary": "#hex", "accent": "#hex"}}
            }},
            "sync_points": [
                {{"time": "0:00", "voiceover_word": "first key word", "visual_action": "what happens visually"}},
                {{"time": "0:05", "voiceover_word": "second key word", "visual_action": "what happens visually"}}
            ],
            "transition_to_next": "How this scene connects to the next"
        }}
    ]
}}

CONTENT STRUCTURE (25-35 scenes):
1. HOOK (2-3 scenes): Grab attention with an intriguing question or surprising visual
2. FOUNDATION (5-7 scenes): Build intuition with simple, clear visuals
3. CORE EXPLANATION (10-15 scenes): Deep dive with varied visualizations
4. ADVANCED INSIGHTS (5-7 scenes): Show connections and deeper patterns
5. SUMMARY (2-3 scenes): Recap key insights with memorable visuals

CRITICAL RULES:
1. NEVER repeat the same animation type in consecutive scenes
2. ALWAYS sync voiceover with visual - when you say "gradient", show the gradient
3. Use SPECIFIC math functions - not just "parabola" every time
4. Vary camera angles and visual perspectives
5. Include smooth transitions between scenes
6. Make each scene visually distinct and memorable

Generate the complete script now:"""

    # Compact prompt for 30-second sample videos
    SAMPLE_SCRIPT_PROMPT = """You are a world-class educational content creator like 3Blue1Brown.
Create a SHORT, IMPACTFUL 30-second sample video script.

REQUIREMENTS:
1. DURATION: Exactly 30 seconds (3 scenes, ~10 seconds each)
2. MAXIMUM VISUAL IMPACT: Each scene must be stunning and different
3. CLEAR EXPLANATION: Concise but insightful narration
4. VARIETY: Use 3 different visual types

USER TOPIC: "{prompt}"

Return valid JSON:
{{
    "title": "Video Title",
    "total_duration_seconds": 30,
    "summary": "Brief description",
    "scenes": [
        {{
            "scene_number": 1,
            "duration_seconds": 10,
            "voiceover": "Engaging intro (20-30 words)",
            "visual_description": "Striking opening visual",
            "visual_type": "text_labels",
            "visual_elements": {{
                "primary": "Title or key concept",
                "math_expressions": ["LaTeX formula"],
                "colors": {{"primary": "#FFD700"}}
            }}
        }},
        {{
            "scene_number": 2,
            "duration_seconds": 10,
            "voiceover": "Core explanation (20-30 words)",
            "visual_description": "Dynamic graph animation",
            "visual_type": "graph_2d",
            "visual_elements": {{
                "primary": "Function visualization",
                "function": "sin(x)",
                "colors": {{"primary": "#3B82F6"}}
            }}
        }},
        {{
            "scene_number": 3,
            "duration_seconds": 10,
            "voiceover": "Key insight (20-30 words)",
            "visual_description": "Vector or path animation",
            "visual_type": "vector_arrows",
            "visual_elements": {{
                "primary": "Direction visualization",
                "colors": {{"primary": "#22C55E"}}
            }}
        }}
    ]
}}

Generate the script:"""

    def __init__(self):
        self.llm = LLMClient()
    
    async def generate_script(self, prompt: str, sample_mode: bool = False, duration_seconds: int = 180) -> Dict[str, Any]:
        """
        Generate a complete synchronized script from a user prompt.
        
        Args:
            prompt: User's topic/question
            sample_mode: If True, generates a short sample video
            duration_seconds: Target video duration in seconds
        
        Returns structured script with voiceover and animation specifications.
        """
        # Short videos (under 60s) use sample mode
        if duration_seconds <= 60:
            return await self._generate_sample_script(prompt, duration_seconds)
        
        if not self.llm.provider:
            return self._generate_fallback_script(prompt, duration_seconds)
        
        # Calculate scene count based on duration (~12 seconds per scene)
        target_scenes = max(5, duration_seconds // 12)
        
        try:
            # Dynamic prompt based on duration
            dynamic_prompt = self.SCRIPT_GENERATION_PROMPT.replace(
                "VIDEO LENGTH: Must be 6-8 minutes (360-480 seconds)",
                f"VIDEO LENGTH: Must be approximately {duration_seconds} seconds ({duration_seconds // 60} minutes)"
            ).replace(
                "SCENE COUNT: 25-35 scenes",
                f"SCENE COUNT: {target_scenes} scenes (each ~10-15 seconds with voiceover)"
            )
            
            content = await self.llm.chat(
                dynamic_prompt.format(prompt=prompt),
                temperature=0.7,
                max_tokens=12000
            )
            
            if not content:
                return self._generate_fallback_script(prompt, duration_seconds)
            
            return self._parse_script_response(content, prompt)
            
        except Exception as e:
            print(f"Script generation failed: {e}")
            return self._generate_fallback_script(prompt, duration_seconds)
    
    async def _generate_sample_script(self, prompt: str, duration_seconds: int = 30) -> Dict[str, Any]:
        """Generate a short sample video with maximum visual impact."""
        num_scenes = max(2, duration_seconds // 10)
        print(f"🎬 Generating {duration_seconds}-second sample video script ({num_scenes} scenes)...")
        
        if not self.llm.provider:
            return self._generate_sample_fallback(prompt, num_scenes)
        
        try:
            # Modify prompt for specific duration
            modified_prompt = self.SAMPLE_SCRIPT_PROMPT.replace(
                "DURATION: Exactly 30 seconds (3 scenes, ~10 seconds each)",
                f"DURATION: Exactly {duration_seconds} seconds ({num_scenes} scenes, ~10 seconds each)"
            )
            
            content = await self.llm.chat(
                modified_prompt.format(prompt=prompt),
                temperature=0.8,
                max_tokens=3000
            )
            
            if not content:
                return self._generate_sample_fallback(prompt, num_scenes)
            
            return self._parse_script_response(content, prompt)
            
        except Exception as e:
            print(f"Sample script generation failed: {e}")
            return self._generate_sample_fallback(prompt, num_scenes)
    
    def _generate_sample_fallback(self, prompt: str, num_scenes: int = 3) -> Dict[str, Any]:
        """Generate a high-quality sample fallback with specified number of scenes."""
        duration = num_scenes * 10
        
        base_scenes = [
            {
                "scene_number": 1,
                "duration_seconds": 10,
                "voiceover": f"Welcome! Today we're exploring {prompt}. This concept opens up fascinating possibilities.",
                "visual_description": "Animated title with glowing symbols",
                "visual_type": "text_labels",
                "visual_elements": {
                    "primary": prompt[:30],
                    "math_expressions": ["f(x)"],
                    "colors": {"primary": "#FFD700"}
                }
            },
            {
                "scene_number": 2,
                "duration_seconds": 10,
                "voiceover": "Watch how this transforms. Notice the smooth curve and how it changes at every point.",
                "visual_description": "Dynamic function visualization",
                "visual_type": "graph_2d",
                "visual_elements": {
                    "primary": "Animated function",
                    "function": "sin(x)",
                    "show_derivative": True,
                    "moving_dot": True,
                    "colors": {"primary": "#3B82F6"}
                }
            },
            {
                "scene_number": 3,
                "duration_seconds": 10,
                "voiceover": "These vectors show the direction of change. Each arrow represents the rate at that point.",
                "visual_description": "Vector field showing directions",
                "visual_type": "vector_arrows",
                "visual_elements": {
                    "primary": "Direction vectors",
                    "vectors": [[1, 2], [-1, 1], [2, -1], [0, 2]],
                    "colors": {"primary": "#22C55E"}
                }
            },
            {
                "scene_number": 4,
                "duration_seconds": 10,
                "voiceover": "As we trace this path, we can see the underlying pattern emerge clearly.",
                "visual_description": "Tracing a curved path",
                "visual_type": "dots_paths",
                "visual_elements": {
                    "primary": "Path trace",
                    "start_point": [-2, 0],
                    "end_point": [2, 0],
                    "path_type": "curve",
                    "colors": {"primary": "#A855F7"}
                }
            },
            {
                "scene_number": 5,
                "duration_seconds": 10,
                "voiceover": "This exponential curve shows how quickly values can grow or decay.",
                "visual_description": "Exponential function",
                "visual_type": "graph_2d",
                "visual_elements": {
                    "primary": "Exponential growth",
                    "function": "exp(-x**2)",
                    "colors": {"primary": "#F59E0B"}
                }
            },
            {
                "scene_number": 6,
                "duration_seconds": 10,
                "voiceover": "And here we see the relationship between multiple variables working together.",
                "visual_description": "Multiple function comparison",
                "visual_type": "graph_2d",
                "visual_elements": {
                    "primary": "Combined view",
                    "function": "cos(x)",
                    "colors": {"primary": "#EC4899"}
                }
            }
        ]
        
        scenes = base_scenes[:num_scenes]
        for i, scene in enumerate(scenes):
            scene["scene_number"] = i + 1
        
        return {
            "title": f"Understanding {prompt[:40]}",
            "total_duration_seconds": duration,
            "summary": f"A visual introduction to {prompt}",
            "scenes": scenes
        }
    
    def _parse_script_response(self, content: str, prompt: str) -> Dict[str, Any]:
        """Parse LLM response into structured script."""
        try:
            # Clean markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            script = json.loads(content.strip())
            
            # Validate and enhance
            if "scenes" not in script:
                raise ValueError("Missing scenes")
            
            # Ensure each scene has required fields
            for i, scene in enumerate(script["scenes"]):
                scene["scene_number"] = i + 1
                if "voiceover" not in scene:
                    scene["voiceover"] = ""
                if "visual_type" not in scene:
                    scene["visual_type"] = "graph_2d"
                if "visual_description" not in scene:
                    scene["visual_description"] = ""
                if "visual_elements" not in scene:
                    scene["visual_elements"] = {}
                if "duration_seconds" not in scene:
                    scene["duration_seconds"] = 12
            
            return script
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to parse script: {e}")
            return self._generate_fallback_script(prompt, 180)
    
    def _generate_fallback_script(self, prompt: str, duration_seconds: int = 180) -> Dict[str, Any]:
        """Generate a comprehensive fallback script based on duration."""
        # Calculate number of scenes (~12 seconds per scene)
        num_scenes = max(5, min(30, duration_seconds // 12))
        
        # Create varied scenes for educational content
        visual_types = [
            "text_labels", "graph_2d", "vector_arrows", "graph_2d", "dots_paths",
            "graph_2d", "vector_arrows", "text_labels", "graph_2d", "dots_paths",
            "graph_2d", "vector_arrows", "graph_2d", "text_labels", "dots_paths",
            "graph_2d", "vector_arrows", "graph_2d", "dots_paths", "text_labels"
        ]
        
        functions = [
            ("x**2", "parabola"), ("np.sin(x)", "sine wave"), 
            ("np.exp(x)", "exponential"), ("np.log(x+1)", "logarithm"),
            ("x**3", "cubic"), ("np.cos(x)", "cosine"), 
            ("np.tan(x)", "tangent"), ("np.abs(x)", "absolute value"),
            ("x**2 - 4", "shifted parabola"), ("np.sin(2*x)", "fast sine"),
            ("2**x", "exponential growth"), ("1/(x+0.5)", "hyperbola"),
            ("x**3 - x", "s-curve"), ("np.sin(x)*x", "damped sine"),
            ("x**4 - x**2", "w-curve"), ("np.exp(-x**2)", "bell curve"),
            ("np.floor(x)", "step function"), ("x - np.sin(x)", "cycloid-like"),
            ("np.sqrt(np.abs(x))", "square root"), ("np.arctan(x)", "arctangent")
        ]
        
        colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#9b59b6", "#f39c12",
            "#1abc9c", "#e67e22", "#34495e", "#16a085", "#c0392b",
            "#27ae60", "#8e44ad", "#d35400", "#2980b9", "#7f8c8d",
            "#f1c40f", "#1abc9c", "#9b59b6", "#3498db", "#e74c3c"
        ]
        
        voiceovers = [
            f"Welcome to our exploration of {prompt}. This is a fundamental concept that appears throughout mathematics and science. Let's begin by building an intuition for what this really means.",
            "To understand this concept deeply, we need to visualize it. Watch carefully as we draw this function and observe how it behaves across different values of x.",
            "Now let's think about the direction of change. At every point on this curve, there's an associated vector showing which way we're heading.",
            "Notice how the curve changes its behavior at different regions. The rate of change varies dramatically as we move along.",
            "Let's trace the path of a point moving along this curve. Watch how its position changes over time.",
            "Here's another function with a completely different character. Compare how it behaves to what we saw before.",
            "The vectors here tell a different story. See how the direction and magnitude shift as we explore the domain.",
            "Let's pause and summarize what we've learned so far. These key insights will be essential as we go deeper.",
            "Now we encounter a more complex example. This function combines multiple behaviors in interesting ways.",
            "Watch as we trace this path. The motion reveals patterns that aren't obvious from the static curve.",
            "This transformation shows us something profound about the relationship between these mathematical objects.",
            "The vectors here form a beautiful pattern. Each arrow represents the instantaneous direction of change.",
            "As we examine this curve, notice the critical points where the behavior changes dramatically.",
            "Let's connect these ideas back to our original question. The relationship becomes clearer now.",
            "This path shows us another perspective on the same underlying mathematics.",
            "Here's where things get really interesting. Watch how this function captures the essence of our topic.",
            "The direction field reveals the global structure. Every point has its own unique orientation.",
            "This example illustrates a subtle but important point that often gets overlooked.",
            "As we trace this final path, consider how all the pieces fit together.",
            "And so we've completed our journey through this fascinating topic. These concepts connect to many areas of mathematics and will serve you well in future explorations."
        ]
        
        scenes = []
        for i in range(20):
            func_expr, func_name = functions[i]
            scenes.append({
                "scene_number": i + 1,
                "duration_seconds": 18,
                "voiceover": voiceovers[i],
                "visual_description": f"Animated {visual_types[i]} visualization using {func_name}",
                "visual_type": visual_types[i],
                "visual_elements": {
                    "primary": func_name,
                    "math_expressions": [f"f(x) = {func_expr}"],
                    "function": func_expr,
                    "colors": {"primary": colors[i]}
                },
                "sync_points": [
                    {"time": "0:00", "voiceover_word": "start", "visual_action": "begin animation"},
                    {"time": "0:08", "voiceover_word": "middle", "visual_action": "show key feature"},
                    {"time": "0:15", "voiceover_word": "end", "visual_action": "complete animation"}
                ]
            })
        
        # Trim to requested number of scenes
        scenes = scenes[:num_scenes]
        
        return {
            "title": f"Understanding {prompt[:50]}",
            "total_duration_seconds": duration_seconds,
            "summary": f"A visual exploration of {prompt}",
            "scenes": scenes
        }
