from manim import *

class CameraControlExample(ThreeDScene):
    def construct(self):
        # 1. Setup Scene
        axes = ThreeDAxes()
        circle = Circle(radius=2, color=RED).rotate(PI/2, axis=RIGHT)
        square = Square(side_length=2, color=BLUE).shift(UP * 2)
        
        self.add(axes, circle, square)
        
        # 2. Camera Move 1: Zoom In
        self.play(
            self.camera.frame.animate.set(width=5),
            run_time=2
        )
        
        # 3. Camera Move 2: Rotate around (Phi/Theta)
        self.move_camera(phi=75 * DEGREES, theta=45 * DEGREES, run_time=2)
        
        # 4. Camera Move 3: Fly through
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(2)
        self.stop_ambient_camera_rotation()
        
        # Reset
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=2)
