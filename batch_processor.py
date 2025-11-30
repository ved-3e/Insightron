#!/usr/bin/env python3
"""
Batch Processor for Insightron
Provides optimized batch processing with thread and process pool support.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import logging
from datetime import datetime
import multiprocessing

# Force UTF-8 output on Windows (use reconfigure to avoid closing stdout)
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from transcribe import AudioTranscriber
from config import WHISPER_MODEL, DEFAULT_LANGUAGE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchTranscriber:
    """
    Batch transcription processor with optimized concurrency support.
    Uses thread pools for I/O operations and process pools for CPU-bound tasks.
    """
    
    def __init__(
        self, 
        model_size: str = WHISPER_MODEL,
        language: str = DEFAULT_LANGUAGE,
        max_workers: Optional[int] = None,
        use_multiprocessing: bool = False
    ):
        """
        Initialize batch transcriber.
        
        Args:
            model_size: Whisper model size to use
            language: Default language for transcription
            max_workers: Maximum number of workers (defaults to CPU count)
            use_multiprocessing: Use process pool instead of thread pool
        """
        self.model_size = model_size
        self.language = language
        self.use_multiprocessing = use_multiprocessing
        
        # Determine optimal worker count
        if max_workers is None:
            cpu_count = multiprocessing.cpu_count()
            # For I/O-bound tasks (threading), use more workers
            # For CPU-bound tasks (multiprocessing), use CPU count
            self.max_workers = cpu_count if use_multiprocessing else min(cpu_count * 2, 8)
        else:
            self.max_workers = max_workers
        
        logger.info(f"BatchTranscriber initialized: model={model_size}, workers={self.max_workers}, "
                   f"multiprocessing={use_multiprocessing}")
    
    def transcribe_batch(
        self,
        audio_files: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        formatting_style: str = "auto"
    ) -> Dict[str, Any]:
        """
        Transcribe multiple audio files in batch with optimized concurrency.
        
        Args:
            audio_files: List of audio file paths
            progress_callback: Callback function(completed, total, filename)
            formatting_style: Text formatting style
            
        Returns:
            Dictionary with results and statistics
        """
        start_time = datetime.now()
        results = {
            'successful': [],
            'failed': [],
            'total_files': len(audio_files),
            'completed': 0,
            'failed_count': 0
        }
        
        logger.info(f"Starting batch transcription of {len(audio_files)} files")
        
        # Choose executor based on configuration
        ExecutorClass = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {}
            
            for audio_file in audio_files:
                future = executor.submit(
                    self._transcribe_single_file,
                    audio_file,
                    formatting_style
                )
                future_to_file[future] = audio_file
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                audio_file = future_to_file[future]
                
                try:
                    result = future.result()
                    results['successful'].append({
                        'file': audio_file,
                        'output': result['output_path'],
                        'duration': result['duration'],
                        'language': result['language']
                    })
                    results['completed'] += 1
                    
                    if progress_callback:
                        progress_callback(
                            results['completed'],
                            results['total_files'],
                            Path(audio_file).name
                        )
                    
                    logger.info(f"✓ Completed: {Path(audio_file).name}")
                    
                except Exception as e:
                    results['failed'].append({
                        'file': audio_file,
                        'error': str(e)
                    })
                    results['failed_count'] += 1
                    logger.error(f"✗ Failed: {Path(audio_file).name} - {e}")
        
        # Calculate statistics
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        results['statistics'] = {
            'total_time_seconds': total_time,
            'average_time_per_file': total_time / len(audio_files) if audio_files else 0,
            'success_rate': (results['completed'] / results['total_files'] * 100) if results['total_files'] > 0 else 0,
            'throughput': results['completed'] / total_time if total_time > 0 else 0
        }
        
        logger.info(f"Batch transcription completed: {results['completed']}/{results['total_files']} successful "
                   f"in {total_time:.1f}s ({results['statistics']['throughput']:.2f} files/sec)")
        
        return results
    
    def _transcribe_single_file(self, audio_file: str, formatting_style: str) -> Dict[str, Any]:
        """
        Transcribe a single file (worker function).
        
        Args:
            audio_file: Path to audio file
            formatting_style: Text formatting style
            
        Returns:
            Transcription result dictionary
        """
        # Create a new transcriber instance for this worker
        # This is important for multiprocessing to avoid sharing model state
        transcriber = AudioTranscriber(self.model_size, self.language)
        
        output_path, transcription_data = transcriber.transcribe_file(
            audio_file,
            formatting_style=formatting_style
        )
        
        return {
            'output_path': str(output_path),
            'duration': transcription_data['duration'],
            'language': transcription_data['language'],
            'processing_time': transcription_data['processing_time_seconds']
        }


class OptimizedTextProcessor:
    """
    Optimized text processor using process pools for CPU-bound operations.
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        """
        Initialize optimized text processor.
        
        Args:
            max_workers: Maximum number of worker processes
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        logger.info(f"OptimizedTextProcessor initialized with {self.max_workers} workers")
    
    def process_large_text_parallel(
        self,
        text: str,
        chunk_size: int = 10000,
        formatting_style: str = "auto"
    ) -> str:
        """
        Process very large text in parallel chunks.
        
        Args:
            text: Text to process
            chunk_size: Size of each chunk in characters
            formatting_style: Formatting style to apply
            
        Returns:
            Processed text
        """
        from text_formatter import format_transcript
        
        # If text is small, process directly
        if len(text) < chunk_size * 2:
            return format_transcript(text, formatting_style)
        
        # Split text into chunks
        chunks = self._split_text_into_chunks(text, chunk_size)
        
        # Process chunks in parallel
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(format_transcript, chunk, formatting_style)
                for chunk in chunks
            ]
            
            processed_chunks = [future.result() for future in as_completed(futures)]
        
        # Combine results
        return '\n\n'.join(processed_chunks)
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks at sentence boundaries.
        
        Args:
            text: Text to split
            chunk_size: Approximate size of each chunk
            
        Returns:
            List of text chunks
        """
        import re
        
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks


def batch_transcribe_files(
    audio_files: List[str],
    model_size: str = WHISPER_MODEL,
    language: str = DEFAULT_LANGUAGE,
    max_workers: Optional[int] = None,
    use_multiprocessing: bool = False,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """
    Convenience function for batch transcription.
    
    Args:
        audio_files: List of audio file paths
        model_size: Whisper model size
        language: Language for transcription
        max_workers: Maximum number of workers
        use_multiprocessing: Use process pool instead of thread pool
        progress_callback: Progress callback function
        
    Returns:
        Batch transcription results
    """
    batch_transcriber = BatchTranscriber(
        model_size=model_size,
        language=language,
        max_workers=max_workers,
        use_multiprocessing=use_multiprocessing
    )
    
    return batch_transcriber.transcribe_batch(
        audio_files,
        progress_callback=progress_callback
    )


# Example usage
if __name__ == "__main__":
    # Example: Batch transcribe multiple files
    sample_files = [
        "audio1.mp3",
        "audio2.mp3",
        "audio3.mp3"
    ]
    
    def progress_callback(completed, total, filename):
        print(f"Progress: {completed}/{total} - Processing: {filename}")
    
    # Using thread pool (better for I/O-bound Whisper transcription)
    results = batch_transcribe_files(
        sample_files,
        model_size="tiny",
        max_workers=4,
        use_multiprocessing=False,
        progress_callback=progress_callback
    )
    
    print(f"\nResults: {results['completed']} successful, {results['failed_count']} failed")
    print(f"Throughput: {results['statistics']['throughput']:.2f} files/sec")
