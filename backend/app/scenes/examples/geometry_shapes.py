from manim import *

class GeometryShapesExample(Scene):
    def construct(self):
        # 1. Morphing: Square -> Circle -> Triangle
        square = Square(color=RED, fill_opacity=0.5)
        circle = Circle(color=BLUE, fill_opacity=0.5)
        triangle = Triangle(color=GREEN, fill_opacity=0.5)
        
        self.play(Create(square))
        self.wait(0.5)
        
        # Transform Square to Circle
        self.play(Transform(square, circle))
        self.wait(0.5)
        
        # Transform Circle to Triangle
        self.play(Transform(square, triangle)) 
        # Note: 'square' variable now holds the circle/triangle mobject visually
        self.wait(0.5)
        self.play(FadeOut(square))
        
        # 2. Boolean Operations
        c1 = Circle(radius=1.5).shift(LEFT)
        c2 = Circle(radius=1.5).shift(RIGHT)
        
        union = Union(c1, c2, color=ORANGE, fill_opacity=0.5)
        intersection = Intersection(c1, c2, color=PURPLE, fill_opacity=0.8)
        
        text = Text("Boolean Operations").to_edge(UP)
        self.play(Write(text))
        
        self.play(FadeIn(c1), FadeIn(c2))
        self.wait(1)
        self.play(FadeOut(c1), FadeOut(c2), FadeIn(union))
        self.wait(1)
        self.play(Transform(union, intersection))
        self.wait(1)
