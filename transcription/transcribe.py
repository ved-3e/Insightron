import os
import logging
import wave
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
import librosa
import soundfile
import numpy as np


from core.utils import create_markdown
from core.config import (
    get_config_manager,
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
        Initialize the transcriber using the ModelManager singleton.
        
        Args:
            model_size: Size of the model (managed by ModelManager, argument kept for compatibility but logged if different)
            language: Default language code
        """
        from core.model_manager import ModelManager
        
        self.model_manager = ModelManager()
        
        # Check if requested model matches loaded model
        if model_size != self.model_manager.model_size:
            logger.warning(f"Requested model '{model_size}' but ModelManager is configured for '{self.model_manager.model_size}'. Using ModelManager's model.")
            
        self.model_size = self.model_manager.model_size
        self.supported_formats = {'.mp3', '.wav', '.m4a', '.flac', '.mp4', '.ogg', '.aac', '.wma'}
        self.supported_languages = SUPPORTED_LANGUAGES
        self.language = language
        
        # Optimization: Set beam size based on model type
        self.beam_size = 1 if "distil" in self.model_size else 5
        
        # Load performance optimization settings from config
        config = get_config_manager()
        self.segment_merge_threshold = config.get('transcription.segment_merge_threshold', -0.5)
        self.min_segment_duration = config.get('transcription.min_segment_duration', 0.1)
        self.progress_update_frequency = config.get('transcription.progress_update_frequency', 5)
        self.enable_segment_filtering = config.get('transcription.enable_segment_filtering', True)
        
        logger.info(f"AudioTranscriber initialized with model: {self.model_size}")
        logger.debug(f"Optimization settings: merge_threshold={self.segment_merge_threshold}, "
                    f"min_duration={self.min_segment_duration}s, progress_freq={self.progress_update_frequency}%")

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

    def _merge_segments_smart(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Intelligently merge segments based on confidence and timing.
        
        Segments are merged if:
        - They are consecutive (no significant gap)
        - Both have reasonable confidence scores
        - The gap between them is small (< 0.5 seconds)
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            List of merged segments
        """
        if not segments or len(segments) <= 1:
            return segments
        
        merged = []
        current = segments[0].copy()
        
        for i in range(1, len(segments)):
            next_seg = segments[i]
            
            # Calculate gap between segments
            gap = next_seg['start'] - current['end']
            
            # Get confidence scores
            current_conf = current.get('confidence', 0)
            next_conf = next_seg.get('confidence', 0)
            
            # Merge conditions: small gap and both have decent confidence
            should_merge = (
                gap < 0.5 and  # Less than 0.5 second gap
                current_conf > self.segment_merge_threshold and
                next_conf > self.segment_merge_threshold
            )
            
            if should_merge:
                # Merge segments
                current['end'] = next_seg['end']
                current['text'] = current['text'] + ' ' + next_seg['text']
                # Average the confidence scores
                if 'confidence' in current and 'confidence' in next_seg:
                    current['confidence'] = (current_conf + next_conf) / 2
            else:
                # Save current and start new segment
                merged.append(current)
                current = next_seg.copy()
        
        # Don't forget the last segment
        merged.append(current)
        
        logger.debug(f"Segment merging: {len(segments)} → {len(merged)} segments")
        return merged

    def _calculate_quality_metrics(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate quality metrics for transcribed segments.
        
        Args:
            segments: List of segment dictionaries with confidence scores
            
        Returns:
            Dictionary with quality metrics
        """
        if not segments:
            return {
                "avg_confidence": 0.0,
                "low_confidence_count": 0,
                "total_segments": 0,
                "min_confidence": 0.0,
                "max_confidence": 0.0
            }
        
        confidences = [seg.get('confidence', 0.0) for seg in segments if 'confidence' in seg]
        
        if not confidences:
            return {
                "avg_confidence": 0.0,
                "low_confidence_count": 0,
                "total_segments": len(segments),
                "min_confidence": 0.0,
                "max_confidence": 0.0
            }
        
        return {
            "avg_confidence": sum(confidences) / len(confidences),
            "low_confidence_count": sum(1 for c in confidences if c < self.segment_merge_threshold),
            "total_segments": len(segments),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences)
        }


    def transcribe_file(self, audio_path: str, progress_callback: Optional[Callable[[str], None]] = None, 
                       formatting_style: str = "auto", language: Optional[str] = None) -> tuple[Path, Dict[str, Any]]:
        """
        Transcribe audio file using the shared ModelManager instance.
        
        Args:
            audio_path: Path to the audio file.
            progress_callback: Optional callback for progress updates.
            formatting_style: Formatting style for the output markdown.
            language: Language code to force transcription in specific language.
            
        Returns:
            Tuple containing the path to the generated markdown file and the transcription data dictionary.
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
            # Transcribe
            # faster-whisper returns a generator
            segments, info = self.model_manager.transcribe(
                str(audio_path),
                beam_size=self.beam_size,
                language=transcription_language,
                task="transcribe"
            )
            
            if progress_callback:
                progress_callback(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            # Process segments with optimizations
            transcribed_segments = []
            text_parts = []  # Memory-efficient list for text assembly
            
            total_duration = info.duration
            last_progress_percent = -1
            
            # Pre-allocate list capacity estimate for better performance
            estimated_segments = int(total_duration / 3) if total_duration > 0 else 100
            transcribed_segments = []
            text_parts = []
            
            for segment in segments:
                # Smart segment filtering: skip very short, low-confidence segments
                segment_duration = segment.end - segment.start
                if self.enable_segment_filtering:
                    if segment_duration < self.min_segment_duration:
                        if hasattr(segment, 'avg_logprob') and segment.avg_logprob < self.segment_merge_threshold:
                            logger.debug(f"Filtered micro-segment: {segment_duration:.2f}s, confidence: {segment.avg_logprob:.2f}")
                            continue
                
                # Store segment data
                segment_data = {
                    "id": segment.id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                }
                
                # Add confidence if available
                if hasattr(segment, 'avg_logprob'):
                    segment_data["confidence"] = segment.avg_logprob
                
                transcribed_segments.append(segment_data)
                text_parts.append(segment.text)
                
                # Optimized progress updates: only update on significant changes
                if progress_callback and total_duration > 0:
                    current_percent = int((segment.end / total_duration) * 100)
                    # Update only if percent changed by at least progress_update_frequency
                    if current_percent - last_progress_percent >= self.progress_update_frequency:
                        progress_callback(f"Transcribing: {current_percent}% ({int(segment.end)}s/{int(total_duration)}s)")
                        last_progress_percent = current_percent
            
            # Efficient text assembly using join (O(n) vs O(n²) concatenation)
            final_text = "".join(text_parts).strip()
            
            # Prepare result data
            now = datetime.now()
            processing_time = (now - start_time).total_seconds()
            
            # Apply smart segment merging for better quality
            transcribed_segments = self._merge_segments_smart(transcribed_segments)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(transcribed_segments)
            
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
                'characters_per_second': len(final_text) / processing_time if processing_time > 0 else 0,
                'quality_metrics': quality_metrics
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
