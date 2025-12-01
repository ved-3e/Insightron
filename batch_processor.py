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

# Force UTF-8 output on Windows
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
    """
    
    def __init__(
        self, 
        model_size: str = WHISPER_MODEL,
        language: str = DEFAULT_LANGUAGE,
        max_workers: Optional[int] = None,
        use_multiprocessing: bool = False
    ):
        self.model_size = model_size
        self.language = language
        self.use_multiprocessing = use_multiprocessing
        
        # Determine optimal worker count
        if max_workers is None:
            cpu_count = multiprocessing.cpu_count()
            self.max_workers = cpu_count if use_multiprocessing else min(cpu_count * 2, 8)
        else:
            self.max_workers = max_workers
            
        # Initialize transcriber ONLY if using threads (shared instance)
        # faster-whisper is thread-safe
        self.transcriber = None
        if not self.use_multiprocessing:
            logger.info("Initializing shared model for thread pool...")
            self.transcriber = AudioTranscriber(model_size, language)
        
        logger.info(f"BatchTranscriber initialized: model={model_size}, workers={self.max_workers}, "
                   f"multiprocessing={use_multiprocessing}")
    
    def transcribe_batch(
        self,
        audio_files: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        formatting_style: str = "auto"
    ) -> Dict[str, Any]:
        """Transcribe multiple audio files in batch."""
        start_time = datetime.now()
        results = {
            'successful': [],
            'failed': [],
            'total_files': len(audio_files),
            'completed': 0,
            'failed_count': 0
        }
        
        logger.info(f"Starting batch transcription of {len(audio_files)} files")
        
        ExecutorClass = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            future_to_file = {}
            
            for audio_file in audio_files:
                future = executor.submit(
                    self._transcribe_single_file,
                    audio_file,
                    formatting_style
                )
                future_to_file[future] = audio_file
            
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
                    results['failed'].append({'file': audio_file, 'error': str(e)})
                    results['failed_count'] += 1
                    logger.error(f"✗ Failed: {Path(audio_file).name} - {e}")
        
        # Statistics
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        results['statistics'] = {
            'total_time_seconds': total_time,
            'throughput': results['completed'] / total_time if total_time > 0 else 0
        }
        
        return results
    
    def _transcribe_single_file(self, audio_file: str, formatting_style: str) -> Dict[str, Any]:
        """Worker function."""
        # Use shared transcriber if available, otherwise create new (for multiprocessing)
        if self.transcriber:
            transcriber = self.transcriber
        else:
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

def batch_transcribe_files(
    audio_files: List[str],
    model_size: str = WHISPER_MODEL,
    language: str = DEFAULT_LANGUAGE,
    max_workers: Optional[int] = None,
    use_multiprocessing: bool = False,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Dict[str, Any]:
    """Convenience function for batch transcription."""
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

if __name__ == "__main__":
    # Test
    print("Batch Processor Test")
