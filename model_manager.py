import logging
import torch
from faster_whisper import WhisperModel
from config import get_config_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Singleton class to manage the Whisper model.
    Ensures the model is loaded only once and lazy-loaded when needed.
    """
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # Get configuration from ConfigManager
        config = get_config_manager()
        self.model_size = config.model.name
        self.compute_type = config.model.compute_type
        
        # Device selection: respect config, but validate against hardware
        device_setting = config.model.device
        if device_setting == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        elif device_setting == "cuda":
            if torch.cuda.is_available():
                self.device = "cuda"
            else:
                logger.warning("CUDA requested but not available. Falling back to CPU.")
                self.device = "cpu"
        else:
            self.device = device_setting
        
        logger.info(f"ModelManager initialized. Device: {self.device}, Compute Type: {self.compute_type}")

    def load_model(self):
        """
        Loads the Whisper model if it hasn't been loaded yet.
        """
        if self._model is None:
            logger.info(f"Loading faster-whisper model: {self.model_size} on {self.device}...")
            try:
                self._model = WhisperModel(
                    self.model_size, 
                    device=self.device, 
                    compute_type=self.compute_type
                )
                logger.info(f"Successfully loaded {self.model_size} model.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise RuntimeError(f"Could not load model '{self.model_size}': {e}")
        return self._model

    def transcribe(self, audio, **kwargs):
        """
        Transcribes the given audio using the loaded model.
        """
        model = self.load_model()
        return model.transcribe(audio, **kwargs)
