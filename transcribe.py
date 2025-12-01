import os
import logging
import wave
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import librosa
import soundfile
from faster_whisper import WhisperModel

from utils import create_markdown
from config import (
    WHISPER_MODEL, 
    TRANSCRIPTION_FOLDER, 
    SUPPORTED_LANGUAGES, 
    DEFAULT_LANGUAGE, 
    ENSURE_UTF8_ENCODING, 
    OUTPUT_ENCODING
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioTranscriber:
    """
    High-Performance Audio Transcriber using faster-whisper (CTranslate2).
    Delivers up to 4x faster transcription with lower memory usage.
    """
    
    def __init__(self, model_size: str = WHISPER_MODEL, language: str = DEFAULT_LANGUAGE):
        """
        Initialize the transcriber with the specified Whisper model.
        
        Args:
            model_size: Size of the model (tiny, base, small, medium, large-v2)
            language: Default language code
        """
        logger.info(f"Loading faster-whisper model: {model_size}...")
        try:
            # Use INT8 quantization for CPU speedup, or float16 for GPU if available
            # device="auto" automatically selects CUDA if available
            self.model = WhisperModel(model_size, device="auto", compute_type="int8")
            self.model_size = model_size
            self.supported_formats = {'.mp3', '.wav', '.m4a', '.flac', '.mp4', '.ogg', '.aac', '.wma'}
            self.supported_languages = SUPPORTED_LANGUAGES
            self.language = language
            logger.info(f"Successfully loaded {model_size} model (faster-whisper)")
        except Exception as e:
            logger.error(f"Failed to load faster-whisper model: {e}")
            raise RuntimeError(f"Could not load model '{model_size}': {e}")

    def set_language(self, language: str) -> bool:
        """Set the transcription language."""
        if language not in self.supported_languages and language != 'auto':
            logger.warning(f"Language '{language}' not in supported languages. Using auto-detection.")
            self.language = 'auto'
            return False
        
        self.language = language
        logger.info(f"Language set to: {language}")
        return True

    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages."""
        return self.supported_languages.copy()

    def validate_audio_file(self, audio_path: str) -> bool:
        """Validate if the audio file is supported and accessible."""
        audio = Path(audio_path)
        
        if not audio.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if audio.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {audio.suffix}")
        
        # Check file size (faster-whisper handles larger files better, but let's keep a sane limit)
        # Increased limit to 2GB since we process efficiently
        file_size_mb = audio.stat().st_size / (1024 * 1024)
        if file_size_mb > 2048:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB. Maximum size is 2GB.")
        
        logger.info(f"Audio file validation passed: {audio.name} ({file_size_mb:.1f}MB)")
        return True

    def get_audio_metadata(self, audio_path: str) -> Dict[str, Any]:
        """Extract comprehensive audio metadata."""
        try:
            audio = Path(audio_path)
            file_size = audio.stat().st_size
            
            duration = 0
            try:
                # Try librosa first
                duration = librosa.get_duration(filename=str(audio))
            except Exception:
                try:
                    # Fallback to soundfile
                    info = soundfile.info(str(audio))
                    duration = info.duration
                except Exception:
                    pass
            
            metadata = {
                'filename': audio.name,
                'file_size_mb': file_size / (1024 * 1024),
                'duration_seconds': duration,
                'duration_formatted': f"{int(duration // 60)}:{(duration % 60):02.0f}" if duration else "Unknown",
                'file_extension': audio.suffix.lower()
            }
            return metadata
            
        except Exception as e:
            logger.error(f"Could not extract metadata: {e}")
            return {
                'filename': Path(audio_path).name,
                'file_size_mb': 0,
                'duration_seconds': 0,
                'duration_formatted': "Unknown",
                'file_extension': Path(audio_path).suffix.lower()
            }

    def transcribe_file(self, audio_path: str, progress_callback: Optional[Callable[[str], None]] = None, 
                       formatting_style: str = "auto", language: Optional[str] = None) -> tuple[Path, Dict[str, Any]]:
        """
        Transcribe audio file using faster-whisper with real-time segment tracking.
        """
        start_time = datetime.now()
        
        try:
            self.validate_audio_file(audio_path)
            metadata = self.get_audio_metadata(audio_path)
            
            if progress_callback:
                progress_callback("Initializing transcription...")
            
            logger.info(f"Transcribing: {metadata['filename']}")
            
            # Determine language
            transcription_language = None
            if language and language != 'auto':
                transcription_language = language
            elif self.language and self.language != 'auto':
                transcription_language = self.language
            
            # Transcribe
            # faster-whisper returns a generator
            segments, info = self.model.transcribe(
                str(audio_path),
                beam_size=5,
                language=transcription_language,
                task="transcribe"
            )
            
            if progress_callback:
                progress_callback(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            # Process segments
            transcribed_segments = []
            full_text = []
            
            total_duration = info.duration
            
            for segment in segments:
                transcribed_segments.append({
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })
                full_text.append(segment.text)
                
                # Update progress
                if progress_callback and total_duration > 0:
                    percent = int((segment.end / total_duration) * 100)
                    progress_callback(f"Transcribing: {percent}% ({int(segment.end)}s/{int(total_duration)}s)")
            
            final_text = "".join(full_text).strip()
            
            # Prepare result data
            now = datetime.now()
            processing_time = (now - start_time).total_seconds()
            
            transcription_data = {
                'filename': Path(audio_path).stem,
                'text': final_text,
                'date': now.strftime("%Y-%m-%d %H:%M:%S"),
                'duration': metadata['duration_formatted'],
                'duration_seconds': metadata['duration_seconds'],
                'file_size_mb': metadata['file_size_mb'],
                'model': self.model_size,
                'language': info.language,
                'segments': transcribed_segments,
                'formatting_style': formatting_style,
                'processing_time_seconds': processing_time,
                'characters_per_second': len(final_text) / processing_time if processing_time > 0 else 0
            }
            
            # Save to Markdown
            markdown_text = create_markdown(**transcription_data)
            TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)
            
            output_path = TRANSCRIPTION_FOLDER / f"{Path(audio_path).stem}.md"
            
            # Atomic write
            temp_path = output_path.with_suffix('.tmp')
            encoding = OUTPUT_ENCODING if ENSURE_UTF8_ENCODING else "utf-8"
            temp_path.write_text(markdown_text, encoding=encoding)
            if output_path.exists():
                output_path.unlink()
            temp_path.rename(output_path)
            
            if progress_callback:
                progress_callback("✓ Transcription completed!")
            
            logger.info(f"Completed in {processing_time:.1f}s")
            return output_path, transcription_data
            
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"Error: {str(e)}")
            raise Exception(error_msg)
