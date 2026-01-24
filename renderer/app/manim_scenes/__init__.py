"""
Manim scenes package - Contains all scene types for video generation.
"""
from .base_scene import render_scene, Graph2DScene, VectorArrowsScene, DotsPathsScene, TextLabelsScene
from .graph_2d import Graph2D, GradientDescentGraph
from .vector_arrows import VectorArrows, VectorAddition
from .dots_paths import DotsPaths, GradientDescentPath
from .text_labels import TextLabels, TextLabelScene, MathDerivation, ConceptExplanation

__all__ = [
    "render_scene",
    "Graph2DScene",
    "VectorArrowsScene",
    "DotsPathsScene",
    "TextLabelsScene",
    "Graph2D",
    "GradientDescentGraph",
    "VectorArrows",
    "VectorAddition",
    "DotsPaths",
    "GradientDescentPath",
    "TextLabels",
    "TextLabelScene",
    "MathDerivation",
    "ConceptExplanation",
]