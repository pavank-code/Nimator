from manim import *

class MediaDisplayExample(Scene):
    def construct(self):
        # Note: In a real environment, we'd need actual asset files.
        # This script assumes placeholder assets or standard SVGs if available.
        # For demonstration, we create "proxy" objects that behave like images.
        
        # 1. Image Mockup
        # In real code: img = ImageMobject("path/to/image.png")
        img_rect = Rectangle(height=4, width=6, fill_color=BLUE, fill_opacity=1)
        img_label = Text("Image Placeholder").move_to(img_rect)
        image_group = VGroup(img_rect, img_label)
        
        self.play(FadeIn(image_group))
        self.play(image_group.animate.scale(0.5).to_edge(LEFT))
        
        # 2. SVG Mockup
        # In real code: svg = SVGMobject("path/to/icon.svg")
        # We simulate SVG drawing with a text object (which is essentially paths)
        svg_sim = Text("SVG Icon", font_size=64, color=RED).to_edge(RIGHT)
        
        self.play(Write(svg_sim)) # Write animates paths just like SVG drawing
        
        self.wait(1)
        
        # 3. Caption
        caption = Text("Displaying External Media").to_edge(DOWN)
        self.play(Write(caption))
        
        self.wait(2)
