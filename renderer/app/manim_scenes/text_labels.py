"""
TextLabels Scene - Manim scene for text and mathematical notation.
"""
from manim import *


class TextLabels(Scene):
    """Scene for displaying text and mathematical labels."""
    
    CONFIG = {
        "title": "Title",
        "content": [],  # List of strings or math expressions
        "show_math": True,
        "animations": ["write"]  # write, fade, transform
    }
    
    def construct(self):
        config = self.CONFIG
        
        # Title
        title = Text(config["title"], font_size=40, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.7)
        
        # Content items
        items = config.get("content", [])
        if not items:
            items = ["Default content"]
        
        prev_mob = title
        for i, item in enumerate(items):
            # Check if it's a math expression (starts with $ or contains \)
            if item.startswith("$") or "\\" in item:
                text_item = item.strip("$")
                mob = MathTex(text_item, font_size=32)
            else:
                mob = Text(item, font_size=28)
            
            mob.next_to(prev_mob, DOWN, buff=0.5)
            
            animation_type = config.get("animations", ["write"])[0]
            if animation_type == "fade":
                self.play(FadeIn(mob), run_time=0.5)
            elif animation_type == "transform" and prev_mob != title:
                self.play(TransformFromCopy(prev_mob, mob), run_time=0.6)
            else:
                self.play(Write(mob), run_time=0.6)
            
            prev_mob = mob
        
        self.wait(1)


class TextLabelScene(Scene):
    """Backward-compatible scene for simple text display."""
    
    def construct(self):
        label = Text("This is a text label").scale(1.5)
        label.move_to(ORIGIN)
        self.play(Write(label))
        self.wait(2)
        self.play(FadeOut(label))


class MathDerivation(Scene):
    """Scene for showing step-by-step mathematical derivations."""
    
    def construct(self):
        # Title
        title = Text("Derivative of x²", font_size=36, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.5)
        
        # Step 1: Original function
        step1 = MathTex(r"f(x) = x^2", color=WHITE)
        step1.shift(UP * 1.5)
        self.play(Write(step1), run_time=0.6)
        
        # Step 2: Definition of derivative
        step2 = MathTex(
            r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}",
            color=WHITE
        )
        step2.next_to(step1, DOWN, buff=0.5)
        self.play(Write(step2), run_time=0.8)
        
        # Step 3: Substitute
        step3 = MathTex(
            r"= \lim_{h \to 0} \frac{(x+h)^2 - x^2}{h}",
            color=WHITE
        )
        step3.next_to(step2, DOWN, buff=0.4)
        self.play(Write(step3), run_time=0.7)
        
        # Step 4: Expand
        step4 = MathTex(
            r"= \lim_{h \to 0} \frac{x^2 + 2xh + h^2 - x^2}{h}",
            color=WHITE
        )
        step4.next_to(step3, DOWN, buff=0.4)
        self.play(Write(step4), run_time=0.7)
        
        # Step 5: Simplify
        step5 = MathTex(
            r"= \lim_{h \to 0} \frac{2xh + h^2}{h}",
            color=WHITE
        )
        step5.next_to(step4, DOWN, buff=0.4)
        self.play(Write(step5), run_time=0.6)
        
        # Step 6: Factor and cancel
        step6 = MathTex(r"= \lim_{h \to 0} (2x + h)", color=WHITE)
        step6.next_to(step5, DOWN, buff=0.4)
        self.play(Write(step6), run_time=0.6)
        
        # Step 7: Result
        result = MathTex(r"= 2x", color=GREEN, font_size=48)
        result.next_to(step6, DOWN, buff=0.6)
        
        box = SurroundingRectangle(result, color=GREEN, buff=0.2)
        
        self.play(Write(result), Create(box), run_time=0.7)
        
        self.wait(1)


class ConceptExplanation(Scene):
    """Scene for explaining concepts with bullet points."""
    
    CONFIG = {
        "concept_title": "Key Concept",
        "bullet_points": [
            "First important point",
            "Second important point",
            "Third important point"
        ]
    }
    
    def construct(self):
        config = self.CONFIG
        
        # Title
        title = Text(config["concept_title"], font_size=40, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title), run_time=0.6)
        
        # Underline
        underline = Line(
            start=title.get_left() + DOWN * 0.3,
            end=title.get_right() + DOWN * 0.3,
            color=BLUE
        )
        self.play(Create(underline), run_time=0.3)
        
        # Bullet points
        bullets = VGroup()
        for i, point in enumerate(config["bullet_points"]):
            # Bullet marker
            bullet = Dot(radius=0.08, color=YELLOW)
            text = Text(point, font_size=24)
            text.next_to(bullet, RIGHT, buff=0.2)
            
            bullet_group = VGroup(bullet, text)
            if i == 0:
                bullet_group.next_to(underline, DOWN, buff=0.6)
            else:
                bullet_group.next_to(bullets[-1], DOWN, buff=0.3, aligned_edge=LEFT)
            
            bullets.add(bullet_group)
        
        bullets.center().shift(DOWN * 0.5)
        
        for bullet_group in bullets:
            self.play(
                Create(bullet_group[0]),
                Write(bullet_group[1]),
                run_time=0.5
            )
        
        self.wait(1)