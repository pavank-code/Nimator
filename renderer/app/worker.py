"""
Renderer Worker
Processes video generation jobs from Redis queue.
"""
import os
import sys
import json
import time
import redis
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.manim_scenes.base_scene import render_scene
from app.tts.voiceover import VoiceoverGenerator
from app.assembler.video_assembler import VideoAssembler


class RendererConfig:
    """Configuration for the renderer worker."""
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/outputs")
    TEMP_DIR = os.getenv("TEMP_DIR", "/app/temp")
    RENDER_TIMEOUT = int(os.getenv("RENDER_TIMEOUT", 600))  # 10 min per scene for 15+ min videos
    VIDEO_FPS = int(os.getenv("VIDEO_FPS", 60))  # Smooth 60fps
    VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", 1920))
    VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", 1080))
    MAX_SCENES = int(os.getenv("MAX_SCENES", 150))  # Support up to 150 scenes for 15+ min videos
    ASSEMBLY_TIMEOUT = int(os.getenv("ASSEMBLY_TIMEOUT", 1800))  # 30 min for final assembly


class RenderWorker:
    """
    Worker that processes render jobs from Redis queue.
    """
    
    def __init__(self):
        self.config = RendererConfig()
        self.redis = redis.Redis(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
            decode_responses=True
        )
        self.voiceover = VoiceoverGenerator(self.config.TEMP_DIR)
        self.assembler = VideoAssembler(
            self.config.TEMP_DIR,
            self.config.OUTPUT_DIR,
            fps=self.config.VIDEO_FPS
        )
        
        # Create directories
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.config.TEMP_DIR, exist_ok=True)
        
        print(f"✅ Renderer worker initialized")
        print(f"   Output dir: {self.config.OUTPUT_DIR}")
        print(f"   Temp dir: {self.config.TEMP_DIR}")
    
    def run(self):
        """Main worker loop."""
        print("🎬 Renderer worker started, waiting for jobs...")
        
        while True:
            try:
                # Blocking pop from queue
                result = self.redis.brpop("render_queue", timeout=5)
                
                if result:
                    _, job_data = result
                    job = json.loads(job_data)
                    self.process_job(job)
                    
            except redis.ConnectionError:
                print("❌ Redis connection error, retrying in 5s...")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Worker error: {e}")
                traceback.print_exc()
                time.sleep(1)
    
    def process_job(self, job: Dict[str, Any]):
        """Process a single render job."""
        job_id = job.get("job_id")
        print(f"\n🎬 Processing job: {job_id}")
        
        try:
            # Update status to processing
            self.update_job_status(job_id, "processing", progress=5)
            
            scenes = job.get("scenes", [])
            if not scenes:
                raise ValueError("No scenes to render")
            
            # Step 1: Generate voiceovers (20% progress)
            print(f"   🔊 Generating voiceovers...")
            audio_files = []
            for i, scene in enumerate(scenes):
                narration = scene.get("narration", "")
                if narration and narration != "...":
                    audio_path = self.voiceover.generate(narration, f"{job_id}_scene_{i}")
                    audio_files.append(audio_path)
                else:
                    audio_files.append(None)
                
                progress = 5 + int((i + 1) / len(scenes) * 15)
                self.update_job_status(job_id, "processing", progress=progress)
            
            # Step 2: Render scenes (20-80% progress)
            print(f"   🎨 Rendering {len(scenes)} scenes...")
            scene_videos = []
            successful_scenes = 0
            
            for i, scene in enumerate(scenes):
                print(f"      Scene {i+1}/{len(scenes)}: {scene.get('scene_type', 'unknown')}")
                
                try:
                    video_path = render_scene(
                        scene,
                        job_id,
                        i,
                        self.config.TEMP_DIR,
                        timeout=self.config.RENDER_TIMEOUT
                    )
                    if video_path and os.path.exists(video_path):
                        scene_videos.append(video_path)
                        successful_scenes += 1
                    else:
                        print(f"      ⚠️ Scene {i+1} render returned no video")
                        scene_videos.append(None)
                except Exception as e:
                    print(f"      ❌ Scene {i+1} failed: {e}")
                    scene_videos.append(None)
                
                progress = 20 + int((i + 1) / len(scenes) * 60)
                self.update_job_status(job_id, "processing", progress=progress)
            
            # Check if we have at least one scene
            if successful_scenes < 1:
                raise ValueError(f"No scenes rendered successfully. Please try again.")
            
            print(f"   ✅ {successful_scenes}/{len(scenes)} scenes rendered successfully")
            
            # Step 3: Assemble final video (80-95% progress)
            print(f"   🎞️ Assembling final video...")
            self.update_job_status(job_id, "processing", progress=85)
            
            final_video = self.assembler.assemble(
                job_id,
                scene_videos,
                audio_files
            )
            
            if not final_video or not os.path.exists(final_video):
                raise ValueError("Failed to assemble final video")
            
            # Step 4: Cleanup and complete
            print(f"   🧹 Cleaning up temp files...")
            self.update_job_status(job_id, "processing", progress=95)
            self.cleanup_temp_files(job_id, scene_videos, audio_files)
            
            # Mark as completed
            video_url = f"/videos/{job_id}.mp4"
            self.update_job_status(
                job_id,
                "completed",
                progress=100,
                video_url=video_url
            )
            print(f"   ✅ Job {job_id} completed: {video_url}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Job {job_id} failed: {error_msg}")
            traceback.print_exc()
            self.update_job_status(
                job_id,
                "failed",
                error_message=error_msg
            )
    
    def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: int = None,
        error_message: str = None,
        video_url: str = None
    ):
        """Update job status in Redis."""
        try:
            data = self.redis.get(f"job:{job_id}")
            if data:
                job = json.loads(data)
                job["status"] = status
                job["updated_at"] = datetime.utcnow().isoformat()
                
                if progress is not None:
                    job["progress"] = progress
                if error_message is not None:
                    job["error_message"] = error_message
                if video_url is not None:
                    job["video_url"] = video_url
                
                self.redis.set(f"job:{job_id}", json.dumps(job), ex=3600)
        except Exception as e:
            print(f"Failed to update job status: {e}")
    
    def cleanup_temp_files(
        self,
        job_id: str,
        scene_videos: List[Optional[str]],
        audio_files: List[Optional[str]]
    ):
        """Clean up temporary files after job completion."""
        for path in scene_videos + audio_files:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        
        # Clean up any other temp files for this job
        temp_pattern = os.path.join(self.config.TEMP_DIR, f"{job_id}*")
        import glob
        for f in glob.glob(temp_pattern):
            try:
                if os.path.isfile(f):
                    os.remove(f)
            except:
                pass


def main():
    """Entry point for the worker."""
    worker = RenderWorker()
    worker.run()


if __name__ == "__main__":
    main()