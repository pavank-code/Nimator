from manim import *

class ThreeDGraphExample(ThreeDScene):
    def construct(self):
        # 1. Setup Axes
        axes = ThreeDAxes()
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        
        # 2. Text Label
        text3d = Text("3D Surface Plotting").to_corner(UL)
        self.add_fixed_in_frame_mobjects(text3d)
        self.play(Write(text3d))
        
        # 3. Create Surface: z = f(x, y) = cos(x) + sin(y)
        surface = Surface(
            lambda u, v: axes.c2p(u, v, np.cos(u) + np.sin(v)),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(30, 30),
            should_make_jagged=False
        )
        surface.set_style(fill_opacity=0.6)
        surface.set_fill_by_checkerboard(BLUE, BLUE_E, opacity=0.5)
        
        # 4. Animate structure
        self.play(Create(axes))
        self.play(Create(surface))
        
        # 5. Rotate Camera
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(5)
        self.stop_ambient_camera_rotation()
        
        self.play(FadeOut(surface), FadeOut(axes), FadeOut(text3d))
