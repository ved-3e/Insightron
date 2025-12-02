#!/usr/bin/env python3
"""
Batch Processor for Insightron
Provides optimized batch processing with thread and process pool support.
"""

import sys
import os
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

from transcription.transcribe import AudioTranscriber
from core.config import WHISPER_MODEL, DEFAULT_LANGUAGE, get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_single_file_worker(audio_file: str, model_size: str, language: str, formatting_style: str) -> Dict[str, Any]:
    """
    Top-level worker function for batch processing.
    Must be at module level for multiprocessing pickling.
    """
    try:
        # Create a new transcriber instance for this process
        # ModelManager singleton will handle model loading/sharing within the process
        transcriber = AudioTranscriber(model_size, language)
        
        output_path, transcription_data = transcriber.transcribe_file(
            audio_file,
            formatting_style=formatting_style
        )
        
        return {
            'output_path': str(output_path),
            'duration': transcription_data['duration'],
            'language': transcription_data['language'],
            'processing_time': transcription_data['processing_time_seconds'],
            'status': 'success'
        }
    except Exception as e:
        return {
            'file': audio_file,
            'error': str(e),
            'status': 'failed'
        }

class BatchTranscriber:
    """
    Batch transcription processor with optimized concurrency support.
    """
    
    def __init__(
        self, 
        model_size: str = WHISPER_MODEL,
        language: str = DEFAULT_LANGUAGE,
        max_workers: Optional[int] = None,
        use_multiprocessing: bool = True, # Default to True for better CPU utilization
        transcriber: Optional[AudioTranscriber] = None
    ):
        self.model_size = model_size
        self.language = language
        self.use_multiprocessing = use_multiprocessing
        
        # Determine optimal worker count from config or defaults
        if max_workers is None:
            # Try to get worker_count from config first
            worker_count_config = get_config('runtime.worker_count')
            if worker_count_config is not None:
                self.max_workers = worker_count_config
            else:
                # Auto-detect based on CPU and device
                cpu_count = os.cpu_count() or 1
                import torch
                if torch.cuda.is_available():
                    # Conservative default for GPU: 2 workers or 1/4 of CPUs
                    self.max_workers = max(1, min(2, cpu_count // 4))
                else:
                    # For CPU, use physical cores (often cpu_count / 2 for hyperthreading)
                    self.max_workers = max(1, int(cpu_count * 0.75))
        else:
            self.max_workers = max_workers
            
        # Initialize transcriber ONLY if using threads (shared instance)
        self.transcriber = transcriber
        if not self.use_multiprocessing and self.transcriber is None:
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
        
        logger.info(f"Starting batch transcription of {len(audio_files)} files with {self.max_workers} workers")
        
        ExecutorClass = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            future_to_file = {}
            
            for audio_file in audio_files:
                if self.use_multiprocessing:
                    # Pass simple types for multiprocessing
                    future = executor.submit(
                        transcribe_single_file_worker,
                        audio_file,
                        self.model_size,
                        self.language,
                        formatting_style
                    )
                else:
                    # Use internal method for threading (can share self.transcriber)
                    future = executor.submit(
                        self._transcribe_single_file_threaded,
                        audio_file,
                        formatting_style
                    )
                future_to_file[future] = audio_file
            
            for future in as_completed(future_to_file):
                audio_file = future_to_file[future]
                try:
                    result = future.result()
                    
                    if result.get('status') == 'failed':
                        raise Exception(result.get('error', 'Unknown error'))
                        
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
    
    def _transcribe_single_file_threaded(self, audio_file: str, formatting_style: str) -> Dict[str, Any]:
        """Worker method for ThreadPoolExecutor (can use shared self.transcriber)."""
        # Use shared transcriber if available, otherwise create new
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
            'processing_time': transcription_data['processing_time_seconds'],
            'status': 'success'
        }

def batch_transcribe_files(
    audio_files: List[str],
    model_size: str = WHISPER_MODEL,
    language: str = DEFAULT_LANGUAGE,
    max_workers: Optional[int] = None,
    use_multiprocessing: bool = True,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    transcriber: Optional[AudioTranscriber] = None
) -> Dict[str, Any]:
    """Convenience function for batch transcription."""
    batch_transcriber = BatchTranscriber(
        model_size=model_size,
        language=language,
        max_workers=max_workers,
        use_multiprocessing=use_multiprocessing,
        transcriber=transcriber
    )
    
    return batch_transcriber.transcribe_batch(
        audio_files,
        progress_callback=progress_callback
    )

if __name__ == "__main__":
    # Simple test when running directly
    print("Batch Processor Module")
    # You can add a simple test here if needed
