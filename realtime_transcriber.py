import sounddevice as sd
import numpy as np
import threading
import queue
import logging
import time
from typing import Optional, Callable, List, Dict, Any
from faster_whisper import WhisperModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeTranscriber:
    """
    Realtime Audio Transcriber using sounddevice and faster-whisper.
    Uses silence detection to chunk audio for smooth transcription.
    """
    
    def __init__(self, model_size: str = "base", language: str = "en"):
        self.model_size = model_size
        self.language = language
        self.model = None
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.result_callback = None
        self.audio_level_callback = None
        self.stream = None
        self.thread = None
        
        # Audio parameters
        self.sample_rate = 16000
        self.channels = 1
        self.dtype = 'float32'
        self.block_size = 4096  # Audio block size
        
        # Silence detection parameters
        self.silence_threshold = 0.01  # Amplitude threshold
        self.silence_duration = 0.8    # Seconds of silence to trigger transcription
        self.min_chunk_duration = 1.0  # Minimum audio duration to transcribe
        
        # State
        self.audio_buffer = np.array([], dtype=self.dtype)
        self.full_audio_buffer = np.array([], dtype=self.dtype)  # Store complete recording
        self.last_speech_time = time.time()
        self.transcribed_segments = []
        self.time_offset = 0.0
        
    def initialize_model(self):
        """Initialize the Whisper model if not already loaded."""
        if self.model is None:
            logger.info(f"Loading realtime model: {self.model_size}...")
            # Use int8 for speed
            self.model = WhisperModel(self.model_size, device="auto", compute_type="int8")
            logger.info("Realtime model loaded.")

    def get_microphones(self) -> List[Dict[str, any]]:
        """Get list of available microphones."""
        devices = []
        try:
            host_api_info = sd.query_host_apis()
            # Prefer MME on Windows or Core Audio on macOS if needed, but default is usually fine.
            # We'll just list all input devices.
            
            all_devices = sd.query_devices()
            for i, dev in enumerate(all_devices):
                if dev['max_input_channels'] > 0:
                    # Filter out some virtual devices if needed, but for now list all
                    devices.append({
                        'index': i,
                        'name': dev['name'],
                        'host_api': dev['hostapi'],
                        'samplerate': dev['default_samplerate']
                    })
        except Exception as e:
            logger.error(f"Error listing microphones: {e}")
            # Fallback
            devices.append({'index': -1, 'name': 'Default Microphone'})
            
        return devices

    def start_transcription(self, device_index: int, callback: Callable[[str], None], 
                           audio_level_callback: Optional[Callable[[float], None]] = None):
        """
        Start realtime transcription.
        
        Args:
            device_index: Index of the microphone device
            callback: Function to call with transcribed text
            audio_level_callback: Optional callback for audio level updates (0.0-1.0)
        """
        if self.is_running:
            return

        self.initialize_model()
        self.result_callback = callback
        self.audio_level_callback = audio_level_callback
        self.is_running = True
        self.audio_buffer = np.array([], dtype=self.dtype)
        self.full_audio_buffer = np.array([], dtype=self.dtype)  # Reset full buffer
        self.transcribed_segments = []
        self.time_offset = 0.0
        self.last_speech_time = time.time()
        
        # Clear queue
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()
            
        # Start processing thread
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        
        # Start audio stream
        try:
            self.stream = sd.InputStream(
                device=device_index if device_index >= 0 else None,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=self.dtype,
                blocksize=self.block_size,
                callback=self._audio_callback
            )
            self.stream.start()
            logger.info(f"Started recording on device {device_index}")
        except Exception as e:
            self.is_running = False
            logger.error(f"Failed to start stream: {e}")
            raise e

    def stop_transcription(self):
        """Stop realtime transcription."""
        self.is_running = False
        
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.error(f"Error closing stream: {e}")
            self.stream = None
            
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
            
        logger.info("Stopped transcription")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for sounddevice."""
        if status:
            logger.warning(f"Audio status: {status}")
        if self.is_running:
            # Calculate RMS audio level for visualization
            rms = np.sqrt(np.mean(indata**2))
            # Normalize to 0-1 range - reduced from 0.5 to 0.15 for more sensitivity
            level = min(rms / 0.15, 1.0)
            
            if self.audio_level_callback:
                try:
                    self.audio_level_callback(level)
                except Exception as e:
                    logger.error(f"Error in audio level callback: {e}")
            
            self.audio_queue.put(indata.copy())

    def _process_loop(self):
        """Main processing loop."""
        while self.is_running:
            try:
                # Get audio from queue
                try:
                    # Non-blocking get with timeout to check is_running
                    data = self.audio_queue.get(timeout=0.1)
                    self.audio_buffer = np.concatenate((self.audio_buffer, data.flatten()))
                    # Also store in full buffer for saving
                    self.full_audio_buffer = np.concatenate((self.full_audio_buffer, data.flatten()))
                except queue.Empty:
                    continue
                
                # Analyze audio for silence
                # Simple RMS amplitude
                rms = np.sqrt(np.mean(data**2))
                current_time = time.time()
                
                if rms > self.silence_threshold:
                    self.last_speech_time = current_time
                
                # Check if we should transcribe
                # 1. Silence duration exceeded AND
                # 2. Minimum chunk duration met
                silence_duration = current_time - self.last_speech_time
                buffer_duration = len(self.audio_buffer) / self.sample_rate
                
                if (silence_duration > self.silence_duration and buffer_duration > self.min_chunk_duration) or \
                   (buffer_duration > 10.0): # Force transcribe if buffer gets too long (10s)
                    
                    self._transcribe_buffer()
                    
            except Exception as e:
                logger.error(f"Error in process loop: {e}")
                time.sleep(0.1)

    def _transcribe_buffer(self):
        """Transcribe the current audio buffer."""
        if len(self.audio_buffer) == 0:
            return
            
        # Transcribe
        try:
            # faster-whisper accepts np.ndarray
            segments, info = self.model.transcribe(
                self.audio_buffer,
                language=self.language if self.language != 'auto' else None,
                beam_size=5,
                vad_filter=True  # Use VAD to filter out silence/noise
            )
            
            # Process segments and update offsets
            buffer_text = []
            for segment in segments:
                # Adjust timestamps with current offset
                adjusted_segment = {
                    'start': segment.start + self.time_offset,
                    'end': segment.end + self.time_offset,
                    'text': segment.text
                }
                self.transcribed_segments.append(adjusted_segment)
                buffer_text.append(segment.text)
            
            text = " ".join(buffer_text).strip()
            
            if text:
                logger.info(f"Realtime transcribed: {text}")
                if self.result_callback:
                    self.result_callback(text)
            
            # Update time offset before clearing buffer
            buffer_duration = len(self.audio_buffer) / self.sample_rate
            self.time_offset += buffer_duration
            
            # Reset buffer
            self.audio_buffer = np.array([], dtype=self.dtype)
            
        except Exception as e:
            logger.error(f"Realtime transcription error: {e}")

    def get_transcription_data(self) -> Dict[str, Any]:
        """Get the full transcription data including segments."""
        full_text = " ".join([s['text'] for s in self.transcribed_segments])
        return {
            'text': full_text,
            'segments': self.transcribed_segments,
            'language': self.language
        }

    def save_recording(self, output_path: str):
        """Save the recorded audio to WAV file"""
        import wave
        
        if len(self.full_audio_buffer) == 0:
            logger.warning("No audio to save")
            return None
        
        try:
            # Convert float32 to 16-bit PCM
            audio_int16 = np.int16(self.full_audio_buffer * 32767)
            
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            logger.info(f"Audio saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return None
