#!/usr/bin/env python3
"""
Comprehensive Test Suite for Insightron
Tests all modules for functionality, performance, and reliability.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules to test
from transcribe import AudioTranscriber
from text_formatter import TextFormatter, format_transcript
from utils import create_markdown, format_timestamp
from config import WHISPER_MODEL, TRANSCRIPTION_FOLDER

# Configure test logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests

class TestTextFormatter(unittest.TestCase):
    """Test the TextFormatter class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = TextFormatter()
        self.sample_text = "um hello there what happens is that i think this is a test and so basically what i mean is that this should work"
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        result = self.formatter.clean_text(self.sample_text)
        self.assertIsInstance(result, str)
        self.assertNotIn("um", result.lower())
        self.assertIn("hello", result)
    
    def test_fix_common_errors(self):
        """Test common error fixing."""
        test_text = "molar-type chakra and 3d consciousness"
        result = self.formatter._fix_common_errors(test_text)
        self.assertIn("Mooladhara", result)
        self.assertIn("3D", result)
    
    def test_add_punctuation(self):
        """Test punctuation addition."""
        text = "hello world"
        result = self.formatter.add_punctuation(text)
        self.assertTrue(result.endswith('.'))
    
    def test_format_text_auto(self):
        """Test auto formatting."""
        result = self.formatter.format_text(self.sample_text)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_format_with_custom_structure(self):
        """Test custom structure formatting."""
        result = self.formatter.format_with_custom_structure(self.sample_text, 2)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_empty_text_handling(self):
        """Test handling of empty text."""
        result = self.formatter.clean_text("")
        self.assertEqual(result, "")
        
        result = self.formatter.clean_text(None)
        self.assertEqual(result, "")

class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_format_timestamp(self):
        """Test timestamp formatting function."""
        self.assertEqual(format_timestamp(0), "00:00")
        self.assertEqual(format_timestamp(60), "01:00")
        self.assertEqual(format_timestamp(125), "02:05")
        self.assertEqual(format_timestamp(3661), "01:01:01")
    
    def test_create_markdown(self):
        """Test markdown creation."""
        result = create_markdown(
            filename="test",
            text="Hello world",
            date="2024-01-01 12:00:00",
            duration="1:23",
            model="medium",
            duration_seconds=83.0,
            file_size_mb=1.5,
            language="en"
        )
        
        self.assertIn("test", result)
        self.assertIn("Hello world", result)
        self.assertIn("medium", result)
        self.assertIn("1.5 MB", result)
        self.assertIn("1:23", result)

