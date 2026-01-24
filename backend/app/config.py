from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379/0"
    
    # LLM Provider Selection (auto-detects based on available keys)
    # Priority: nvidia > gemini > groq > openrouter > openai > ollama > fallback
    LLM_PROVIDER: str = "auto"  # auto, nvidia, gemini, groq, openrouter, openai, ollama
    
    # ===== NVIDIA NIM Multi-Agent LLM Configuration =====
    # Future Architecture: Orchestrator assigns specialized jobs to each model
    # - DeepSeek: Reasoning, visual-first pedagogy, script generation
    # - Qwen Coder: Manim code generation, validation, debugging
    
    NVIDIA_API_KEY: Optional[str] = None  # Shared key (fallback)
    
    # DeepSeek V3.2 - Primary reasoning model
    NVIDIA_DEEPSEEK_MODEL: str = "deepseek-ai/deepseek-v3.2"
    NVIDIA_DEEPSEEK_API_KEY: Optional[str] = None
    # Future: NVIDIA_DEEPSEEK_SYSTEM_PROMPT for visual-first pedagogy
    
    # Qwen 2.5 Coder 32B - Code generation specialist
    NVIDIA_QWEN_MODEL: str = "qwen/qwen2.5-coder-32b-instruct"
    NVIDIA_QWEN_API_KEY: Optional[str] = None
    # Future: NVIDIA_QWEN_SYSTEM_PROMPT for Manim code generation
    
    # Legacy support
    NVIDIA_MODEL: str = "deepseek-ai/deepseek-v3.2"
    
    # Google Gemini - https://aistudio.google.com/
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # Groq (fast inference, free tier) - https://console.groq.com/
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # OpenRouter (many models) - https://openrouter.ai/
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "xiaomi/mimo-v2-flash:free"
    
    # OpenAI (optional) - https://platform.openai.com/
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Ollama (local) - http://localhost:11434
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    
    # Legacy compatibility
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    # Video settings - Extended for 10+ minute videos
    MAX_SCENES: int = 100
    MIN_SCENES_REQUIRED: int = 10
    MAX_PROMPT_LENGTH: int = 1000
    TARGET_GENERATION_TIME: int = 600  # 10 minutes
    RENDER_TIMEOUT: int = 60  # seconds per scene
    
    # Storage settings
    OUTPUT_DIR: str = "/app/outputs"
    TEMP_DIR: str = "/app/temp"
    
    # Video output settings
    VIDEO_RESOLUTION: str = "1080p"
    VIDEO_WIDTH: int = 1920
    VIDEO_HEIGHT: int = 1080
    VIDEO_FPS: int = 30
    
    # Frontend URL for CORS
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)