from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.api.routes import router as api_router
from app.api.tutor_orchestrated import router as tutor_orchestrated_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create output directories
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    
    # Mount static files for videos after directories exist
    app.mount("/videos", StaticFiles(directory=settings.OUTPUT_DIR), name="videos")
    
    print("✅ Visual Explainer Generator API started")
    print(f"   Output directory: {settings.OUTPUT_DIR}")
    print(f"   LLM Provider: {settings.LLM_PROVIDER}")
    yield
    # Shutdown
    print("👋 Shutting down API")


app = FastAPI(
    title="Visual Explainer Generator",
    description="Generate visual explainer videos for math & technical concepts",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(tutor_orchestrated_router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "message": "Visual Explainer Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}