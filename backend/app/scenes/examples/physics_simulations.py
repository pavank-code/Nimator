from manim import *

class PhysicsExample(Scene):
    def construct(self):
        # 1. Pendulum Simulation
        # Simple harmonic motion visualization
        ceiling = Line(LEFT, RIGHT)
        pendulum_len = 3
        theta_max = 30 * DEGREES
        
        pivot = Dot(color=WHITE)
        bob = Dot(color=RED, radius=0.2)
        string = Line(pivot.get_center(), bob.get_center())
        
        # Group them
        pendulum = VGroup(string, bob)
        
        self.add(ceiling, pivot)
        self.play(Create(pendulum))
        
        # Animate Swing
        # We manually animate theta
        dt = 0.05
        t = 0
        
        def update_pendulum(mob, dt):
            nonlocal t
            t += dt * 2
            theta = theta_max * np.cos(t)
            # Position bob relative to pivot
            new_x = pendulum_len * np.sin(theta)
            new_y = -pendulum_len * np.cos(theta)
            
            # Update bob and string
            bob.move_to([new_x, new_y, 0])
            string.put_start_and_end_on(pivot.get_center(), bob.get_center())

        self.play(Write(Text("Pendulum Simulation").to_corner(UL)))
        
        # Add updater
        pendulum.add_updater(update_pendulum)
        self.wait(5)
        pendulum.remove_updater(update_pendulum)
