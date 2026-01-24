"""
Base Scene Module - Premium 15+ Minute Educational Animations
Pitch black background, smooth animations, 2D/3D visuals.
Ultra-fast intro (< 4 seconds), immediate content delivery.
"""
import os
import tempfile
import numpy as np
from typing import Dict, Any, Optional, List
from sympy import sympify, symbols, diff
from manim import *

# Configure Manim for PREMIUM rendering - PITCH BLACK background
config.pixel_height = 1080
config.pixel_width = 1920
config.frame_rate = 60
config.background_color = "#000000"  # PITCH BLACK


def render_scene(
    scene_data: Dict[str, Any],
    job_id: str,
    scene_index: int,
    output_dir: str,
    timeout: int = 600
) -> Optional[str]:
    """Render a scene and return the output video path."""
    import shutil
    
    scene_type = scene_data.get("scene_type", "text_labels")
    output_path = os.path.join(output_dir, f"{job_id}_scene_{scene_index}.mp4")
    
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"manim_{job_id}_{scene_index}_")
        config.media_dir = temp_dir
        config.output_file = f"{job_id}_scene_{scene_index}"
        
        scene_classes = {
            "graph_2d": Graph2DScene,
            "vector_arrows": VectorArrowsScene,
            "dots_paths": DotsPathsScene,
            "text_labels": TextLabelsScene,
            "transformation": TransformationScene,
            "coordinate_system": CoordinateSystemScene,
            "graph_3d": Graph3DScene,
            "surface_3d": Surface3DScene,
            "vector_field": VectorFieldScene,
            "matrix_transform": MatrixTransformScene,
            "complex_plane": ComplexPlaneScene,
            "parametric_curve": ParametricCurveScene,
        }
        
        scene_class = scene_classes.get(scene_type, TextLabelsScene)
        scene = scene_class(scene_data)
        scene.render()
        
        video_found = None
        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                if f.endswith(".mp4"):
                    video_found = os.path.join(root, f)
                    break
            if video_found:
                break
        
        if video_found and os.path.exists(video_found):
            shutil.copy2(video_found, output_path)
            print(f"      ✅ Scene {scene_index+1} rendered")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return output_path
        else:
            print(f"      ⚠️ No video found in {temp_dir}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None
        
    except Exception as e:
        print(f"Scene render error: {e}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# 2D SCENES - Rich, Smooth Animations
# =============================================================================

class Graph2DScene(Scene):
    """
    2D Graph Scene - 25-40 seconds of rich graph animations.
    Smooth transitions, multiple visual elements, comprehensive coverage.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        is_intro = data.get("is_intro", False)
        
        # Parse function
        func_str = data.get("function", "x**2")
        x_sym = symbols('x')
        
        try:
            expr = sympify(func_str.replace("^", "**"))
            def func(val):
                try:
                    result = float(expr.subs(x_sym, val))
                    return result if abs(result) < 50 else np.sign(result) * 50
                except:
                    return 0
            deriv_expr = diff(expr, x_sym)
            def deriv_func(val):
                try:
                    result = float(deriv_expr.subs(x_sym, val))
                    return result if abs(result) < 50 else np.sign(result) * 50
                except:
                    return 0
        except:
            func = lambda val: val**2
            deriv_func = lambda val: 2 * val
        
        x_range = data.get("x_range", [-5, 5, 1])
        y_range = data.get("y_range", [-3, 10, 1])
        
        # FAST title for intro scenes (< 2 seconds)
        if title and not is_intro:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        elif title and is_intro:
            # Ultra-fast intro - just flash title
            title_text = Text(title, font_size=48, color=YELLOW, weight=BOLD)
            self.play(FadeIn(title_text), run_time=0.3)
            self.wait(0.5)
            self.play(FadeOut(title_text), run_time=0.2)
        
        # Create axes with smooth animation
        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=11,
            y_length=6.5,
            axis_config={
                "color": BLUE_C,
                "stroke_width": 2,
                "include_tip": True,
                "tip_length": 0.2,
            },
            tips=True,
        )
        axes_labels = axes.get_axis_labels(
            x_label=MathTex("x", color=BLUE_C),
            y_label=MathTex("y", color=BLUE_C)
        )
        
        self.play(Create(axes, lag_ratio=0.05), run_time=1.2)
        self.play(Write(axes_labels), run_time=0.4)
        
        # Create and animate the main graph with glow effect
        try:
            graph = axes.plot(func, color=YELLOW, stroke_width=4)
            graph_glow = axes.plot(func, color=YELLOW_A, stroke_width=8, stroke_opacity=0.3)
        except:
            graph = axes.plot(lambda x: x**2, color=YELLOW, stroke_width=4)
            graph_glow = axes.plot(lambda x: x**2, color=YELLOW_A, stroke_width=8, stroke_opacity=0.3)
        
        # Function label
        label_tex = func_str.replace("**", "^").replace("*", "\\cdot ")
        try:
            graph_label = MathTex(f"f(x) = {label_tex}", color=YELLOW).scale(0.65)
        except:
            graph_label = Text(f"f(x) = {func_str}", color=YELLOW, font_size=24)
        graph_label.to_corner(UR).shift(DOWN * 0.3 + LEFT * 0.2)
        
        # Smooth graph creation with glow
        self.play(Create(graph_glow), Create(graph), run_time=2, rate_func=smooth)
        self.play(FadeIn(graph_label, shift=LEFT * 0.3), run_time=0.5)
        
        # Multiple visual elements for comprehensive explanation
        
        # 1. Moving dot with trace (smooth animation)
        if data.get("moving_dot", False):
            start_x = data.get("start_x", x_range[0] + 1)
            end_x = data.get("end_x", x_range[1] - 1)
            
            tracer = Dot(color=RED, radius=0.12)
            tracer.add_updater(lambda m: m.set_z_index(10))
            tracer.move_to(axes.c2p(start_x, func(start_x)))
            
            # Glowing trace
            trace = TracedPath(
                tracer.get_center,
                stroke_color=RED,
                stroke_width=3,
                stroke_opacity=0.8
            )
            self.add(trace)
            self.play(FadeIn(tracer, scale=0.5), run_time=0.4)
            
            # Smooth movement along curve
            self.play(
                MoveAlongPath(tracer, graph),
                run_time=4,
                rate_func=smooth
            )
            self.wait(0.5)
        
        # 2. Tangent line animation
        if data.get("show_tangent", False):
            tangent_x = data.get("tangent_x", 2)
            point_y = func(tangent_x)
            slope = deriv_func(tangent_x)
            
            # Point on curve with glow
            dot = Dot(axes.c2p(tangent_x, point_y), color=GREEN, radius=0.12)
            dot_glow = Dot(axes.c2p(tangent_x, point_y), color=GREEN, radius=0.25, fill_opacity=0.3)
            
            self.play(FadeIn(dot_glow), FadeIn(dot), run_time=0.5)
            
            # Tangent line
            def tangent_line(t):
                return slope * (t - tangent_x) + point_y
            
            tangent = axes.plot(
                tangent_line,
                color=GREEN,
                x_range=[tangent_x - 2.5, tangent_x + 2.5],
                stroke_width=3
            )
            
            slope_label = MathTex(f"m = {slope:.2f}", color=GREEN).scale(0.6)
            slope_label.next_to(dot, UR, buff=0.2)
            
            self.play(Create(tangent), run_time=1)
            self.play(FadeIn(slope_label), run_time=0.4)
            self.wait(0.5)
            
            # Animate tangent moving along curve
            if data.get("animate_tangent", False):
                for new_x in np.linspace(tangent_x - 1.5, tangent_x + 1.5, 8):
                    new_y = func(new_x)
                    new_slope = deriv_func(new_x)
                    new_tangent = axes.plot(
                        lambda t, s=new_slope, nx=new_x, ny=new_y: s * (t - nx) + ny,
                        color=GREEN,
                        x_range=[new_x - 2, new_x + 2],
                        stroke_width=3
                    )
                    self.play(
                        dot.animate.move_to(axes.c2p(new_x, new_y)),
                        dot_glow.animate.move_to(axes.c2p(new_x, new_y)),
                        Transform(tangent, new_tangent),
                        run_time=0.4
                    )
        
        # 3. Derivative curve with comparison
        if data.get("show_derivative", False):
            try:
                deriv_graph = axes.plot(deriv_func, color=BLUE, stroke_width=3)
                deriv_glow = axes.plot(deriv_func, color=BLUE_A, stroke_width=6, stroke_opacity=0.3)
            except:
                deriv_graph = axes.plot(lambda x: 2*x, color=BLUE, stroke_width=3)
                deriv_glow = axes.plot(lambda x: 2*x, color=BLUE_A, stroke_width=6, stroke_opacity=0.3)
            
            deriv_label = MathTex(r"f'(x)", color=BLUE).scale(0.6)
            deriv_label.next_to(graph_label, DOWN, buff=0.2)
            
            self.play(
                Create(deriv_glow),
                Create(deriv_graph),
                run_time=1.5,
                rate_func=smooth
            )
            self.play(FadeIn(deriv_label), run_time=0.4)
            self.wait(0.5)
        
        # 4. Area under curve with gradient fill
        if data.get("highlight_area", False):
            a = data.get("area_start", -2)
            b = data.get("area_end", 2)
            try:
                area = axes.get_area(
                    graph,
                    x_range=[a, b],
                    color=[BLUE_E, TEAL_E],
                    opacity=0.6
                )
                
                # Area label
                area_label = MathTex(
                    r"\int_{" + str(a) + r"}^{" + str(b) + r"} f(x)\,dx",
                    color=TEAL
                ).scale(0.55)
                area_label.next_to(area, DOWN, buff=0.3)
                
                self.play(FadeIn(area), run_time=1.2)
                self.play(FadeIn(area_label), run_time=0.5)
                self.wait(0.5)
            except:
                pass
        
        # 5. Critical points highlight
        if data.get("show_critical_points", False):
            # Find zeros of derivative (simplified)
            critical_points = data.get("critical_points", [0])
            for cp in critical_points:
                cp_dot = Dot(axes.c2p(cp, func(cp)), color=ORANGE, radius=0.15)
                cp_label = MathTex(f"({cp}, {func(cp):.1f})", color=ORANGE).scale(0.5)
                cp_label.next_to(cp_dot, UP, buff=0.15)
                
                self.play(
                    FadeIn(cp_dot, scale=0.5),
                    FadeIn(cp_label),
                    run_time=0.6
                )
        
        # Final pause for narration sync
        self.wait(2.5)


class VectorArrowsScene(Scene):
    """
    Vector Visualization Scene - 20-30 seconds.
    Shows vectors with smooth animations, components, and operations.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        
        # Fast title
        if title:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        
        # Create number plane with subtle grid
        plane = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-5, 5, 1],
            x_length=12,
            y_length=8,
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.3
            },
            axis_config={
                "stroke_color": BLUE_C,
                "stroke_width": 2,
            }
        )
        
        self.play(Create(plane, lag_ratio=0.02), run_time=1)
        
        vectors = data.get("vectors", [[2, 1], [-1, 2]])
        labels = data.get("labels", [])
        colors = [YELLOW, RED, BLUE, GREEN, ORANGE, PURPLE, PINK, TEAL]
        
        origin = data.get("origin", [0, 0])
        origin_point = plane.c2p(origin[0], origin[1])
        
        arrows = []
        arrow_labels = []
        
        # Create each vector with smooth animation
        for i, vec in enumerate(vectors):
            color = colors[i % len(colors)]
            end_point = plane.c2p(origin[0] + vec[0], origin[1] + vec[1])
            
            # Arrow with glow effect
            arrow = Arrow(
                start=origin_point,
                end=end_point,
                color=color,
                buff=0,
                stroke_width=6,
                max_tip_length_to_length_ratio=0.12
            )
            arrow_glow = Arrow(
                start=origin_point,
                end=end_point,
                color=color,
                buff=0,
                stroke_width=12,
                stroke_opacity=0.3,
                max_tip_length_to_length_ratio=0.12
            )
            arrows.append(arrow)
            
            self.play(
                GrowArrow(arrow_glow),
                GrowArrow(arrow),
                run_time=0.8
            )
            
            # Add label
            if i < len(labels) and labels[i]:
                try:
                    label = MathTex(str(labels[i]), color=color).scale(0.6)
                except:
                    label = Text(str(labels[i]), color=color, font_size=20)
                label.next_to(arrow.get_end(), UP + RIGHT, buff=0.1)
                arrow_labels.append(label)
                self.play(FadeIn(label), run_time=0.3)
            
            self.wait(0.3)
        
        # Show components with dashed lines
        if data.get("show_components", False) and vectors:
            for i, vec in enumerate(vectors[:2]):  # Show components for first 2 vectors
                color = colors[i % len(colors)]
                
                x_line = DashedLine(
                    plane.c2p(origin[0], origin[1]),
                    plane.c2p(origin[0] + vec[0], origin[1]),
                    color=color,
                    stroke_width=2,
                    stroke_opacity=0.7
                )
                y_line = DashedLine(
                    plane.c2p(origin[0] + vec[0], origin[1]),
                    plane.c2p(origin[0] + vec[0], origin[1] + vec[1]),
                    color=color,
                    stroke_width=2,
                    stroke_opacity=0.7
                )
                
                self.play(Create(x_line), Create(y_line), run_time=0.6)
        
        # Vector addition animation
        if data.get("animate_sum", False) and len(vectors) >= 2:
            v1, v2 = vectors[0], vectors[1]
            sum_vec = [v1[0] + v2[0], v1[1] + v2[1]]
            
            # Move second vector to tip of first
            moved_start = plane.c2p(origin[0] + v1[0], origin[1] + v1[1])
            moved_end = plane.c2p(origin[0] + sum_vec[0], origin[1] + sum_vec[1])
            
            moved_arrow = Arrow(
                start=moved_start,
                end=moved_end,
                color=colors[1],
                buff=0,
                stroke_width=4,
                stroke_opacity=0.8
            )
            
            self.play(Create(moved_arrow), run_time=0.8)
            
            # Result vector with emphasis
            result_arrow = Arrow(
                start=origin_point,
                end=plane.c2p(origin[0] + sum_vec[0], origin[1] + sum_vec[1]),
                color=WHITE,
                buff=0,
                stroke_width=8
            )
            
            result_label = MathTex(r"\vec{a} + \vec{b}", color=WHITE).scale(0.6)
            result_label.next_to(result_arrow.get_center(), RIGHT, buff=0.2)
            
            self.play(GrowArrow(result_arrow), run_time=1)
            self.play(FadeIn(result_label), run_time=0.4)
            
        self.wait(2)


