# Constants for the Visual Explainer Generator

# Maximum length for user prompts
MAX_PROMPT_LENGTH = 300

# Supported topics
SUPPORTED_TOPICS = [
    "Mathematics",
    "Machine Learning",
    "Algorithms",
    "Physics"
]

# Video generation settings
VIDEO_RESOLUTION = "1080p"
VIDEO_FPS = 30
MIN_SCENES_REQUIRED = 3

# Error messages
INVALID_TOPIC_MESSAGE = "This MVP currently supports math & technical concepts only."
HALLUCINATION_BLOCK_MESSAGE = "The generated content contains undefined concepts."

# Timeouts
RENDER_TIMEOUT = 20  # seconds per scene
TARGET_GENERATION_TIME = 120  # seconds for total generation time

# File settings
TEMP_STORAGE_PATH = "/tmp/explainer_videos"
AUTO_DELETE_AFTER_DOWNLOAD = True