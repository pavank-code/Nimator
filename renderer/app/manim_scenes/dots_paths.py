"""
DotsPaths Scene - Manim scene for dot and path animations.
"""
from manim import *
import numpy as np


class DotsPaths(Scene):
    """Scene for animating dots moving along paths."""
    
    CONFIG = {
        "start_point": [-3, 0],
        "end_point": [3, 0],
        "path_type": "line",  # line, curve, parabola, bezier
        "dot_color": BLUE,
        "path_color": YELLOW,
        "show_trace": True
    }
    
    def construct(self):
        config = self.CONFIG
        
        start = config["start_point"]
        end = config["end_point"]
        path_type = config["path_type"]
        
        # Create start and end markers
        start_dot = Dot(point=[start[0], start[1], 0], color=GREEN, radius=0.15)
        end_dot = Dot(point=[end[0], end[1], 0], color=RED, radius=0.15)
        
        start_label = Text("Start", font_size=20, color=GREEN)
        start_label.next_to(start_dot, DOWN)
        
        end_label = Text("End", font_size=20, color=RED)
        end_label.next_to(end_dot, DOWN)
        
        # Create path based on type
        if path_type == "line":
            path = Line(
                start=[start[0], start[1], 0],
                end=[end[0], end[1], 0],
                color=config["path_color"]
            )
        elif path_type == "curve" or path_type == "bezier":
            control_y = max(start[1], end[1]) + 2
            path = CubicBezier(
                np.array([start[0], start[1], 0]),
                np.array([(start[0] + end[0]) / 2, control_y, 0]),
                np.array([(start[0] + end[0]) / 2, control_y, 0]),
                np.array([end[0], end[1], 0]),
                color=config["path_color"]
            )
        elif path_type == "parabola":
            path = ParametricFunction(
                lambda t: np.array([
                    start[0] + (end[0] - start[0]) * t,
                    start[1] + 4 * t * (1 - t) * 2,
                    0
                ]),
                t_range=[0, 1],
                color=config["path_color"]
            )
        else:
            path = Line(
                start=[start[0], start[1], 0],
                end=[end[0], end[1], 0],
                color=config["path_color"]
            )
        
        # Moving dot
        moving_dot = Dot(point=[start[0], start[1], 0], color=config["dot_color"], radius=0.12)
        
        # Animate
        self.play(Create(start_dot), Create(end_dot), run_time=0.5)
        self.play(Write(start_label), Write(end_label), run_time=0.5)
        self.play(Create(path), run_time=1)
        self.play(Create(moving_dot), run_time=0.3)
        
        # Create trace if enabled
        if config.get("show_trace", True):
            trace = TracedPath(moving_dot.get_center, stroke_color=BLUE, stroke_width=2)
            self.add(trace)
        
        # Move along path
        self.play(MoveAlongPath(moving_dot, path), run_time=3, rate_func=smooth)
        
        self.wait(1)


class GradientDescentPath(Scene):
    """Specialized path scene for gradient descent visualization."""
    
    def construct(self):
        # Title
        title = Text("Gradient Descent Steps", font_size=32)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # Create a "landscape" (1D projection of loss)
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 10, 2],
            x_length=10,
            y_length=5,
            axis_config={"include_tip": True}
        )
        axes.shift(DOWN * 0.5)
        
        # Loss function
        loss = axes.plot(lambda x: x**2 + 1, color=YELLOW)
        loss_label = MathTex("L(w)", color=YELLOW).scale(0.7)
        loss_label.next_to(loss, UR)
        
        self.play(Create(axes), run_time=0.8)
        self.play(Create(loss), Write(loss_label), run_time=0.8)
        
        # Starting point
        x_vals = [2.5, 1.75, 1.225, 0.8575, 0.6, 0.42, 0.29, 0.2]
        
        dot = Dot(color=RED, radius=0.1)
        dot.move_to(axes.c2p(x_vals[0], x_vals[0]**2 + 1))
        
        step_label = Text("Step 0", font_size=20)
        step_label.to_corner(DL)
        
        self.play(Create(dot), Write(step_label), run_time=0.5)
        
        # Animate descent steps
        for i in range(1, len(x_vals)):
            new_x = x_vals[i]
            new_y = new_x**2 + 1
            
            new_step_label = Text(f"Step {i}", font_size=20)
            new_step_label.to_corner(DL)
            
            self.play(
                dot.animate.move_to(axes.c2p(new_x, new_y)),
                Transform(step_label, new_step_label),
                run_time=0.6
            )
        
        # Converged
        converged = Text("Minimum Found!", font_size=24, color=GREEN)
        converged.next_to(dot, UP, buff=0.3)
        self.play(Write(converged), run_time=0.5)
        
        self.wait(1)