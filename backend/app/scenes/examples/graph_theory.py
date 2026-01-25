from manim import *

class GraphTheoryExample(Scene):
    def construct(self):
        # 1. Create a Graph
        # Nodes: 0, 1, 2, 3, 4
        # Edges match a small network
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 3)]
        
        g = Graph(
            [0, 1, 2, 3, 4],
            edges,
            layout="circular",
            labels=True
        )
        
        self.play(Create(g))
        self.wait(1)
        
        # 2. Change Layout
        self.play(g.animate.change_layout("spring"))
        self.wait(1)
        
        # 3. Highlight a Path (e.g. 0 -> 2 -> 3)
        path_edges = [(0, 2), (2, 3)]
        
        for u, v in path_edges:
            self.play(
                g.edges[(u, v)].animate.set_color(RED).set_stroke(width=6),
                run_time=0.5
            )
            
        self.play(Write(Text("Shortest Path").next_to(g, DOWN)))
        self.wait(2)
