from manim import *

class LinearAlgebraExample(LinearTransformationScene):
    def construct(self):
        # Built-in methods for LinearTransformationScene
        
        # 1. Show Grid
        # (Implicitly shown by default in this scene type, but we can animate its setup)
        
        # 2. Apply Matrix
        # Matrix [[2, 1], [-1, 1]]
        # Stretches x by 2, skews y
        matrix = [[2, 1], [-1, 1]]
        
        title = Text("Linear Transformation: matrix [[2, 1], [-1, 1]]").to_corner(UL).scale(0.6)
        self.add_foreground_mobject(title)
        
        self.wait(1)
        self.apply_matrix(matrix)
        self.wait(2)
        
        # 3. Moving Vectors
        # Show a vector being transformed
        v = [-1, 1, 0] # A vector in the distorted space
        vec = Vector(v, color=RED)
        
        # Since the grid is already transformed, adding a vector now places it in the transformed system?
        # Actually standard Vector is in global coords.
        # But typically we show the vector BEFORE transformation.
        
        # Let's reset and show a vector transforming
        self.apply_inverse(matrix) # Reset (Hack for demo)
        self.wait(1)
        
        self.add_vector(vec)
        self.play(
             ApplyPointwiseFunction(
                lambda point: np.dot(point, np.array(matrix).T),
                vec
            )
        )
        self.apply_matrix(matrix) # Apply to grid again matching the vector
        
        self.wait(2)
