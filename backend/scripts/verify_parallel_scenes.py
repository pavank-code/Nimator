import sys
import os
import asyncio
import time
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock config before importing anything that uses it
sys.modules["app.config"] = MagicMock()
sys.modules["app.config"].settings = MagicMock()

# Mock fastapi
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()

# Mock httpx
sys.modules["httpx"] = MagicMock()

# Mock app.services.topic_classifier module BEFORE importing ManimCodeGenerator
mock_topic_classifier = MagicMock()
sys.modules["app.services.topic_classifier"] = mock_topic_classifier

# Create a Mock LLMClient class
class MockLLMClient:
    def __init__(self):
        self.provider = "mock"

    async def chat_code(self, prompt, temperature=0.1, max_tokens=1000):
        await asyncio.sleep(0.5) # Simulate network latency
        return '{"scene_type": "graph_2d", "function": "x**2"}'

mock_topic_classifier.LLMClient = MockLLMClient

# Now we can import the service
from app.services.manim_code_generator import ManimCodeGenerator

async def run_benchmark():
    generator = ManimCodeGenerator()

    # 4 scenes
    script = {
        "scenes": [
            {"scene_number": 1, "visual_type": "graph_2d", "voiceover": "one"},
            {"scene_number": 2, "visual_type": "graph_2d", "voiceover": "two"},
            {"scene_number": 3, "visual_type": "graph_2d", "voiceover": "three"},
            {"scene_number": 4, "visual_type": "graph_2d", "voiceover": "four"},
        ]
    }

    print("Starting generation...")
    start = time.time()
    scenes = await generator.generate_scenes(script)
    end = time.time()

    duration = end - start
    print(f"Generated {len(scenes)} scenes in {duration:.2f} seconds")

    # Validation
    if len(scenes) != 4:
        print("ERROR: Generated incorrect number of scenes")
        sys.exit(1)

    # Check if we got the "happy path" result
    happy_path_count = 0
    for scene in scenes:
        if scene.get("function") == "x**2":
            happy_path_count += 1

    print(f"Happy path scenes: {happy_path_count}/4")

    if happy_path_count != 4:
        print("ERROR: Fallback mechanism triggered for some scenes (or logic failed)")
        sys.exit(1)

    return duration

if __name__ == "__main__":
    asyncio.run(run_benchmark())