class DotsPathsScene(Scene):
    """
    Dots and Paths Scene - 20-30 seconds.
    Smooth path tracing with multiple visual elements.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        
        # Fast title
        if title:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        
        start = data.get("start_point", [-4, 0])
        end = data.get("end_point", [4, 0])
        path_type = data.get("path_type", "curve")
        num_dots = min(data.get("num_dots", 1), 5)
        
        # Create subtle background grid
        grid = NumberPlane(
            x_range=[-7, 7, 1],
            y_range=[-5, 5, 1],
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 0.5,
                "stroke_opacity": 0.2
            }
        )
        self.play(FadeIn(grid), run_time=0.5)
        
        # Create path based on type
        if path_type == "line":
            path = Line([start[0], start[1], 0], [end[0], end[1], 0], color=GRAY, stroke_width=2)
        elif path_type == "curve" or path_type == "bezier":
            mid_y = max(start[1], end[1]) + 2.5
            path = CubicBezier(
                [start[0], start[1], 0],
                [start[0] + 2, mid_y, 0],
                [end[0] - 2, mid_y, 0],
                [end[0], end[1], 0],
                color=GRAY,
                stroke_width=2
            )
        elif path_type == "parabola":
            path = ParametricFunction(
                lambda t: np.array([
                    start[0] + (end[0] - start[0]) * t,
                    start[1] + 4 * t * (1 - t) * 3,
                    0
                ]),
                t_range=[0, 1],
                color=GRAY,
                stroke_width=2
            )
        elif path_type == "spiral":
            path = ParametricFunction(
                lambda t: np.array([
                    (4 - 3*t) * np.cos(6 * PI * t),
                    (4 - 3*t) * np.sin(6 * PI * t),
                    0
                ]),
                t_range=[0, 1],
                color=GRAY,
                stroke_width=2
            )
        elif path_type == "oscillate":
            path = ParametricFunction(
                lambda t: np.array([
                    start[0] + (end[0] - start[0]) * t,
                    start[1] + np.sin(6 * PI * t) * 1.5,
                    0
                ]),
                t_range=[0, 1],
                color=GRAY,
                stroke_width=2
            )
        elif path_type == "helix":
            path = ParametricFunction(
                lambda t: np.array([
                    2 * np.cos(4 * PI * t),
                    2 * np.sin(4 * PI * t) + 2 * t - 1,
                    0
                ]),
                t_range=[0, 1],
                color=GRAY,
                stroke_width=2
            )
        else:
            path = Line([start[0], start[1], 0], [end[0], end[1], 0], color=GRAY, stroke_width=2)
        
        self.play(Create(path), run_time=1)
        
        # Create and animate dots with glowing trails
        colors = [YELLOW, RED, BLUE, GREEN, PURPLE]
        dots = []
        traces = []
        
        for i in range(num_dots):
            color = colors[i % len(colors)]
            
            dot = Dot(color=color, radius=0.15)
            dot_glow = Dot(color=color, radius=0.3, fill_opacity=0.3)
            dot.move_to(path.get_start())
            dot_glow.move_to(path.get_start())
            
            trace = TracedPath(
                dot.get_center,
                stroke_color=color,
                stroke_width=4,
                stroke_opacity=0.8
            )
            
            dots.append((dot, dot_glow))
            traces.append(trace)
            self.add(trace)
        
        # Animate dots appearing
        self.play(
            *[FadeIn(d, scale=0.5) for d, g in dots],
            *[FadeIn(g, scale=0.5) for d, g in dots],
            run_time=0.5
        )
        
        # Move dots along path with staggered timing
        animations = []
        for i, (dot, glow) in enumerate(dots):
            delay_factor = 1 + i * 0.5
            animations.append(MoveAlongPath(dot, path, rate_func=smooth))
            animations.append(MoveAlongPath(glow, path, rate_func=smooth))
        
        self.play(*animations, run_time=4)
        
        # Pulse effect at end
        self.play(
            *[d.animate.scale(1.5) for d, g in dots],
            *[g.animate.scale(1.5) for d, g in dots],
            run_time=0.3
        )
        self.play(
            *[d.animate.scale(1/1.5) for d, g in dots],
            *[g.animate.scale(1/1.5) for d, g in dots],
            run_time=0.3
        )
        
        self.wait(2)


class TextLabelsScene(Scene):
    """
    Text and Formula Scene - 15-25 seconds.
    Fast intro, elegant formula reveals.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        
        text = str(data.get("text", ""))
        math_mode = data.get("math_mode", False)
        title = data.get("title", "")
        is_intro = data.get("is_intro", False)
        build_up = data.get("build_up", True)
        
        # ULTRA-FAST intro for first scene (< 4 seconds total)
        if is_intro:
            # Just show title quickly and move on
            if title:
                title_text = Text(title, font_size=56, color=YELLOW, weight=BOLD)
                subtitle = Text(text if not math_mode else "", font_size=28, color=WHITE)
                subtitle.next_to(title_text, DOWN, buff=0.4)
                
                self.play(FadeIn(title_text, scale=0.9), run_time=0.4)
                if text and not math_mode:
                    self.play(FadeIn(subtitle), run_time=0.3)
                self.wait(1.5)
                self.play(
                    FadeOut(title_text, shift=UP * 0.5),
                    FadeOut(subtitle, shift=UP * 0.3) if text and not math_mode else Wait(0.1),
                    run_time=0.5
                )
            return
        
        # Normal title
        if title:
            title_text = Text(title, font_size=40, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.6)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
            self.wait(0.3)
        
        # Main content
        if math_mode:
            try:
                main_content = MathTex(text, font_size=52, color=YELLOW)
            except:
                main_content = Text(text, font_size=32, color=YELLOW)
        else:
            font_size = 28 if len(text) > 100 else (36 if len(text) > 50 else 44)
            main_content = Text(text, font_size=font_size, color=WHITE)
        
        main_content.move_to(ORIGIN)
        
        # Animate content
        if build_up and math_mode:
            self.play(Write(main_content), run_time=2)
        else:
            self.play(FadeIn(main_content, scale=0.95), run_time=1)
        
        self.wait(0.5)
        
        # Add emphasis box for math
        if math_mode:
            box = SurroundingRectangle(
                main_content,
                color=BLUE,
                buff=0.25,
                corner_radius=0.1,
                stroke_width=2
            )
            self.play(Create(box), run_time=0.6)
            
            # Subtle glow pulse
            self.play(
                main_content.animate.scale(1.05),
                box.animate.scale(1.05),
                run_time=0.3
            )
            self.play(
                main_content.animate.scale(1/1.05),
                box.animate.scale(1/1.05),
                run_time=0.3
            )
        
        self.wait(3)


