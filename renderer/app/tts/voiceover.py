"""
Text-to-Speech Voiceover Generator
Uses Deepgram for high-quality AI voice generation.
Falls back to gTTS if Deepgram is unavailable.
"""
import os
import httpx
from typing import Optional
from gtts import gTTS
from pydub import AudioSegment
import hashlib


class VoiceoverGenerator:
    """
    Generates voiceover audio from narration text.
    Uses Deepgram Aura for high-quality AI voices.
    """
    
    # Deepgram Aura voices - natural sounding AI voices
    DEEPGRAM_VOICES = [
        "aura-asteria-en",   # Female, warm and professional
        "aura-luna-en",      # Female, friendly and expressive
        "aura-stella-en",    # Female, calm and articulate
        "aura-athena-en",    # Female, authoritative
        "aura-hera-en",      # Female, warm and nurturing
        "aura-orion-en",     # Male, deep and authoritative
        "aura-arcas-en",     # Male, friendly and conversational
        "aura-perseus-en",   # Male, clear and professional
        "aura-angus-en",     # Male, warm Scottish accent
        "aura-orpheus-en",   # Male, smooth and engaging
        "aura-helios-en",    # Male, energetic and bright
        "aura-zeus-en",      # Male, powerful and commanding
    ]
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Deepgram API configuration
        self.deepgram_api_key = os.environ.get("DEEPGRAM_API_KEY", "")
        self.deepgram_voice = "aura-orion-en"  # Default to Orion - deep, clear, professional
        self.use_deepgram = bool(self.deepgram_api_key)
        
        # Fallback gTTS settings
        self.language = "en"
        self.slow = False
        
        if self.use_deepgram:
            print(f"🎙️ Using Deepgram TTS with voice: {self.deepgram_voice}")
        else:
            print("⚠️ No Deepgram API key - falling back to gTTS")
    
    def generate(self, text: str, file_prefix: str) -> Optional[str]:
        """
        Generate voiceover audio from text.
        Returns the path to the generated audio file.
        """
        if not text or text.strip() == "..." or len(text.strip()) < 3:
            return None
        
        # Clean up text for TTS
        clean_text = self._clean_text(text)
        
        # Generate unique filename
        text_hash = hashlib.md5(clean_text.encode()).hexdigest()[:8]
        output_path = os.path.join(self.output_dir, f"{file_prefix}_{text_hash}.mp3")
        
        # Check if already generated (caching)
        if os.path.exists(output_path):
            return output_path
        
        # Try Deepgram first, then fall back to gTTS
        if self.use_deepgram:
            result = self._generate_deepgram(clean_text, output_path)
            if result:
                return result
            print("Deepgram failed, falling back to gTTS")
        
        return self._generate_gtts(clean_text, output_path)
    
    def _generate_deepgram(self, text: str, output_path: str) -> Optional[str]:
        """Generate audio using Deepgram Aura TTS."""
        try:
            url = f"https://api.deepgram.com/v1/speak?model={self.deepgram_voice}"
            
            headers = {
                "Authorization": f"Token {self.deepgram_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text
            }
            
            # Use synchronous request for simplicity in worker context
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                # Save the audio content
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return output_path
                    
        except Exception as e:
            print(f"Deepgram TTS error: {e}")
        
        return None
    
    def _generate_gtts(self, text: str, output_path: str) -> Optional[str]:
        """Generate audio using gTTS (fallback)."""
        try:
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            tts.save(output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
                
        except Exception as e:
            print(f"gTTS generation error: {e}")
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for TTS."""
        # Remove LaTeX commands
        import re
        
        # Remove common LaTeX patterns
        text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)  # \command{content} -> content
        text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remove remaining commands
        text = re.sub(r'\{|\}', '', text)  # Remove braces
        text = re.sub(r'\$', '', text)  # Remove dollar signs
        text = re.sub(r'_\{([^}]*)\}', r' sub \1', text)  # Subscripts
        text = re.sub(r'\^\{([^}]*)\}', r' to the power of \1', text)  # Superscripts
        text = re.sub(r'_(\w)', r' sub \1', text)  # Single char subscripts
        text = re.sub(r'\^(\w)', r' to the power of \1', text)  # Single char superscripts
        
        # Replace common math symbols with words
        replacements = {
            '→': ' implies ',
            '←': ' is implied by ',
            '≤': ' less than or equal to ',
            '≥': ' greater than or equal to ',
            '≠': ' not equal to ',
            '=': ' equals ',
            '+': ' plus ',
            '-': ' minus ',
            '*': ' times ',
            '/': ' divided by ',
            '∞': ' infinity ',
            'α': ' alpha ',
            'β': ' beta ',
            'γ': ' gamma ',
            'δ': ' delta ',
            'θ': ' theta ',
            'λ': ' lambda ',
            'σ': ' sigma ',
            '∇': ' gradient of ',
            '∂': ' partial ',
            '∑': ' sum of ',
            '∏': ' product of ',
            '√': ' square root of ',
        }
        
        for symbol, word in replacements.items():
            text = text.replace(symbol, word)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get the duration of an audio file in seconds."""
        try:
            audio = AudioSegment.from_mp3(audio_path)
            return len(audio) / 1000.0  # Convert ms to seconds
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 3.0  # Default duration
    
    def adjust_audio_speed(self, audio_path: str, speed: float = 1.0) -> str:
        """
        Adjust the playback speed of an audio file.
        Returns path to the adjusted file.
        """
        if speed == 1.0:
            return audio_path
        
        try:
            audio = AudioSegment.from_mp3(audio_path)
            
            # Change speed by modifying frame rate
            adjusted = audio._spawn(audio.raw_data, overrides={
                "frame_rate": int(audio.frame_rate * speed)
            }).set_frame_rate(audio.frame_rate)
            
            # Save adjusted audio
            output_path = audio_path.replace(".mp3", f"_speed{speed}.mp3")
            adjusted.export(output_path, format="mp3")
            
            return output_path
        except Exception as e:
            print(f"Error adjusting audio speed: {e}")
            return audio_path
    
    def cleanup(self, file_path: str) -> bool:
        """Remove an audio file."""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error cleaning up audio file: {e}")
        return False


# Module-level functions for backward compatibility
def generate_voiceover(narration_text: str, output_file: str) -> None:
    """Legacy function for generating voiceover."""
    generator = VoiceoverGenerator(os.path.dirname(output_file))
    generator.generate(narration_text, os.path.basename(output_file).replace('.mp3', ''))


def cleanup_audio_file(output_file: str) -> None:
    """Legacy function for cleaning up audio files."""
    if os.path.exists(output_file):
        os.remove(output_file)