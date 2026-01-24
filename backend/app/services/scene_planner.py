"""
Scene Planner - Two-Stage Pipeline Orchestrator with Visual Synchronization

Stage 1: Script Writer generates synchronized script
Stage 2: Manim Code Generator converts script to animations
Stage 3: Sync Narration ensures narration TRAILS visualization

CORE PRINCIPLE: Narration describes what IS visible, never what WILL BE visible.
"""
from typing import List, Dict, Any, Optional
import json
from app.config import settings
from app.services.script_writer import ScriptWriter
from app.services.manim_code_generator import ManimCodeGenerator
from app.services.topic_classifier import LLMClient
from app.services.sync_narration import generate_sync_narration


class ScenePlanner:
    """
    Orchestrates the two-stage video generation pipeline with visual synchronization.
    
    The pipeline ensures:
    1. Script Writing: Creates voiceover + animation descriptions
    2. Code Generation: Converts script into Manim scene specifications
    3. Sync Narration: Rewrites narration to follow visual-first principle
    
    CRITICAL: All narration is processed to ensure it describes
    what IS on screen, never what WILL BE on screen.
    """
    
    def __init__(self):
        self.script_writer = ScriptWriter()
        self.code_generator = ManimCodeGenerator()
        self.llm = LLMClient()
    
    async def plan(self, prompt: str, topic: str, sample_mode: bool = False, duration_seconds: int = 180) -> Dict[str, Any]:
        """
        Generate a complete scene plan using the two-stage pipeline.
        
        Stage 1: Generate synchronized script (voiceover + visual descriptions)
        Stage 2: Convert script to Manim scene specifications
        Stage 3: Apply sync narration (visual-first principle)
        
        Args:
            prompt: User's topic/question
            topic: Classified topic category
            sample_mode: If True, generates a short sample video
            duration_seconds: Target video duration in seconds
        """
        if duration_seconds <= 60:
            sample_mode = True
        
        mode_str = f"{duration_seconds}s" if sample_mode else f"{duration_seconds}s full"
        print(f"🎬 Starting visual-synchronized pipeline ({mode_str})...")
        print(f"   Topic: {topic}")
        print(f"   Target duration: {duration_seconds} seconds")
        print(f"   Prompt: {prompt[:100]}...")
        
        # Stage 1: Generate synchronized script
        print(f"📝 Stage 1: Generating synchronized script...")
        script = await self.script_writer.generate_script(
            prompt, 
            sample_mode=sample_mode,
            duration_seconds=duration_seconds
        )
        
        script_scene_count = len(script.get("scenes", []))
        print(f"   ✅ Script generated: {script_scene_count} scenes")
        print(f"   Title: {script.get('title', 'Untitled')}")
        
        # Stage 2: Convert script to Manim scenes
        print(f"🎨 Stage 2: Converting script to Manim code...")
        scenes = await self.code_generator.generate_scenes(script)
        
        print(f"   ✅ Generated {len(scenes)} Manim scenes")
        
        # Stage 3: Apply visual-synchronized narration
        print(f"🔄 Stage 3: Applying visual-first narration sync...")
        synced_scenes = generate_sync_narration(scenes)
        print(f"   ✅ Narration synchronized for {len(synced_scenes)} scenes")
        
        # Analyze variety
        scene_types = {}
        for s in synced_scenes:
            st = s.get("scene_type", "unknown")
            scene_types[st] = scene_types.get(st, 0) + 1
        print(f"   Scene type distribution: {scene_types}")
        
        # Build final plan
        return {
            "topic": script.get("title", topic),
            "summary": script.get("summary", f"Visual explanation of {prompt}"),
            "total_scenes": len(synced_scenes),
            "estimated_duration_seconds": script.get("total_duration_seconds", len(synced_scenes) * 12),
            "scenes": synced_scenes,
            "sync_enabled": True  # Flag to indicate visual-sync is active
        }


