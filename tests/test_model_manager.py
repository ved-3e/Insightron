import unittest
from unittest.mock import MagicMock, patch
from model_manager import ModelManager

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

    @patch('model_manager.WhisperModel')
    def test_lazy_loading(self, mock_whisper):
        """Test that the model is not loaded on initialization."""
        manager = ModelManager()
        self.assertIsNone(manager._model)
        
        # Accessing load_model should trigger loading
        manager.load_model()
        mock_whisper.assert_called_once()
        self.assertIsNotNone(manager._model)

    @patch('model_manager.WhisperModel')
    def test_transcribe_calls_model_transcribe(self, mock_whisper):
        """Test that transcribe method delegates to the model."""
        mock_model_instance = MagicMock()
        mock_whisper.return_value = mock_model_instance
        
        manager = ModelManager()
        manager.transcribe("dummy_audio.wav", language="en")
        
        mock_model_instance.transcribe.assert_called_once_with("dummy_audio.wav", language="en")

if __name__ == '__main__':
    unittest.main()
