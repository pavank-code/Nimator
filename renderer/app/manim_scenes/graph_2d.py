"""
Graph2D Scene - Standalone Manim scene for 2D function plotting.
This file can be used directly with `manim render graph_2d.py Graph2D`
"""
from manim import *
from sympy import sympify, symbols


class Graph2D(Scene):
    """Scene for rendering 2D graphs and functions."""
    
    # Default configuration - can be overridden
    CONFIG = {
        "function": "x**2",
        "x_range": [-4, 4, 1],
        "y_range": [-2, 10, 1],
        "show_derivative": False,
        "moving_dot": True,
        "start_x": 2.5,
        "color_scheme": {
            "axes": WHITE,
            "graph": YELLOW,
            "derivative": BLUE,
            "dot": RED
        }
    }
    
    def construct(self):
        config = self.CONFIG
        
        # Parse function
        func_str = config["function"]
        x = symbols('x')
        
        try:
            expr = sympify(func_str.replace("^", "**"))
            func = lambda val: float(expr.subs(x, val))
        except:
            func = lambda val: val**2
        
        x_range = config["x_range"]
        y_range = config["y_range"]
        
        # Create axes
        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=10,
            y_length=6,
            axis_config={
                "color": config["color_scheme"]["axes"],
                "stroke_width": 2,
                "include_tip": True,
                "tip_length": 0.2
            },
            x_axis_config={"numbers_to_include": list(range(int(x_range[0]), int(x_range[1]) + 1))},
            y_axis_config={"numbers_to_include": list(range(int(y_range[0]), int(y_range[1]) + 1, 2))}
        )
        axes.add_coordinates()
        
        # Create the graph
        graph = axes.plot(
            func,
            color=config["color_scheme"]["graph"],
            x_range=[x_range[0] + 0.5, x_range[1] - 0.5]
        )
        
        # Create label
        label_text = func_str.replace("**", "^")
        graph_label = MathTex(f"f(x) = {label_text}").scale(0.8)
        graph_label.to_corner(UR).shift(DOWN * 0.5)
        
        # Animate axes and graph
        self.play(Create(axes), run_time=1.5)
        self.play(Create(graph), Write(graph_label), run_time=1.5)
        
        # Moving dot animation
        if config["moving_dot"]:
            start_x = config.get("start_x", x_range[1] - 1)
            dot = Dot(color=config["color_scheme"]["dot"], radius=0.1)
            dot.move_to(axes.c2p(start_x, func(start_x)))
            
            self.play(Create(dot), run_time=0.5)
            
            # Gradient descent animation
            steps = 5
            current_x = start_x
            for i in range(steps):
                next_x = current_x * 0.6
                self.play(
                    dot.animate.move_to(axes.c2p(next_x, func(next_x))),
                    run_time=0.8
                )
                current_x = next_x
        
        # Show derivative if requested
        if config["show_derivative"]:
            try:
                from sympy import diff
                deriv_expr = diff(expr, x)
                deriv_func = lambda val: float(deriv_expr.subs(x, val))
                
                derivative_graph = axes.plot(
                    deriv_func,
                    color=config["color_scheme"]["derivative"],
                    x_range=[x_range[0] + 0.5, x_range[1] - 0.5]
                )
                derivative_label = MathTex(f"f'(x)", color=BLUE).scale(0.7)
                derivative_label.next_to(graph_label, DOWN)
                
                self.play(Create(derivative_graph), Write(derivative_label), run_time=1)
            except:
                pass
        
        self.wait(1)


class GradientDescentGraph(Scene):
    """Specialized scene for gradient descent visualization."""
    
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 9, 1],
            x_length=10,
            y_length=6,
            axis_config={"color": WHITE, "include_tip": True}
        )
        axes.add_coordinates()
        
        # Cost function (parabola)
        cost_func = lambda x: x**2
        graph = axes.plot(cost_func, color=YELLOW, x_range=[-2.8, 2.8])
        
        # Labels
        cost_label = MathTex("J(w) = w^2", color=YELLOW).scale(0.8)
        cost_label.to_corner(UR)
        
        title = Text("Gradient Descent", font_size=36)
        title.to_edge(UP)
        
        # Initial animations
        self.play(Write(title), run_time=0.8)
        self.play(Create(axes), run_time=1)
        self.play(Create(graph), Write(cost_label), run_time=1)
        
        # Create moving point
        start_x = 2.5
        dot = Dot(color=RED, radius=0.12)
        dot.move_to(axes.c2p(start_x, cost_func(start_x)))
        
        w_label = MathTex("w", color=RED).scale(0.6)
        w_label.next_to(dot, UP + RIGHT, buff=0.1)
        
        self.play(Create(dot), Write(w_label), run_time=0.5)
        
        # Gradient descent steps
        learning_rate = 0.3
        current_x = start_x
        
        for step in range(6):
            # Calculate gradient
            gradient = 2 * current_x
            new_x = current_x - learning_rate * gradient
            
            # Show gradient arrow
            if abs(gradient) > 0.3:
                arrow_scale = min(abs(gradient) * 0.3, 1.0)
                arrow = Arrow(
                    start=axes.c2p(current_x, cost_func(current_x)),
                    end=axes.c2p(current_x - arrow_scale * (1 if gradient > 0 else -1), cost_func(current_x)),
                    color=GREEN,
                    buff=0,
                    stroke_width=3
                )
                self.play(Create(arrow), run_time=0.3)
            
            # Move point
            self.play(
                dot.animate.move_to(axes.c2p(new_x, cost_func(new_x))),
                w_label.animate.next_to(axes.c2p(new_x, cost_func(new_x)), UP + RIGHT, buff=0.1),
                run_time=0.6
            )
            
            if 'arrow' in locals():
                self.play(FadeOut(arrow), run_time=0.2)
            
            current_x = new_x
        
        # Final state
        converged_text = Text("Converged!", font_size=24, color=GREEN)
        converged_text.next_to(dot, DOWN, buff=0.3)
        self.play(Write(converged_text), run_time=0.5)
        
        self.wait(1)