# Fallback templates for when LLM is unavailable
FALLBACK_SCENES = {
    "gradient_descent": {
        "topic": "Gradient Descent Optimization",
        "summary": "Visual explanation of how gradient descent finds optimal solutions",
        "scenes": [
            {
                "scene_type": "text_labels",
                "title": "Gradient Descent",
                "text": "Finding the Minimum",
                "math_mode": False,
                "is_intro": True,
                "narration": "Welcome to this visual exploration of gradient descent, one of the most fundamental algorithms in machine learning."
            },
            {
                "scene_type": "graph_2d",
                "title": "The Loss Landscape",
                "function": "x**2 + 0.5*sin(3*x)",
                "x_range": [-4, 4, 1],
                "y_range": [-2, 10, 2],
                "moving_dot": True,
                "start_x": 3.5,
                "narration": "Imagine standing on a hilly landscape. Your goal is to find the lowest point. The height at each position represents the error or loss of your model. We want to minimize this loss."
            },
            {
                "scene_type": "vector_arrows",
                "title": "The Gradient Points Uphill",
                "vectors": [[2, 3], [-2, -3]],
                "labels": ["\\nabla L", "-\\nabla L"],
                "show_components": True,
                "narration": "The gradient always points in the direction of steepest increase. To go downhill, we move in the opposite direction - the negative gradient. This simple idea is the heart of gradient descent."
            },
            {
                "scene_type": "graph_2d",
                "title": "Exponential Decay",
                "function": "exp(-x**2)",
                "x_range": [-3, 3, 1],
                "y_range": [-0.5, 1.5, 0.5],
                "show_derivative": True,
                "narration": "Different functions have different landscapes. This Gaussian curve has a smooth peak. Watch how the derivative, shown in blue, tells us the slope at each point."
            },
            {
                "scene_type": "dots_paths",
                "title": "Convergence Paths",
                "start_point": [3, 2],
                "end_point": [0, 0],
                "path_type": "spiral",
                "num_dots": 3,
                "narration": "Multiple starting points converge toward the minimum. In high dimensions, gradient descent navigates through complex loss landscapes to find optimal solutions."
            },
            {
                "scene_type": "graph_2d",
                "title": "Sine Wave Analysis",
                "function": "sin(x) + 0.3*sin(3*x)",
                "x_range": [-6, 6, 1],
                "y_range": [-2, 2, 1],
                "show_tangent": True,
                "tangent_x": 2,
                "narration": "Periodic functions like sine waves have multiple local minima. Gradient descent will find a local minimum, but not necessarily the global one."
            },
            {
                "scene_type": "text_labels",
                "title": "The Update Rule",
                "text": r"w_{t+1} = w_t - \alpha \nabla L(w_t)",
                "math_mode": True,
                "narration": "This is the update rule. We take the current parameters, subtract the gradient scaled by a learning rate alpha, and get new parameters. Repeat until convergence."
            },
            {
                "scene_type": "graph_2d",
                "title": "Learning Rate Effects",
                "function": "0.5*x**2 - 2*x + 3",
                "x_range": [-2, 6, 1],
                "y_range": [-1, 8, 1],
                "moving_dot": True,
                "start_x": 5,
                "narration": "The learning rate controls step size. Too small and training takes forever. Too large and we might overshoot the minimum. Finding the right balance is crucial."
            },
            {
                "scene_type": "vector_arrows",
                "title": "Momentum",
                "vectors": [[1.5, 0.5], [1.2, 0.3], [0.9, 0.1], [0.6, -0.1]],
                "labels": ["v_1", "v_2", "v_3", "v_4"],
                "narration": "Momentum helps gradient descent accelerate through flat regions and dampen oscillations. It's like a ball rolling downhill with inertia."
            },
            {
                "scene_type": "graph_2d",
                "title": "Sigmoid Function",
                "function": "1/(1+exp(-x))",
                "x_range": [-6, 6, 1],
                "y_range": [-0.5, 1.5, 0.5],
                "show_derivative": True,
                "narration": "The sigmoid function is used in logistic regression and neural networks. Its derivative is largest in the middle and vanishes at the extremes."
            },
            {
                "scene_type": "dots_paths",
                "title": "Stochastic Path",
                "start_point": [4, 3],
                "end_point": [0.5, 0.2],
                "path_type": "bezier",
                "num_dots": 1,
                "narration": "Stochastic gradient descent uses random samples instead of the full dataset. This adds noise but can help escape local minima and speeds up training."
            },
            {
                "scene_type": "text_labels",
                "title": "Key Takeaways",
                "text": "Gradient Descent: Simple Yet Powerful",
                "math_mode": False,
                "narration": "Gradient descent is elegantly simple: keep asking which way is down, and take a step. This algorithm powers modern machine learning, from simple linear regression to massive neural networks."
            }
        ]
    },
    "default": {
        "topic": "Mathematical Concept",
        "summary": "Visual exploration of mathematical ideas",
        "scenes": [
            {
                "scene_type": "text_labels",
                "title": "Welcome",
                "text": "Let's Explore Mathematics",
                "math_mode": False,
                "is_intro": True,
                "narration": "Welcome to this visual journey through mathematics. We'll use animations to build intuition and understanding."
            },
            {
                "scene_type": "graph_2d",
                "title": "Quadratic Functions",
                "function": "x**2 - 2*x - 3",
                "x_range": [-3, 5, 1],
                "y_range": [-5, 10, 2],
                "moving_dot": True,
                "start_x": 4,
                "narration": "Let's start with a quadratic function. Watch how the curve rises, reaches a minimum, and rises again. The shape of this parabola tells us about the function's behavior."
            },
            {
                "scene_type": "graph_2d",
                "title": "Trigonometric Waves",
                "function": "2*sin(x) + cos(2*x)",
                "x_range": [-6, 6, 1],
                "y_range": [-4, 4, 1],
                "show_derivative": True,
                "narration": "Trigonometric functions create beautiful waves. This combination of sine and cosine shows complex oscillation patterns. The derivative reveals the rate of change."
            },
            {
                "scene_type": "vector_arrows",
                "title": "Vector Visualization",
                "vectors": [[3, 1], [1, 3], [2, 2]],
                "labels": ["\\vec{a}", "\\vec{b}", "\\vec{a}+\\vec{b}"],
                "show_components": True,
                "narration": "Vectors have both magnitude and direction. When we add vectors, we place them tip to tail. The result is a new vector from the start of the first to the end of the last."
            },
            {
                "scene_type": "graph_2d",
                "title": "Exponential Growth",
                "function": "exp(0.5*x)",
                "x_range": [-4, 4, 1],
                "y_range": [-1, 8, 1],
                "show_tangent": True,
                "tangent_x": 1,
                "narration": "Exponential functions grow incredibly fast. The tangent line at any point has a slope proportional to the function value itself. This self-similarity is key to understanding exponential behavior."
            },
            {
                "scene_type": "dots_paths",
                "title": "Parametric Motion",
                "start_point": [-3, 0],
                "end_point": [3, 0],
                "path_type": "curve",
                "num_dots": 2,
                "narration": "Points can trace curved paths through space. These parametric curves appear everywhere in physics, from planetary orbits to projectile motion."
            },
            {
                "scene_type": "graph_2d",
                "title": "Logarithmic Scale",
                "function": "log(x + 1)",
                "x_range": [-0.5, 8, 1],
                "y_range": [-1, 3, 1],
                "narration": "Logarithms are the inverse of exponentials. They grow slowly, compressing large ranges into manageable scales. This is why we use log scales for earthquake magnitudes and sound levels."
            },
            {
                "scene_type": "text_labels",
                "title": "Summary",
                "text": r"f(x), \nabla f, \int f\,dx",
                "math_mode": True,
                "narration": "We've explored functions, derivatives, vectors, and curves. These tools help us understand change, direction, and accumulation. Mathematics reveals the patterns underlying our world."
            }
        ]
    }
}


# Module-level function for backward compatibility
async def plan_scenes(prompt: str) -> Dict[str, Any]:
    """Backward-compatible function for scene planning."""
    planner = ScenePlanner()
    return await planner.plan(prompt, "General")
