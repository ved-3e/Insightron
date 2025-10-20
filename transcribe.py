import whisper
from pathlib import Path
from datetime import datetime
import os
import wave
import librosa
import logging
from typing import Dict, Any, Optional, Callable
from utils import create_markdown
from config import WHISPER_MODEL, TRANSCRIPTION_FOLDER, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, ENSURE_UTF8_ENCODING, OUTPUT_ENCODING

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioTranscriber:
    """
    Enhanced Audio Transcriber with improved error handling, performance optimizations,
    and better progress tracking for the Insightron project.
    """
    
    def __init__(self, model_size: str = WHISPER_MODEL, language: str = DEFAULT_LANGUAGE):
        """Initialize the transcriber with the specified Whisper model and language."""
        logger.info(f"Loading Whisper model: {model_size}...")
        try:
            self.model = whisper.load_model(model_size)
            self.model_size = model_size
            self.supported_formats = {'.mp3', '.wav', '.m4a', '.flac', '.mp4', '.ogg', '.aac', '.wma'}
            self.supported_languages = SUPPORTED_LANGUAGES
            self.language = language
            logger.info(f"Successfully loaded {model_size} model with language support: {language}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Could not load Whisper model '{model_size}': {e}")

    def set_language(self, language: str) -> bool:
        """
        Set the transcription language.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr') or 'auto' for auto-detection
            
        Returns:
            True if language is valid and set
        """
        if language not in self.supported_languages:
            logger.warning(f"Language '{language}' not in supported languages. Using auto-detection.")
            self.language = 'auto'
            return False
        
        self.language = language
        logger.info(f"Language set to: {language} ({self.supported_languages[language]})")
        return True

    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get dictionary of supported languages.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return self.supported_languages.copy()

    def validate_audio_file(self, audio_path: str) -> bool:
        """
        Validate if the audio file is supported and accessible.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            True if valid
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported or too large
        """
        audio = Path(audio_path)
        
        if not audio.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if audio.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {audio.suffix}. Supported formats: {', '.join(self.supported_formats)}")
        
        # Check file size (max 25MB for Whisper)
        file_size_mb = audio.stat().st_size / (1024 * 1024)
        if file_size_mb > 25:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB. Maximum size is 25MB.")
        
        logger.info(f"Audio file validation passed: {audio.name} ({file_size_mb:.1f}MB)")
        return True

    def get_audio_metadata(self, audio_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive audio metadata with improved error handling.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary containing audio metadata
        """
        try:
            audio = Path(audio_path)
            file_size = audio.stat().st_size
            
            # Try to get duration using librosa (more reliable)
            duration = None
            try:
                duration = librosa.get_duration(filename=str(audio))
                logger.debug(f"Duration extracted using librosa: {duration:.2f}s")
            except Exception as e:
                logger.warning(f"Librosa duration extraction failed: {e}")
                try:
                    # Fallback to whisper's method
                    duration = whisper.audio.get_duration(str(audio))
                    logger.debug(f"Duration extracted using whisper: {duration:.2f}s")
                except Exception as e2:
                    logger.warning(f"Whisper duration extraction failed: {e2}")
                    duration = 0
            
            metadata = {
                'filename': audio.name,
                'file_size_mb': file_size / (1024 * 1024),
                'duration_seconds': duration or 0,
                'duration_formatted': f"{int(duration // 60)}:{(duration % 60):02.0f}" if duration else "Unknown",
                'file_extension': audio.suffix.lower()
            }
            
            logger.info(f"Metadata extracted: {metadata['filename']} - {metadata['duration_formatted']} - {metadata['file_size_mb']:.1f}MB")
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
        Transcribe audio file with enhanced error handling and progress tracking.
        
        Args:
            audio_path: Path to the audio file to transcribe
            progress_callback: Optional callback function for progress updates
            formatting_style: Text formatting style ('auto', 'paragraphs', 'minimal')
            language: Language code for transcription (e.g., 'en', 'es', 'fr') or None for auto-detection
            
        Returns:
            Tuple of (output_path, transcription_data)
            
        Raises:
            Exception: If transcription fails
        """
        start_time = datetime.now()
        
        try:
            # Validate file
            self.validate_audio_file(audio_path)
            
            # Get metadata
            metadata = self.get_audio_metadata(audio_path)
            
            if progress_callback:
                progress_callback("Starting transcription...")
            
            logger.info(f"Transcribing: {metadata['filename']} - {metadata['duration_formatted']} - {metadata['file_size_mb']:.1f}MB")
            
            # Transcribe with progress tracking
            if progress_callback:
                progress_callback("Processing audio...")
            
            # Determine language for transcription
            transcription_language = None
            if language:
                # Use provided language if valid
                if language in self.supported_languages and language != 'auto':
                    transcription_language = language
                    logger.info(f"Using specified language: {language} ({self.supported_languages[language]})")
                else:
                    logger.info(f"Invalid or auto language specified: {language}, using auto-detection")
            elif self.language and self.language != 'auto':
                # Use instance language if set
                transcription_language = self.language
                logger.info(f"Using instance language: {self.language} ({self.supported_languages[self.language]})")
            else:
                logger.info("Using auto language detection")
            
            # Configure transcription parameters for optimal performance
            transcribe_kwargs = {
                'verbose': False,  # Reduce console output
                'fp16': False,     # Use fp32 for better compatibility
                'language': transcription_language,  # Language or None for auto-detect
                'task': 'transcribe'
            }
            
            # Add model-specific optimizations
            if self.model_size in ['tiny', 'base']:
                transcribe_kwargs['beam_size'] = 1  # Faster for smaller models
            elif self.model_size in ['small', 'medium']:
                transcribe_kwargs['beam_size'] = 5  # Balanced for medium models
            else:  # large
                transcribe_kwargs['beam_size'] = 5  # Conservative for large model
            
            result = self.model.transcribe(str(audio_path), **transcribe_kwargs)
            
            if progress_callback:
                progress_callback("Generating transcript...")
            
            # Prepare transcription data
            now = datetime.now()
            processing_time = (now - start_time).total_seconds()
            
            transcription_data = {
                'filename': Path(audio_path).stem,
                'text': result["text"].strip(),
                'date': now.strftime("%Y-%m-%d %H:%M:%S"),
                'duration': metadata['duration_formatted'],
                'duration_seconds': metadata['duration_seconds'],
                'file_size_mb': metadata['file_size_mb'],
                'model': self.model_size,
                'language': result.get('language', 'unknown'),
                'segments': result.get('segments', []),
                'formatting_style': formatting_style,
                'processing_time_seconds': processing_time,
                'characters_per_second': len(result["text"]) / processing_time if processing_time > 0 else 0
            }
            
            # Create markdown content
            markdown_text = create_markdown(**transcription_data)
            
            # Ensure output directory exists
            TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)
            
            # Save to file with atomic write
            output_path = TRANSCRIPTION_FOLDER / f"{Path(audio_path).stem}.md"
            temp_path = output_path.with_suffix('.tmp')
            
            try:
                # Ensure UTF-8 encoding for all text output
                if ENSURE_UTF8_ENCODING:
                    temp_path.write_text(markdown_text, encoding=OUTPUT_ENCODING)
                    logger.debug(f"File written with {OUTPUT_ENCODING} encoding")
                else:
                    temp_path.write_text(markdown_text, encoding="utf-8")
                temp_path.replace(output_path)  # Atomic move
            except Exception as e:
                if temp_path.exists():
                    temp_path.unlink()  # Clean up temp file
                raise e
            
            if progress_callback:
                progress_callback("Transcription completed!")
            
            logger.info(f"Transcription completed in {processing_time:.1f}s - Saved to: {output_path}")
            return output_path, transcription_data
            
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(f"Error: {str(e)}")
            raise Exception(error_msg)
