from manim import *

class AdvancedMathExample(Scene):
    def construct(self):
        # 1. Complex LaTeX
        equation = MathTex(
            r"\oint_C \vec{E} \cdot d\vec{l} = -\frac{d}{dt} \iint_S \vec{B} \cdot d\vec{S}"
        )
        self.play(Write(equation))
        self.wait(1)
        
        # 2. Equation Transformation
        # Highlight the 'd/dt' part
        frame = SurroundingRectangle(equation[0][7:11], buff=0.1)
        self.play(Create(frame))
        
        explanation = Text("Rate of change of Magnetic Flux", font_size=24)
        explanation.next_to(frame, DOWN)
        self.play(Write(explanation))
        
        self.wait(2)
        self.play(FadeOut(frame), FadeOut(explanation), FadeOut(equation))
        
        # 3. Code Block
        code = Code(
            code="""
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)
""",
            tab_width=4,
            background="window",
            language="Python",
            font="Monospace",
            style="monokai"
        )
        self.play(Create(code))
        self.wait(2)
