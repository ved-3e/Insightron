import unittest
from unittest.mock import MagicMock, patch
from core.model_manager import ModelManager

class TestModelManager(unittest.TestCase):
    def setUp(self):
        # Reset singleton instance for each test
        ModelManager._instance = None
        ModelManager._model = None

    def test_singleton_behavior(self):
        """Test that multiple instantiations return the same object."""
        manager1 = ModelManager()
        manager2 = ModelManager()
        self.assertIs(manager1, manager2)

    @patch('core.model_manager.WhisperModel')
    def test_lazy_loading(self, mock_whisper):
        """Test that the model is not loaded on initialization."""
        manager = ModelManager()
        self.assertIsNone(manager._model)
        
        # Accessing load_model should trigger loading
        manager.load_model()
        mock_whisper.assert_called_once()
        self.assertIsNotNone(manager._model)

    @patch('core.model_manager.WhisperModel')
    def test_transcribe_returns_tuple(self, mock_whisper):
        """Test that transcribe method returns (segments, info) tuple from faster-whisper."""
        # Create mock segments and info
        mock_segment1 = MagicMock()
        mock_segment1.text = "Hello world"
        mock_segment1.start = 0.0
        mock_segment1.end = 1.5
        mock_segment1.id = 0
        mock_segment1.avg_logprob = -0.3
        
        mock_info = MagicMock()
        mock_info.language = "en"
        mock_info.language_probability = 0.95
        mock_info.duration = 10.0
        
        # Setup mock model to return tuple
        mock_model_instance = MagicMock()
        mock_model_instance.transcribe.return_value = ([mock_segment1], mock_info)
        mock_whisper.return_value = mock_model_instance
        
        manager = ModelManager()
        segments, info = manager.transcribe("dummy_audio.wav", language="en", beam_size=5)
        
        # Verify return type is tuple
        self.assertIsInstance(segments, list)
        self.assertEqual(info.language, "en")
        self.assertEqual(info.language_probability, 0.95)
        
        # Verify model.transcribe was called with quality parameters
        mock_model_instance.transcribe.assert_called_once()

    @patch('core.model_manager.WhisperModel')
    def test_quality_mode_configuration(self, mock_whisper):
        """Test that quality mode affects beam_size configuration."""
        manager = ModelManager()
        
        # High quality mode should set beam_size=5
        if manager.quality_mode == "high":
            self.assertEqual(manager.default_beam_size, 5)
            self.assertEqual(manager.default_best_of, 5)

    @patch('core.model_manager.WhisperModel')
    def test_vad_parameters_included(self, mock_whisper):
        """Test that VAD parameters are properly configured."""
        mock_model_instance = MagicMock()
        mock_model_instance.transcribe.return_value = ([], MagicMock())
        mock_whisper.return_value = mock_model_instance
        
        manager = ModelManager()
        manager.transcribe("test.wav", vad_filter=True)
        
        # Check that transcribe was called with VAD parameters
        call_kwargs = mock_model_instance.transcribe.call_args[1]
        if call_kwargs.get("vad_filter"):
            self.assertIn("vad_parameters", call_kwargs)

    def test_get_quality_metrics(self):
        """Test quality metrics calculation."""
        manager = ModelManager()
        
        # Create mock segments
        mock_segments = [
            MagicMock(avg_logprob=-0.2),
            MagicMock(avg_logprob=-0.4),
            MagicMock(avg_logprob=-0.6),  # Low confidence
        ]
        
        metrics = manager.get_quality_metrics(mock_segments)
        
        self.assertEqual(metrics["total_segments"], 3)
        self.assertEqual(metrics["low_confidence_count"], 1)  # One segment < -0.5
        self.assertAlmostEqual(metrics["avg_confidence"], -0.4, places=1)

if __name__ == '__main__':
    unittest.main()