class TransformationScene(Scene):
    """
    Geometric Transformation Scene - 20-30 seconds.
    Smooth, visually rich transformations.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        transform_type = data.get("transform_type", "rotate")
        
        # Fast title
        if title:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        
        # Subtle grid background
        grid = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-4, 4, 1],
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 0.5,
                "stroke_opacity": 0.3
            }
        )
        self.play(FadeIn(grid), run_time=0.5)
        
        # Create shape with glow
        shape = Square(side_length=2.5, color=YELLOW, fill_opacity=0.5, stroke_width=3)
        shape_glow = Square(side_length=2.5, color=YELLOW, fill_opacity=0.15, stroke_width=0)
        
        original_label = Text("Original", font_size=20, color=YELLOW)
        original_label.next_to(shape, DOWN, buff=0.2)
        
        self.play(Create(shape_glow), Create(shape), run_time=0.8)
        self.play(FadeIn(original_label), run_time=0.3)
        self.wait(0.5)
        
        # Apply transformation
        if transform_type == "scale":
            scale_factor = data.get("scale_factor", 2)
            transform_label = MathTex(f"S({scale_factor})", color=GREEN).scale(0.7)
            transform_label.to_corner(UR)
            self.play(FadeIn(transform_label), run_time=0.4)
            
            self.play(
                shape.animate.scale(scale_factor),
                shape_glow.animate.scale(scale_factor),
                original_label.animate.shift(DOWN * (scale_factor - 1)),
                run_time=1.5,
                rate_func=smooth
            )
            
        elif transform_type == "rotate":
            angle = data.get("angle", PI/2)
            transform_label = MathTex(r"R_{90°}", color=GREEN).scale(0.7)
            transform_label.to_corner(UR)
            self.play(FadeIn(transform_label), run_time=0.4)
            
            self.play(
                Rotate(shape, angle=angle),
                Rotate(shape_glow, angle=angle),
                run_time=1.5,
                rate_func=smooth
            )
            
        elif transform_type == "shear":
            transform_label = Text("Shear", font_size=24, color=GREEN)
            transform_label.to_corner(UR)
            self.play(FadeIn(transform_label), run_time=0.4)
            
            self.play(
                shape.animate.apply_matrix([[1, 0.5], [0, 1]]),
                shape_glow.animate.apply_matrix([[1, 0.5], [0, 1]]),
                run_time=1.5,
                rate_func=smooth
            )
            
        elif transform_type == "reflect":
            reflect_axis = DashedLine([-6, 0, 0], [6, 0, 0], color=RED, stroke_width=2)
            self.play(Create(reflect_axis), run_time=0.5)
            
            self.play(
                shape.animate.flip(RIGHT),
                shape_glow.animate.flip(RIGHT),
                run_time=1.5,
                rate_func=smooth
            )
            
        elif transform_type == "morph":
            circle = Circle(radius=1.5, color=BLUE, fill_opacity=0.5, stroke_width=3)
            self.play(
                Transform(shape, circle),
                FadeOut(shape_glow),
                run_time=2,
                rate_func=smooth
            )
        
        # Result label
        self.play(FadeOut(original_label), run_time=0.3)
        result_label = Text("Transformed", font_size=20, color=GREEN)
        result_label.next_to(shape, DOWN, buff=0.2)
        self.play(FadeIn(result_label), run_time=0.3)
        
        self.wait(2.5)


class CoordinateSystemScene(Scene):
    """
    Coordinate System Scene - 25-35 seconds.
    Multiple elements with coordinated reveals.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        
        # Fast title
        if title:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        
        # Create axes
        axes = Axes(
            x_range=[-6, 6, 1],
            y_range=[-4, 4, 1],
            x_length=12,
            y_length=7,
            axis_config={"color": BLUE_C, "stroke_width": 2}
        )
        axes_labels = axes.get_axis_labels(
            x_label=MathTex("x", color=BLUE_C),
            y_label=MathTex("y", color=BLUE_C)
        )
        
        self.play(Create(axes, lag_ratio=0.02), run_time=1)
        self.play(Write(axes_labels), run_time=0.4)
        
        elements = data.get("elements", [])
        colors = [YELLOW, RED, GREEN, BLUE, ORANGE, PURPLE]
        created_objects = []
        
        for i, elem in enumerate(elements):
            color = colors[i % len(colors)]
            elem_type = elem.get("type", "point")
            
            if elem_type == "point":
                x, y = elem.get("x", 0), elem.get("y", 0)
                point = Dot(axes.c2p(x, y), color=color, radius=0.12)
                point_glow = Dot(axes.c2p(x, y), color=color, radius=0.25, fill_opacity=0.3)
                label = MathTex(f"({x}, {y})", color=color).scale(0.5)
                label.next_to(point, UR, buff=0.1)
                
                self.play(FadeIn(point_glow), FadeIn(point), run_time=0.5)
                self.play(FadeIn(label), run_time=0.3)
                created_objects.extend([point, label])
                    
            elif elem_type == "graph":
                func_str = elem.get("function", "x")
                x_sym = symbols('x')
                try:
                    expr = sympify(func_str)
                    func = lambda val, e=expr: float(e.subs(x_sym, val))
                except:
                    func = lambda val: val
                
                try:
                    graph = axes.plot(func, color=color, stroke_width=3)
                    graph_glow = axes.plot(func, color=color, stroke_width=6, stroke_opacity=0.3)
                    
                    self.play(Create(graph_glow), Create(graph), run_time=1.2)
                    created_objects.append(graph)
                except:
                    pass
            
            elif elem_type == "line":
                x1, y1 = elem.get("x1", -3), elem.get("y1", -2)
                x2, y2 = elem.get("x2", 3), elem.get("y2", 2)
                
                line = Line(
                    axes.c2p(x1, y1),
                    axes.c2p(x2, y2),
                    color=color,
                    stroke_width=3
                )
                
                self.play(Create(line), run_time=0.8)
                created_objects.append(line)
            
            self.wait(0.3)
        
        self.wait(2.5)