class TestAudioTranscriber(unittest.TestCase):
    """Test AudioTranscriber class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the whisper model to avoid downloading during tests
        with patch('transcribe.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.name = 'test-model'
            mock_load.return_value = mock_model
            self.transcriber = AudioTranscriber("tiny")
    
    def test_initialization(self):
        """Test transcriber initialization."""
        self.assertEqual(self.transcriber.model_size, "tiny")
        self.assertIsInstance(self.transcriber.supported_formats, set)
        self.assertIn('.mp3', self.transcriber.supported_formats)
    
    def test_validate_audio_file_missing(self):
        """Test validation of missing file."""
        with self.assertRaises(FileNotFoundError):
            self.transcriber.validate_audio_file("nonexistent.mp3")
    
    def test_validate_audio_file_unsupported_format(self):
        """Test validation of unsupported format."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"test")
            tmp_path = tmp.name
        
        try:
            with self.assertRaises(ValueError):
                self.transcriber.validate_audio_file(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_validate_audio_file_too_large(self):
        """Test validation of oversized file."""
        # Create a temporary file larger than 25MB
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            # Write 26MB of data
            tmp.write(b"0" * (26 * 1024 * 1024))
            tmp_path = tmp.name
        
        try:
            with self.assertRaises(ValueError):
                self.transcriber.validate_audio_file(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_get_audio_metadata(self):
        """Test metadata extraction."""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name
        
        try:
            metadata = self.transcriber.get_audio_metadata(tmp_path)
            self.assertIn('filename', metadata)
            self.assertIn('file_size_mb', metadata)
            self.assertIn('duration_seconds', metadata)
            self.assertIn('file_extension', metadata)
        finally:
            os.unlink(tmp_path)
    
    @patch('transcribe.soundfile.info')
    @patch('transcribe.librosa.get_duration')
    def test_get_audio_metadata_fallback(self, mock_librosa, mock_soundfile):
        """Test metadata extraction with fallback methods."""
        mock_librosa.side_effect = Exception("Librosa failed")
        mock_info = Mock()
        mock_info.duration = 120.5
        mock_soundfile.return_value = mock_info
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b"fake audio data")
            tmp_path = tmp.name
        
        try:
            metadata = self.transcriber.get_audio_metadata(tmp_path)
            self.assertIn('duration_seconds', metadata)
            self.assertEqual(metadata['duration_seconds'], 120.5)
        finally:
            os.unlink(tmp_path)

class TestFormatTranscript(unittest.TestCase):
    """Test the format_transcript convenience function."""
    
    def test_format_transcript_auto(self):
        """Test auto formatting."""
        text = "hello world this is a test"
        result = format_transcript(text, "auto")
        self.assertIsInstance(result, str)
        self.assertIn("hello", result.lower())
    
    def test_format_transcript_paragraphs(self):
        """Test paragraph formatting."""
        text = "hello world this is a test"
        result = format_transcript(text, "paragraphs")
        self.assertIsInstance(result, str)
    
    def test_format_transcript_minimal(self):
        """Test minimal formatting."""
        text = "hello world this is a test"
        result = format_transcript(text, "minimal")
        self.assertIsInstance(result, str)
    
    def test_format_transcript_invalid_style(self):
        """Test invalid formatting style fallback."""
        text = "hello world this is a test"
        result = format_transcript(text, "invalid")
        self.assertIsInstance(result, str)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_transcription_folder = TRANSCRIPTION_FOLDER
        
        # Temporarily change transcription folder for testing
        import config
        config.TRANSCRIPTION_FOLDER = Path(self.temp_dir) / "test_transcriptions"
        config.TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        import config
        config.TRANSCRIPTION_FOLDER = self.original_transcription_folder
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('transcribe.whisper.load_model')
    def test_full_transcription_workflow(self, mock_load_model):
        """Test the complete transcription workflow."""
        # Mock the whisper model and its transcribe method
        mock_model = Mock()
        mock_model.name = 'test-model'
        mock_model.transcribe.return_value = {
            'text': 'Hello world, this is a test transcription.',
            'language': 'en',
            'segments': [
                {'start': 0.0, 'end': 2.0, 'text': 'Hello world, this is a test transcription.'}
            ]
        }
        mock_load_model.return_value = mock_model
        
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b"fake audio data")
            audio_path = tmp.name
        
        try:
            # Initialize transcriber
            transcriber = AudioTranscriber("tiny")
            
            # Mock the metadata extraction to avoid librosa/whisper audio processing
            transcriber.get_audio_metadata = Mock(return_value={
                'filename': 'test.mp3',
                'file_size_mb': 1.0,
                'duration_seconds': 2.0,
                'duration_formatted': '0:02',
                'file_extension': '.mp3'
            })
            
            # Perform transcription
            output_path, transcription_data = transcriber.transcribe_file(
                audio_path,
                formatting_style="auto"
            )
            
            # Verify results
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.stem, Path(audio_path).stem)
            self.assertIn('text', transcription_data)
            self.assertIn('Hello world', transcription_data['text'])
            self.assertEqual(transcription_data['model'], 'tiny')
            self.assertEqual(transcription_data['language'], 'en')
            
            # Verify markdown content
            markdown_content = output_path.read_text(encoding='utf-8')
            self.assertIn('Hello world', markdown_content)
            self.assertIn('tiny', markdown_content)
            self.assertIn('transcription', markdown_content.lower())
            
        finally:
            os.unlink(audio_path)

class TestPerformance(unittest.TestCase):
    """Performance tests for critical functions."""
    
    def test_text_formatter_performance(self):
        """Test text formatter performance with large text."""
        formatter = TextFormatter()
        large_text = "hello world " * 1000  # 12,000 characters
        
        import time
        start_time = time.time()
        result = formatter.format_text(large_text)
        end_time = time.time()
        
        self.assertIsInstance(result, str)
        self.assertLess(end_time - start_time, 5.0)  # Should complete in under 5 seconds
    
    def test_markdown_creation_performance(self):
        """Test markdown creation performance."""
        large_text = "This is a test sentence. " * 1000  # Large text
        
        import time
        start_time = time.time()
        result = create_markdown(
            filename="performance_test",
            text=large_text,
            date="2024-01-01 12:00:00",
            duration="10:00",
            model="medium",
            duration_seconds=600.0,
            file_size_mb=5.0,
            language="en"
        )
        end_time = time.time()
        
        self.assertIsInstance(result, str)
        self.assertLess(end_time - start_time, 2.0)  # Should complete in under 2 seconds

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_text_formatter_edge_cases(self):
        """Test text formatter with edge cases."""
        formatter = TextFormatter()
        
        # Test with None input
        result = formatter.clean_text(None)
        self.assertEqual(result, "")
        
        # Test with only whitespace
        result = formatter.clean_text("   \n\t   ")
        self.assertEqual(result, "")
        
        # Test with special characters
        result = formatter.clean_text("Hello @#$%^&*() world!")
        self.assertIn("Hello", result)
        self.assertIn("world", result)
    
    def test_format_timestamp_edge_cases(self):
        """Test format_timestamp with edge cases."""
        self.assertEqual(format_timestamp(0), "00:00")
        self.assertEqual(format_timestamp(0.5), "00:00")
        self.assertEqual(format_timestamp(59.9), "00:59")
        self.assertEqual(format_timestamp(3600), "01:00:00")

def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTextFormatter,
        TestUtils,
        TestAudioTranscriber,
        TestFormatTranscript,
        TestIntegration,
        TestPerformance,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
