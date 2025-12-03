import logging
from typing import Optional, Dict, Any, Tuple, Iterator
from faster_whisper import WhisperModel
from faster_whisper.transcribe import TranscriptionInfo, Segment
from core.config import get_config_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Quality-optimized Whisper model manager using faster-whisper v1.2.1.
    
    Features:
    - 3-4x faster than transformers backend
    - 50% lower memory usage  
    - Optimized for maximum accuracy and stability
    - Enhanced VAD for cleaner segments
    - Intelligent retry mechanism
    - Confidence tracking for quality assurance
    - Uses importlib.metadata (no pkg_resources warnings)
    
    Quality Optimizations:
    - Optimal beam_size for accuracy vs speed
    - Temperature fallback for difficult audio
    - VAD filtering to remove silence/noise
    - Segment confidence tracking
    - Graceful degradation on errors
    
    Returns API:
        transcribe() returns tuple: (segments_iterator, TranscriptionInfo)
        - segments: Iterator of Segment with .text, .start, .end, .id, .avg_logprob
        - info: TranscriptionInfo with .language, .language_probability, .duration
    """
    _instance = None
    _model = None

    # Quality-optimized default parameters
    DEFAULT_PARAMS = {
        "beam_size": 5,  # Accuracy priority (1=fastest, 5=balanced, 10=best)
        "best_of": 5,  # Number of candidates for beam search
        "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],  # Fallback temperatures
        "condition_on_previous_text": True,  # Use context for better accuracy
        "compression_ratio_threshold": 2.4,  # Detect repetition/failures
        "log_prob_threshold": -1.0,  # Filter low-confidence segments
        "no_speech_threshold": 0.6,  # Detect silence/non-speech
    }
    
    # Enhanced VAD parameters for cleaner segments
    VAD_PARAMS = {
        "threshold": 0.5,  # Speech detection confidence (0.0-1.0)
        "min_speech_duration_ms": 250,  # Ignore very short utterances
        "min_silence_duration_ms": 2000,  # Merge segments with short gaps
        "speech_pad_ms": 400,  # Padding around detected speech
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Get configuration
        config = get_config_manager()
        self.model_size = config.model.name
        self.compute_type = config.model.compute_type
        
        # Device selection
        device_setting = config.model.device
        self.device = "auto" if device_setting == "auto" else device_setting
        
        # Quality mode configuration
        self.quality_mode = config.get('model.quality_mode', 'high')  # high|balanced|fast
        self.enable_vad = config.get('model.enable_vad', True)
        self.enable_retry = config.get('model.enable_retry', True)
        self.max_retries = config.get('model.max_retries', 2)
        
        # Adjust parameters based on quality mode
        self._configure_quality_mode()
        
        logger.info(f"ModelManager initialized: Model={self.model_size}, Device={self.device}, "
                   f"Quality={self.quality_mode}, VAD={self.enable_vad}")

    def _configure_quality_mode(self):
        """Configure parameters based on quality mode."""
        if self.quality_mode == "high":
            # Maximum accuracy - slower but best results
            self.default_beam_size = 5
            self.default_best_of = 5
        elif self.quality_mode == "balanced":
            # Balance speed and accuracy
            self.default_beam_size = 3
            self.default_best_of = 3
        else:  # fast
            # Speed priority - faster but lower accuracy
            self.default_beam_size = 1
            self.default_best_of = 1

    def load_model(self) -> WhisperModel:
        """
        Loads the faster-whisper WhisperModel if not already loaded.
        
        Returns:
            WhisperModel: Loaded model instance
        """
        if self._model is None:
            logger.info(f"Loading faster-whisper v1.2.1: {self.model_size} on {self.device}...")
            try:
                # Map model names for compatibility
                model_name = self.model_size
                
                # Handle transformers-style naming
                if model_name.startswith("openai/whisper-"):
                    model_name = model_name.replace("openai/whisper-", "")
                    logger.info(f"Mapped model name: {self.model_size} -> {model_name}")
                
                self._model = WhisperModel(
                    model_name,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root=None,
                    local_files_only=False
                )
                logger.info(f"✓ Model loaded successfully: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise RuntimeError(f"Could not load model '{self.model_size}': {e}")
        return self._model

    def transcribe(
        self,
        audio,
        language: Optional[str] = None,
        task: str = "transcribe",
        **kwargs
    ) -> Tuple[Iterator[Segment], TranscriptionInfo]:
        """
        High-quality transcription with optimal parameters and retry mechanism.
        
        Args:
            audio: Audio file path (str) or numpy array (float32, 16kHz mono)
            language: Language code ('en', 'es', etc.) or None for auto-detect
            task: 'transcribe' or 'translate'
            **kwargs: Override default parameters
                - beam_size: Beam search width
                - temperature: Sampling temperature(s)
                - vad_filter: Enable VAD
                - condition_on_previous_text: Use context
                
        Returns:
            tuple: (segments_iterator, TranscriptionInfo)
                - segments: Iterator of Segment objects with .text, .start, .end, .avg_logprob
                - info: TranscriptionInfo with .language, .language_probability, .duration
        """
        model = self.load_model()
        
        # Merge default quality parameters with user overrides
        params = self._build_transcription_params(language, task, **kwargs)
        
        # Attempt transcription with retry mechanism
        if self.enable_retry:
            return self._transcribe_with_retry(model, audio, params)
        else:
            return self._transcribe_once(model, audio, params)

    def _build_transcription_params(
        self,
        language: Optional[str],
        task: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Build optimized transcription parameters."""
        params = {
            "language": language,
            "task": task,
            "beam_size": kwargs.pop("beam_size", self.default_beam_size),
            "best_of": kwargs.pop("best_of", self.default_best_of),
            "temperature": kwargs.pop("temperature", self.DEFAULT_PARAMS["temperature"]),
            "condition_on_previous_text": kwargs.pop(
                "condition_on_previous_text",
                self.DEFAULT_PARAMS["condition_on_previous_text"]
            ),
            "compression_ratio_threshold": kwargs.pop(
                "compression_ratio_threshold",
                self.DEFAULT_PARAMS["compression_ratio_threshold"]
            ),
            "log_prob_threshold": kwargs.pop(
                "log_prob_threshold",
                self.DEFAULT_PARAMS["log_prob_threshold"]
            ),
            "no_speech_threshold": kwargs.pop(
                "no_speech_threshold",
                self.DEFAULT_PARAMS["no_speech_threshold"]
            ),
            "vad_filter": kwargs.pop("vad_filter", self.enable_vad),
        }
        
        # Add VAD parameters if enabled
        if params["vad_filter"]:
            params["vad_parameters"] = kwargs.pop("vad_parameters", self.VAD_PARAMS.copy())
        
        # Include any additional kwargs
        params.update(kwargs)
        
        return params

    def _transcribe_once(
        self,
        model: WhisperModel,
        audio,
        params: Dict[str, Any]
    ) -> Tuple[Iterator[Segment], TranscriptionInfo]:
        """Perform single transcription attempt."""
        try:
            segments, info = model.transcribe(audio, **params)
            return segments, info
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def _transcribe_with_retry(
        self,
        model: WhisperModel,
        audio,
        params: Dict[str, Any]
    ) -> Tuple[Iterator[Segment], TranscriptionInfo]:
        """
        Transcribe with intelligent retry and fallback strategies.
        
        Strategy:
        - Attempt 1: Best quality (beam_size from config)
        - Attempt 2: Reduced quality (beam_size=3, simpler temperature)
        - Attempt 3: Minimal quality (beam_size=1, basic temperature)
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Adjust parameters for each retry
                if attempt == 1:
                    # Second attempt: reduce quality slightly
                    params["beam_size"] = 3
                    params["best_of"] = 3
                    params["temperature"] = [0.0, 0.2]
                    logger.warning(f"Retry {attempt}: Using balanced quality parameters")
                elif attempt == 2:
                    # Third attempt: minimum quality for speed
                    params["beam_size"] = 1
                    params["best_of"] = 1
                    params["temperature"] = [0.0]
                    params["vad_filter"] = False  # Disable VAD to be more permissive
                    logger.warning(f"Retry {attempt}: Using fast fallback parameters")
                
                segments, info = model.transcribe(audio, **params)
                
                if attempt > 0:
                    logger.info(f"✓ Transcription successful on retry {attempt}")
                
                return segments, info
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
                    raise RuntimeError(
                        f"Transcription failed after {self.max_retries + 1} attempts: {last_error}"
                    )
        
        # Should never reach here, but for type safety
        raise RuntimeError(f"Unexpected error in retry logic: {last_error}")

    def get_quality_metrics(self, segments: list) -> Dict[str, Any]:
        """
        Calculate quality metrics for transcribed segments.
        
        Args:
            segments: List of Segment objects
            
        Returns:
            Dictionary with quality metrics
        """
        if not segments:
            return {
                "avg_confidence": 0.0,
                "low_confidence_count": 0,
                "total_segments": 0
            }
        
        confidences = [seg.avg_logprob for seg in segments if hasattr(seg, 'avg_logprob')]
        
        return {
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
            "low_confidence_count": sum(1 for c in confidences if c < -0.5),
            "total_segments": len(segments),
            "min_confidence": min(confidences) if confidences else 0.0,
            "max_confidence": max(confidences) if confidences else 0.0
        }