# =============================================================================
# 3D SCENES - New additions for comprehensive 3D visualization
# =============================================================================

class Graph3DScene(ThreeDScene):
    """
    3D Graph Scene - 25-40 seconds.
    Rotating 3D function visualization.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        
        # Set camera position
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        
        # Create 3D axes
        axes = ThreeDAxes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            z_range=[-2, 4, 1],
            x_length=8,
            y_length=8,
            z_length=5,
        )
        
        # Add title in 3D space
        if title:
            title_text = Text(title, font_size=32, color=WHITE)
            title_text.to_edge(UP)
            self.add_fixed_in_frame_mobjects(title_text)
            self.play(FadeIn(title_text), run_time=0.5)
        
        self.play(Create(axes), run_time=1.5)
        
        # Create 3D surface
        func_str = data.get("function", "x**2 + y**2")
        
        try:
            x_sym, y_sym = symbols('x y')
            expr = sympify(func_str.replace("^", "**"))
            
            def surface_func(u, v):
                try:
                    z = float(expr.subs([(x_sym, u), (y_sym, v)]))
                    return np.array([u, v, min(max(z, -3), 5)])
                except:
                    return np.array([u, v, u**2 + v**2])
            
            surface = Surface(
                surface_func,
                u_range=[-2, 2],
                v_range=[-2, 2],
                resolution=(30, 30),
                fill_opacity=0.7,
                stroke_color=YELLOW,
                stroke_width=0.5,
            )
            surface.set_color_by_gradient(BLUE, GREEN, YELLOW)
            
        except:
            surface = Surface(
                lambda u, v: np.array([u, v, u**2 + v**2]),
                u_range=[-2, 2],
                v_range=[-2, 2],
                resolution=(30, 30),
                fill_opacity=0.7,
            )
            surface.set_color_by_gradient(BLUE, GREEN, YELLOW)
        
        self.play(Create(surface), run_time=2)
        
        # Rotate camera for better view
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(4)
        self.stop_ambient_camera_rotation()
        
        # Add contour lines effect
        if data.get("show_contours", False):
            for z_level in np.linspace(0.5, 3, 5):
                contour = ParametricFunction(
                    lambda t: axes.c2p(
                        np.sqrt(z_level) * np.cos(t),
                        np.sqrt(z_level) * np.sin(t),
                        z_level
                    ),
                    t_range=[0, TAU],
                    color=WHITE,
                    stroke_width=2,
                    stroke_opacity=0.5
                )
                self.play(Create(contour), run_time=0.3)
        
        self.wait(2)


class Surface3DScene(ThreeDScene):
    """
    3D Surface Scene - 30-45 seconds.
    Complex surface visualization with camera movement.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        surface_type = data.get("surface_type", "paraboloid")
        
        self.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)
        
        if title:
            title_text = Text(title, font_size=32, color=WHITE)
            title_text.to_edge(UP)
            self.add_fixed_in_frame_mobjects(title_text)
            self.play(FadeIn(title_text), run_time=0.5)
        
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-2, 3, 1],
        )
        
        self.play(Create(axes), run_time=1)
        
        # Different surface types
        if surface_type == "saddle":
            surface = Surface(
                lambda u, v: np.array([u, v, u**2 - v**2]),
                u_range=[-2, 2],
                v_range=[-2, 2],
                resolution=(25, 25),
            )
        elif surface_type == "wave":
            surface = Surface(
                lambda u, v: np.array([u, v, np.sin(u) * np.cos(v)]),
                u_range=[-PI, PI],
                v_range=[-PI, PI],
                resolution=(30, 30),
            )
        elif surface_type == "sphere":
            surface = Surface(
                lambda u, v: np.array([
                    np.cos(u) * np.sin(v),
                    np.sin(u) * np.sin(v),
                    np.cos(v)
                ]),
                u_range=[0, TAU],
                v_range=[0, PI],
                resolution=(30, 30),
            )
        elif surface_type == "torus":
            R, r = 2, 0.7
            surface = Surface(
                lambda u, v: np.array([
                    (R + r * np.cos(v)) * np.cos(u),
                    (R + r * np.cos(v)) * np.sin(u),
                    r * np.sin(v)
                ]),
                u_range=[0, TAU],
                v_range=[0, TAU],
                resolution=(30, 30),
            )
        else:  # paraboloid
            surface = Surface(
                lambda u, v: np.array([u, v, u**2 + v**2]),
                u_range=[-2, 2],
                v_range=[-2, 2],
                resolution=(25, 25),
            )
        
        surface.set_color_by_gradient(BLUE_E, TEAL, GREEN, YELLOW)
        surface.set_fill_opacity(0.8)
        
        self.play(Create(surface), run_time=2.5)
        
        # Camera movement
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        self.wait(1.5)


