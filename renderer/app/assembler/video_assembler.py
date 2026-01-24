"""
Video Assembler
Combines rendered scene videos and audio into a final MP4.
"""
import os
import subprocess
from typing import List, Optional
import tempfile


class VideoAssembler:
    """
    Assembles multiple scene videos and audio files into a final video.
    Uses FFmpeg for video processing.
    """
    
    def __init__(self, temp_dir: str, output_dir: str, fps: int = 30):
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.fps = fps
        
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
    
    def assemble(
        self,
        job_id: str,
        scene_videos: List[Optional[str]],
        audio_files: List[Optional[str]]
    ) -> Optional[str]:
        """
        Assemble scene videos and audio into final output.
        Returns path to final video or None on failure.
        """
        # Filter out None values but keep track of indices
        valid_videos = [(i, v) for i, v in enumerate(scene_videos) if v and os.path.exists(v)]
        
        if not valid_videos:
            print("No valid scene videos to assemble")
            return None
        
        output_path = os.path.join(self.output_dir, f"{job_id}.mp4")
        
        try:
            if len(valid_videos) == 1:
                # Single video - just process it with audio if available
                _, video_path = valid_videos[0]
                idx = _
                audio_path = audio_files[idx] if idx < len(audio_files) else None
                return self._process_single_video(video_path, audio_path, output_path)
            else:
                # Multiple videos - concatenate then add audio
                return self._concatenate_and_merge(valid_videos, audio_files, output_path)
                
        except Exception as e:
            print(f"Video assembly error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _process_single_video(
        self,
        video_path: str,
        audio_path: Optional[str],
        output_path: str
    ) -> Optional[str]:
        """Process a single video with optional audio."""
        try:
            if audio_path and os.path.exists(audio_path):
                # Merge video with audio
                cmd = [
                    "ffmpeg", "-y",
                    "-i", video_path,
                    "-i", audio_path,
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    "-preset", "fast",
                    "-crf", "23",
                    output_path
                ]
            else:
                # Just re-encode the video
                cmd = [
                    "ffmpeg", "-y",
                    "-i", video_path,
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "23",
                    "-an",  # No audio
                    output_path
                ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                return None
            
            return output_path if os.path.exists(output_path) else None
            
        except Exception as e:
            print(f"Single video processing error: {e}")
            return None
    
    def _concatenate_and_merge(
        self,
        valid_videos: List[tuple],
        audio_files: List[Optional[str]],
        output_path: str
    ) -> Optional[str]:
        """Concatenate multiple videos and merge with audio."""
        try:
            # Step 1: Create concat list file
            concat_file = os.path.join(self.temp_dir, f"concat_{os.path.basename(output_path)}.txt")
            
            with open(concat_file, 'w') as f:
                for idx, video_path in valid_videos:
                    # Use absolute path and escape for ffmpeg
                    abs_path = os.path.abspath(video_path).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
            
            # Step 2: Concatenate videos
            concat_output = os.path.join(self.temp_dir, f"concat_{os.path.basename(output_path)}")
            
            concat_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-r", str(self.fps),
                "-pix_fmt", "yuv420p",
                concat_output
            ]
            
            result = subprocess.run(
                concat_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for longer videos
            )
            
            if result.returncode != 0:
                print(f"Concat error: {result.stderr}")
                # Try alternative concat method
                return self._concatenate_filter_complex(valid_videos, audio_files, output_path)
            
            # Step 3: Merge combined audio if available
            combined_audio = self._merge_audio_files(valid_videos, audio_files)
            
            if combined_audio and os.path.exists(combined_audio):
                # Add audio to concatenated video
                final_cmd = [
                    "ffmpeg", "-y",
                    "-i", concat_output,
                    "-i", combined_audio,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    output_path
                ]
                
                result = subprocess.run(
                    final_cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Cleanup temp audio
                if os.path.exists(combined_audio):
                    os.remove(combined_audio)
                
                if result.returncode != 0:
                    print(f"Audio merge error: {result.stderr}")
                    # Just use the video without audio
                    import shutil
                    shutil.copy2(concat_output, output_path)
            else:
                # No audio, just copy concatenated video
                import shutil
                shutil.copy2(concat_output, output_path)
            
            # Cleanup
            if os.path.exists(concat_file):
                os.remove(concat_file)
            if os.path.exists(concat_output):
                os.remove(concat_output)
            
            return output_path if os.path.exists(output_path) else None
            
        except Exception as e:
            print(f"Concatenation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _concatenate_filter_complex(
        self,
        valid_videos: List[tuple],
        audio_files: List[Optional[str]],
        output_path: str
    ) -> Optional[str]:
        """Alternative concatenation using filter_complex."""
        try:
            # Build filter complex command
            inputs = []
            filter_parts = []
            
            for i, (idx, video_path) in enumerate(valid_videos):
                inputs.extend(["-i", video_path])
                filter_parts.append(f"[{i}:v]")
            
            filter_str = "".join(filter_parts) + f"concat=n={len(valid_videos)}:v=1:a=0[outv]"
            
            cmd = [
                "ffmpeg", "-y"
            ] + inputs + [
                "-filter_complex", filter_str,
                "-map", "[outv]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes for longer videos
            )
            
            if result.returncode != 0:
                print(f"Filter complex error: {result.stderr}")
                # Last resort: just use the first video
                import shutil
                shutil.copy2(valid_videos[0][1], output_path)
            
            return output_path if os.path.exists(output_path) else None
            
        except Exception as e:
            print(f"Filter complex error: {e}")
            return None
    
    def _merge_audio_files(
        self,
        valid_videos: List[tuple],
        audio_files: List[Optional[str]]
    ) -> Optional[str]:
        """Merge audio files corresponding to valid videos."""
        try:
            # Get valid audio files
            valid_audio = []
            for idx, _ in valid_videos:
                if idx < len(audio_files) and audio_files[idx] and os.path.exists(audio_files[idx]):
                    valid_audio.append(audio_files[idx])
            
            if not valid_audio:
                return None
            
            if len(valid_audio) == 1:
                return valid_audio[0]
            
            # Concatenate audio files
            output_audio = os.path.join(self.temp_dir, "combined_audio.mp3")
            
            # Create concat list
            audio_list = os.path.join(self.temp_dir, "audio_concat.txt")
            with open(audio_list, 'w') as f:
                for audio in valid_audio:
                    abs_path = os.path.abspath(audio).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", audio_list,
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                output_audio
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Cleanup
            if os.path.exists(audio_list):
                os.remove(audio_list)
            
            if result.returncode != 0:
                print(f"Audio merge error: {result.stderr}")
                return None
            
            return output_audio if os.path.exists(output_audio) else None
            
        except Exception as e:
            print(f"Audio merge error: {e}")
            return None