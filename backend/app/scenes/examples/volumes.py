from manim import *

class VolumeExample(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=45 * DEGREES)
        
        # 1. Create Shapes
        cube = Cube(side_length=2, fill_opacity=0.5, fill_color=BLUE)
        sphere = Sphere(radius=1, fill_opacity=0.5, fill_color=RED).shift(RIGHT * 3)
        prism = Prism(dimensions=[1, 2, 3], fill_opacity=0.5, fill_color=GREEN).shift(LEFT * 3)
        
        # 2. Labels
        title = Text("3D Volumes").to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        
        # 3. Animate Creation
        self.play(Write(title))
        self.play(
            Create(cube),
            Create(sphere),
            Create(prism)
        )
        
        # 4. Rotate Objects
        self.play(
            Rotate(cube, angle=PI/2, axis=UP),
            Rotate(sphere, angle=PI, axis=RIGHT),
            Rotate(prism, angle=PI/4, axis=OUT),
            run_time=3
        )
        
        self.wait(1)