class VectorFieldScene(Scene):
    """
    Vector Field Scene - 25-35 seconds.
    Animated vector field visualization.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        field_type = data.get("field_type", "radial")
        
        if title:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        
        # Create vector field
        if field_type == "radial":
            func = lambda p: p / (np.linalg.norm(p) + 0.5)
        elif field_type == "rotational":
            func = lambda p: np.array([-p[1], p[0], 0]) / (np.linalg.norm(p) + 0.5)
        elif field_type == "gradient":
            func = lambda p: np.array([2*p[0], 2*p[1], 0]) / 3
        elif field_type == "sink":
            func = lambda p: -p / (np.linalg.norm(p) + 0.5)
        else:
            func = lambda p: np.array([1, 0.5, 0])
        
        vector_field = ArrowVectorField(
            func,
            x_range=[-5, 5, 0.8],
            y_range=[-3, 3, 0.8],
            colors=[BLUE, TEAL, GREEN, YELLOW, ORANGE],
            length_func=lambda x: min(x, 0.6)
        )
        
        self.play(Create(vector_field), run_time=2.5)
        self.wait(1)
        
        # Animate flow lines
        if data.get("show_flow", True):
            stream_lines = StreamLines(
                func,
                x_range=[-5, 5, 0.5],
                y_range=[-3, 3, 0.5],
                stroke_width=2,
                max_anchors_per_line=30,
            )
            self.add(stream_lines)
            stream_lines.start_animation(flow_speed=1.5)
            self.wait(4)
            stream_lines.end_animation()
        
        self.wait(2)


class MatrixTransformScene(Scene):
    """
    Matrix Transform Scene - 25-35 seconds.
    Visualize linear transformations.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        
        if title:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        
        # Create grid
        plane = NumberPlane(
            x_range=[-5, 5, 1],
            y_range=[-4, 4, 1],
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.5
            }
        )
        
        # Basis vectors
        i_hat = Arrow(ORIGIN, RIGHT * 2, color=GREEN, buff=0, stroke_width=6)
        j_hat = Arrow(ORIGIN, UP * 2, color=RED, buff=0, stroke_width=6)
        i_label = MathTex(r"\hat{i}", color=GREEN).next_to(i_hat, DOWN)
        j_label = MathTex(r"\hat{j}", color=RED).next_to(j_hat, LEFT)
        
        self.play(Create(plane), run_time=1)
        self.play(
            GrowArrow(i_hat), GrowArrow(j_hat),
            FadeIn(i_label), FadeIn(j_label),
            run_time=1
        )
        self.wait(0.5)
        
        # Get transformation matrix
        matrix = data.get("matrix", [[2, 1], [0, 2]])
        
        # Show matrix
        matrix_tex = MathTex(
            r"\begin{bmatrix}" +
            f"{matrix[0][0]} & {matrix[0][1]}" + r"\\" +
            f"{matrix[1][0]} & {matrix[1][1]}" +
            r"\end{bmatrix}",
            color=YELLOW
        ).scale(0.8)
        matrix_tex.to_corner(UL).shift(DOWN * 0.5)
        self.play(FadeIn(matrix_tex), run_time=0.5)
        
        # Apply transformation
        self.play(
            plane.animate.apply_matrix(matrix),
            i_hat.animate.apply_matrix(matrix),
            j_hat.animate.apply_matrix(matrix),
            run_time=2.5,
            rate_func=smooth
        )
        
        self.wait(2.5)


