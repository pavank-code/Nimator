"""
VectorArrows Scene - Manim scene for vector visualization.
"""
from manim import *
import numpy as np


class VectorArrows(Scene):
    """Scene for rendering vector arrows and operations."""
    
    CONFIG = {
        "vectors": [[2, 1], [-1, 2]],
        "labels": ["\\vec{a}", "\\vec{b}"],
        "origin": [0, 0],
        "colors": [YELLOW, RED, BLUE, GREEN, ORANGE, PURPLE],
        "show_sum": True
    }
    
    def construct(self):
        config = self.CONFIG
        
        # Create axes
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            x_length=8,
            y_length=8,
            axis_config={"color": GRAY, "stroke_width": 1}
        )
        
        # Grid for reference
        grid = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            x_length=8,
            y_length=8,
            background_line_style={
                "stroke_color": GRAY,
                "stroke_width": 0.5,
                "stroke_opacity": 0.3
            }
        )
        
        self.play(Create(grid), Create(axes), run_time=1)
        
        vectors = config["vectors"]
        labels = config.get("labels", [])
        colors = config["colors"]
        origin = config["origin"]
        origin_point = axes.c2p(origin[0], origin[1])
        
        created_vectors = []
        
        for i, vec in enumerate(vectors):
            color = colors[i % len(colors)]
            end_point = axes.c2p(origin[0] + vec[0], origin[1] + vec[1])
            
            arrow = Arrow(
                start=origin_point,
                end=end_point,
                color=color,
                buff=0,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.15
            )
            
            created_vectors.append((vec, arrow, color))
            self.play(Create(arrow), run_time=0.8)
            
            # Add label
            if i < len(labels):
                label = MathTex(labels[i], color=color).scale(0.8)
                label.next_to(arrow.get_end(), UP + RIGHT, buff=0.1)
                self.play(Write(label), run_time=0.4)
        
        # Show vector sum if enabled
        if config.get("show_sum", True) and len(vectors) >= 2:
            sum_vec = [sum(v[0] for v in vectors), sum(v[1] for v in vectors)]
            sum_end = axes.c2p(origin[0] + sum_vec[0], origin[1] + sum_vec[1])
            
            sum_arrow = Arrow(
                start=origin_point,
                end=sum_end,
                color=GREEN,
                buff=0,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.12
            )
            
            sum_label = MathTex("\\vec{a} + \\vec{b}", color=GREEN).scale(0.7)
            sum_label.next_to(sum_arrow.get_end(), UP, buff=0.2)
            
            self.play(Create(sum_arrow), Write(sum_label), run_time=1)
        
        self.wait(1)


class VectorAddition(Scene):
    """Demonstrates vector addition step by step."""
    
    def construct(self):
        # Title
        title = Text("Vector Addition", font_size=36)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # Create plane
        plane = NumberPlane(
            x_range=[-4, 6, 1],
            y_range=[-2, 5, 1],
            x_length=10,
            y_length=7,
            background_line_style={"stroke_opacity": 0.3}
        )
        self.play(Create(plane), run_time=1)
        
        # Vector a
        vec_a = Arrow(plane.c2p(0, 0), plane.c2p(3, 1), color=YELLOW, buff=0)
        label_a = MathTex("\\vec{a} = (3, 1)", color=YELLOW).scale(0.6)
        label_a.next_to(vec_a, UP, buff=0.1)
        
        self.play(Create(vec_a), Write(label_a), run_time=1)
        
        # Vector b
        vec_b = Arrow(plane.c2p(0, 0), plane.c2p(1, 2), color=RED, buff=0)
        label_b = MathTex("\\vec{b} = (1, 2)", color=RED).scale(0.6)
        label_b.next_to(vec_b, LEFT, buff=0.1)
        
        self.play(Create(vec_b), Write(label_b), run_time=1)
        
        # Move b to tip of a (tail-to-tip method)
        vec_b_moved = Arrow(plane.c2p(3, 1), plane.c2p(4, 3), color=RED, buff=0)
        
        self.play(
            Transform(vec_b.copy(), vec_b_moved),
            run_time=1.5
        )
        self.add(vec_b_moved)
        
        # Resultant vector
        vec_sum = Arrow(plane.c2p(0, 0), plane.c2p(4, 3), color=GREEN, buff=0, stroke_width=5)
        label_sum = MathTex("\\vec{a} + \\vec{b} = (4, 3)", color=GREEN).scale(0.6)
        label_sum.next_to(vec_sum.get_center(), DOWN + RIGHT, buff=0.2)
        
        self.play(Create(vec_sum), Write(label_sum), run_time=1)
        
        self.wait(1)