class ComplexPlaneScene(Scene):
    """
    Complex Plane Scene - 25-35 seconds.
    Visualize complex numbers and operations.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        
        if title:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        
        # Complex plane
        plane = ComplexPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 3, 1],
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.4
            }
        )
        
        # Labels
        re_label = MathTex(r"\text{Re}", color=BLUE_C).next_to(plane.get_right(), DOWN)
        im_label = MathTex(r"\text{Im}", color=BLUE_C).next_to(plane.get_top(), LEFT)
        
        self.play(Create(plane), run_time=1)
        self.play(FadeIn(re_label), FadeIn(im_label), run_time=0.4)
        
        # Complex numbers to visualize
        numbers = data.get("complex_numbers", [2+1j, -1+2j, 1.5-1j])
        colors = [YELLOW, RED, GREEN, BLUE, ORANGE]
        
        for i, z in enumerate(numbers):
            if isinstance(z, list):
                z = complex(z[0], z[1])
            
            color = colors[i % len(colors)]
            point = Dot(plane.n2p(z), color=color, radius=0.12)
            point_glow = Dot(plane.n2p(z), color=color, radius=0.25, fill_opacity=0.3)
            
            # Vector from origin
            arrow = Arrow(
                plane.n2p(0),
                plane.n2p(z),
                color=color,
                buff=0,
                stroke_width=4
            )
            
            label = MathTex(f"{z.real:.1f} + {z.imag:.1f}i", color=color).scale(0.5)
            label.next_to(point, UR, buff=0.1)
            
            self.play(
                GrowArrow(arrow),
                FadeIn(point_glow),
                FadeIn(point),
                run_time=0.8
            )
            self.play(FadeIn(label), run_time=0.3)
            self.wait(0.3)
        
        # Show unit circle if requested
        if data.get("show_unit_circle", False):
            unit_circle = Circle(radius=plane.get_x_unit_size(), color=WHITE, stroke_width=2)
            self.play(Create(unit_circle), run_time=1)
        
        self.wait(2.5)


class ParametricCurveScene(Scene):
    """
    Parametric Curve Scene - 25-35 seconds.
    Animated parametric curves with tracing dots.
    """
    
    def __init__(self, scene_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.scene_data = scene_data
    
    def construct(self):
        data = self.scene_data
        title = data.get("title", "")
        curve_type = data.get("curve_type", "lissajous")
        
        if title:
            title_text = Text(title, font_size=36, color=WHITE, weight=BOLD)
            title_text.to_edge(UP, buff=0.3)
            self.play(FadeIn(title_text, shift=DOWN * 0.2), run_time=0.5)
        
        # Subtle grid
        grid = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-4, 4, 1],
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 0.5,
                "stroke_opacity": 0.2
            }
        )
        self.play(FadeIn(grid), run_time=0.4)
        
        # Define curves
        if curve_type == "lissajous":
            a, b = data.get("a", 3), data.get("b", 2)
            curve = ParametricFunction(
                lambda t: np.array([3 * np.sin(a * t), 2.5 * np.sin(b * t), 0]),
                t_range=[0, TAU],
                color=YELLOW,
                stroke_width=3
            )
        elif curve_type == "epicycloid":
            R, r = 3, 1
            curve = ParametricFunction(
                lambda t: np.array([
                    (R + r) * np.cos(t) - r * np.cos((R + r) * t / r),
                    (R + r) * np.sin(t) - r * np.sin((R + r) * t / r),
                    0
                ]) * 0.6,
                t_range=[0, 2 * PI],
                color=YELLOW,
                stroke_width=3
            )
        elif curve_type == "heart":
            curve = ParametricFunction(
                lambda t: np.array([
                    16 * np.sin(t)**3,
                    13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t),
                    0
                ]) * 0.15,
                t_range=[0, TAU],
                color=RED,
                stroke_width=3
            )
        elif curve_type == "spiral":
            curve = ParametricFunction(
                lambda t: np.array([
                    (0.2 + 0.4 * t) * np.cos(4 * t),
                    (0.2 + 0.4 * t) * np.sin(4 * t),
                    0
                ]),
                t_range=[0, 3 * PI],
                color=YELLOW,
                stroke_width=3
            )
        else:  # circle
            curve = ParametricFunction(
                lambda t: np.array([2.5 * np.cos(t), 2.5 * np.sin(t), 0]),
                t_range=[0, TAU],
                color=YELLOW,
                stroke_width=3
            )
        
        # Tracer dot
        tracer = Dot(color=RED, radius=0.15)
        tracer.move_to(curve.get_start())
        trace = TracedPath(tracer.get_center, stroke_color=YELLOW, stroke_width=3)
        
        self.add(trace)
        self.play(FadeIn(tracer, scale=0.5), run_time=0.4)
        
        # Animate tracing
        self.play(
            MoveAlongPath(tracer, curve),
            run_time=5,
            rate_func=linear
        )
        
        # Pulse at end
        self.play(tracer.animate.scale(1.5), run_time=0.2)
        self.play(tracer.animate.scale(1/1.5), run_time=0.2)
        
        self.wait(2)
