# Insightron v2.2.0+ Implementation Roadmap

**Status**: Future Planning  
**Last Updated**: December 4, 2025  
**Target Release**: Q1 2026

---

## 📋 Executive Summary

This document outlines the strategic improvements to transform Insightron from a **solid, production-ready application (7.5/10)** into an **enterprise-grade system (9+/10)**. The plan focuses on:

1. **Algorithmic Sophistication** - Adaptive heuristics replacing static thresholds
2. **Reliability & Recovery** - Graceful failure handling with resume capabilities
3. **Performance Profiling** - Memory tracking and resource optimization
4. **User Experience** - Event-driven progress feedback and detailed analytics
5. **Code Quality** - Reduced duplication and improved testability

---

## 🎯 Phase 1: Core Algorithm Improvements (Weeks 1-4)

### Phase 1.1: Adaptive Segment Merging Algorithm

**Current Problem**: Static 0.5s gap threshold doesn't account for speaker cadence or natural pauses.

**Goal**: Implement machine-learned gap thresholds based on audio characteristics.

#### Implementation Steps:

##### Step 1.1.1: Create Segment Analysis Module
**File**: `transcription/segment_analyzer.py` (NEW)

```python
"""
Segment Analysis Module
Provides advanced metrics and pattern detection for transcription segments
"""

from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
import statistics
import logging

logger = logging.getLogger(__name__)

@dataclass
class SegmentMetrics:
    """Metrics for a single segment"""
    duration: float
    gap_after: float
    confidence: float
    word_count: int
    
    @property
    def words_per_second(self) -> float:
        return self.word_count / self.duration if self.duration > 0 else 0

class SegmentAnalyzer:
    """
    Analyzes segment patterns to determine optimal merging thresholds.
    Uses statistical methods to adapt to different speaker cadences.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.segment_cache: Dict[str, List[SegmentMetrics]] = {}
    
    def analyze_segments(
        self, 
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze segment collection for patterns and statistics.
        
        Args:
            segments: List of segment dictionaries from transcription
            
        Returns:
            Dictionary with:
            - avg_gap: Average gap between segments (seconds)
            - avg_duration: Average segment duration (seconds)
            - speech_rate: Average words per second
            - gap_std_dev: Standard deviation of gaps (identifies pauses)
            - adaptive_threshold: Recommended merge threshold
            - confidence_stats: Confidence distribution metrics
        """
        if not segments or len(segments) < 2:
            return self._default_metrics()
        
        # Extract metrics from segments
        metrics = []
        for i, seg in enumerate(segments[:-1]):  # Exclude last segment
            next_seg = segments[i + 1]
            gap = next_seg['start'] - seg['end']
            
            text = seg.get('text', '')
            word_count = len(text.split()) if text else 0
            duration = seg['end'] - seg['start']
            
            metric = SegmentMetrics(
                duration=max(duration, 0.001),  # Avoid division by zero
                gap_after=gap,
                confidence=seg.get('confidence', -1.0),
                word_count=word_count
            )
            metrics.append(metric)
        
        # Calculate statistics
        gaps = [m.gap_after for m in metrics]
        durations = [m.duration for m in metrics]
        speech_rates = [m.words_per_second for m in metrics]
        confidences = [m.confidence for m in metrics if m.confidence >= -1.0]
        
        avg_gap = statistics.mean(gaps)
        std_dev_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
        avg_duration = statistics.mean(durations)
        avg_speech_rate = statistics.mean(speech_rates)
        
        # Adaptive threshold algorithm:
        # If speech rate is fast (>2 wps), allow larger gaps (natural pauses)
        # If speech rate is slow (<1 wps), use tighter thresholds (hesitations)
        if avg_speech_rate > 2.0:
            # Fast speaker: gaps < 0.7s are likely hesitations
            adaptive_threshold = 0.7
        elif avg_speech_rate < 1.0:
            # Slow speaker: gaps < 0.3s are likely breathing
            adaptive_threshold = 0.3
        else:
            # Normal speaker: gaps < 0.5s are likely hesitations
            adaptive_threshold = 0.5
        
        # Adjust for variability: high std dev = irregular pacing
        if std_dev_gap > 0.2:
            adaptive_threshold *= (1 + std_dev_gap / avg_gap)
        
        return {
            'avg_gap': avg_gap,
            'std_dev_gap': std_dev_gap,
            'avg_duration': avg_duration,
            'speech_rate': avg_speech_rate,
            'adaptive_threshold': adaptive_threshold,
            'confidence_mean': statistics.mean(confidences) if confidences else 0.0,
            'confidence_std': statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
            'total_segments': len(segments),
            'analysis_quality': 'high' if len(metrics) > 20 else 'medium' if len(metrics) > 10 else 'low'
        }
    
    def should_merge_segments(
        self,
        current: Dict[str, Any],
        next_seg: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Determine if two segments should be merged based on analysis.
        
        Args:
            current: Current segment
            next_seg: Next segment
            analysis: Segment analysis results
            
        Returns:
            Tuple of (should_merge: bool, reason: str)
        """
        gap = next_seg['start'] - current['end']
        current_conf = current.get('confidence', -1.0)
        next_conf = next_seg.get('confidence', -1.0)
        
        # Check 1: Gap too large
        adaptive_threshold = analysis.get('adaptive_threshold', 0.5)
        if gap > adaptive_threshold:
            return False, f"gap_too_large: {gap:.3f}s > {adaptive_threshold:.3f}s"
        
        # Check 2: Confidence too low (unless both are low)
        if current_conf > -1.0 and next_conf > -1.0:
            avg_conf = (current_conf + next_conf) / 2
            if avg_conf < -1.5:
                return False, f"confidence_too_low: {avg_conf:.2f}"
        
        # Check 3: Gap is negative (overlapping) - always merge
        if gap < 0:
            return True, f"overlapping_segments: gap={gap:.3f}s"
        
        # Check 4: Very small gap - likely breathing room
        if gap < 0.1:
            return True, f"micro_gap: {gap:.3f}s < 0.1s"
        
        # Default: merge if gap is within adaptive threshold
        return True, f"gap_acceptable: {gap:.3f}s <= {adaptive_threshold:.3f}s"
    
    def _default_metrics(self) -> Dict[str, Any]:
        """Return default metrics when analysis impossible"""
        return {
            'avg_gap': 0.3,
            'std_dev_gap': 0.15,
            'avg_duration': 3.0,
            'speech_rate': 1.5,
            'adaptive_threshold': 0.5,
            'confidence_mean': 0.0,
            'confidence_std': 0.0,
            'total_segments': 0,
            'analysis_quality': 'unavailable'
        }
```

##### Step 1.1.2: Integrate into AudioTranscriber
**File**: `transcription/transcribe.py`

**Modifications**:

```python
# Add import at top
from transcription.segment_analyzer import SegmentAnalyzer

class AudioTranscriber:
    def __init__(self, model_size: str = WHISPER_MODEL, language: str = DEFAULT_LANGUAGE):
        # ... existing code ...
        
        # Add segment analyzer
        self.segment_analyzer = SegmentAnalyzer()
        
        logger.info(f"AudioTranscriber initialized with adaptive segment merging")
    
    def transcribe_file(self, audio_path: str, ...):
        # ... existing code ...
        
        # REPLACE this block:
        # OLD: transcribed_segments = self._merge_segments_smart(transcribed_segments)
        
        # NEW: Use adaptive merging
        analysis = self.segment_analyzer.analyze_segments(transcribed_segments)
        logger.info(f"Segment analysis: {analysis['analysis_quality']} quality, "
                   f"adaptive_threshold={analysis['adaptive_threshold']:.3f}s, "
                   f"speech_rate={analysis['speech_rate']:.2f} wps")
        
        transcribed_segments = self._merge_segments_adaptive(
            transcribed_segments, 
            analysis
        )
```

**New Method**:

```python
def _merge_segments_adaptive(
    self, 
    segments: List[Dict[str, Any]], 
    analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Intelligently merge segments using adaptive thresholds.
    
    Args:
        segments: List of segment dictionaries
        analysis: Segment analysis results with adaptive parameters
        
    Returns:
        List of merged segments
    """
    if not segments or len(segments) <= 1:
        return segments
    
    merged = []
    current = segments[0].copy()
    
    for i in range(1, len(segments)):
        next_seg = segments[i]
        
        # Get merge decision
        should_merge, reason = self.segment_analyzer.should_merge_segments(
            current, next_seg, analysis
        )
        
        if should_merge:
            # Merge segments
            current['end'] = next_seg['end']
            current['text'] = current['text'] + ' ' + next_seg['text']
            
            # Weighted confidence average by duration
            if 'confidence' in current and 'confidence' in next_seg:
                dur_current = current.get('_original_duration', current['end'] - current['start'])
                dur_next = next_seg.get('_original_duration', next_seg['end'] - next_seg['start'])
                total_dur = dur_current + dur_next
                
                weighted_conf = (
                    (current['confidence'] * dur_current + next_seg['confidence'] * dur_next) 
                    / total_dur
                )
                current['confidence'] = weighted_conf
            
            logger.debug(f"Merged segments: {reason}")
        else:
            # Save current and start new
            merged.append(current)
            current = next_seg.copy()
    
    merged.append(current)
    
    logger.info(f"Segment merging: {len(segments)} → {len(merged)} segments "
               f"({(1 - len(merged)/len(segments))*100:.1f}% reduction)")
    return merged
```

---

### Phase 1.2: Enhanced Quality Metrics

**Current Problem**: Averaging confidence ignores distribution shape and segment importance.

**File**: `transcription/quality_metrics.py` (NEW)

```python
"""
Quality Metrics Module
Calculates comprehensive quality metrics for transcription output
"""

from typing import List, Dict, Any
import statistics
import logging

logger = logging.getLogger(__name__)

class QualityMetricsCalculator:
    """
    Calculates detailed quality metrics with weighted scoring.
    """
    
    def calculate_metrics(
        self,
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive quality metrics.
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            Dictionary with detailed quality metrics:
            - confidence_weighted_avg: Confidence weighted by segment duration
            - confidence_percentiles: [p25, p50 (median), p75]
            - degradation_detected: Boolean indicating quality decline
            - segment_count: Number of segments
            - avg_segment_duration: Average segment length in seconds
            - quality_tier: 'excellent'|'good'|'acceptable'|'poor'
        """
        if not segments:
            return self._default_metrics()
        
        confidences = [
            seg.get('confidence', -1.0) 
            for seg in segments 
            if 'confidence' in seg
        ]
        
        if not confidences:
            return self._default_metrics()
        
        # Calculate segment durations for weighting
        durations = [
            seg['end'] - seg['start'] 
            for seg in segments 
            if 'start' in seg and 'end' in seg
        ]
        
        # Weighted confidence: longer segments carry more weight
        total_duration = sum(durations)
        weighted_confidences = []
        for i, seg in enumerate(segments):
            if i < len(durations):
                weight = durations[i] / total_duration if total_duration > 0 else 1
                if 'confidence' in seg:
                    weighted_confidences.append(seg['confidence'] * weight)
        
        weighted_avg = sum(weighted_confidences) if weighted_confidences else 0.0
        
        # Calculate percentiles
        sorted_conf = sorted(confidences)
        p25_idx = int(len(sorted_conf) * 0.25)
        p50_idx = int(len(sorted_conf) * 0.50)
        p75_idx = int(len(sorted_conf) * 0.75)
        
        p25 = sorted_conf[p25_idx] if p25_idx < len(sorted_conf) else sorted_conf[0]
        p50 = sorted_conf[p50_idx] if p50_idx < len(sorted_conf) else sorted_conf[0]
        p75 = sorted_conf[p75_idx] if p75_idx < len(sorted_conf) else sorted_conf[-1]
        
        # Detect degradation: compare early segments to late segments
        mid_point = len(segments) // 2
        early_conf = confidences[:mid_point]
        late_conf = confidences[mid_point:]
        
        early_avg = statistics.mean(early_conf) if early_conf else 0
        late_avg = statistics.mean(late_conf) if late_conf else 0
        
        degradation_detected = (early_avg - late_avg) > 0.3  # > 0.3 is significant
        
        # Determine quality tier
        avg_conf = statistics.mean(confidences)
        if avg_conf > -0.3 and not degradation_detected:
            quality_tier = 'excellent'
        elif avg_conf > -0.8:
            quality_tier = 'good'
        elif avg_conf > -1.2:
            quality_tier = 'acceptable'
        else:
            quality_tier = 'poor'
        
        return {
            'confidence_simple_avg': avg_conf,
            'confidence_weighted_avg': weighted_avg,
            'confidence_percentiles': {
                'p25': p25,
                'p50_median': p50,
                'p75': p75
            },
            'degradation_detected': degradation_detected,
            'early_vs_late_diff': early_avg - late_avg,
            'segment_count': len(segments),
            'avg_segment_duration': statistics.mean(durations) if durations else 0,
            'quality_tier': quality_tier,
            'confidence_std': statistics.stdev(confidences) if len(confidences) > 1 else 0
        }
    
    def _default_metrics(self) -> Dict[str, Any]:
        return {
            'confidence_simple_avg': 0.0,
            'confidence_weighted_avg': 0.0,
            'confidence_percentiles': {'p25': 0, 'p50_median': 0, 'p75': 0},
            'degradation_detected': False,
            'early_vs_late_diff': 0,
            'segment_count': 0,
            'avg_segment_duration': 0,
            'quality_tier': 'unknown',
            'confidence_std': 0
        }
```

---

## 🎯 Phase 2: Batch Processing & Reliability (Weeks 5-8)

### Phase 2.1: Batch Resume & State Management

**Current Problem**: Failed batch stops immediately; no way to resume or track progress.

**File**: `transcription/batch_state_manager.py` (NEW)

```python
"""
Batch State Manager
Manages batch processing state, persistence, and resumable operations
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class FileStatus(str, Enum):
    """Status of a file in batch processing"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

class BatchState:
    """
    Manages batch processing state with JSON persistence.
    Allows resume after crashes or cancellations.
    """
    
    def __init__(self, batch_id: str, state_dir: Path = Path('.batch_state')):
        """
        Initialize batch state manager.
        
        Args:
            batch_id: Unique identifier for this batch (e.g., timestamp-based)
            state_dir: Directory to store state files
        """
        self.batch_id = batch_id
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.state_dir / f"{batch_id}.json"
        self.state: Dict[str, Any] = self._load_state()
        
        logger.info(f"BatchState initialized: {batch_id}")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from disk, or create new"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}. Starting fresh.")
        
        return {
            'batch_id': self.batch_id,
            'created_at': datetime.now().isoformat(),
            'files': {},
            'statistics': {
                'total': 0,
                'completed': 0,
                'failed': 0,
                'skipped': 0
            }
        }
    
    def add_file(self, file_path: str):
        """Register a file in the batch"""
        file_key = str(Path(file_path).resolve())
        self.state['files'][file_key] = {
            'path': file_path,
            'status': FileStatus.PENDING.value,
            'attempts': 0,
            'last_error': None,
            'output_path': None,
            'started_at': None,
            'completed_at': None
        }
        self.state['statistics']['total'] += 1
        self._save_state()
    
    def set_file_status(
        self, 
        file_path: str, 
        status: FileStatus,
        **kwargs
    ):
        """
        Update file status with optional metadata.
        
        Args:
            file_path: Path to the file
            status: FileStatus enum value
            **kwargs: Additional metadata (error, output_path, etc.)
        """
        file_key = str(Path(file_path).resolve())
        if file_key not in self.state['files']:
            self.add_file(file_path)
        
        file_state = self.state['files'][file_key]
        previous_status = file_state['status']
        
        file_state['status'] = status.value
        file_state['updated_at'] = datetime.now().isoformat()
        
        # Update statistics if status changed
        if previous_status != status.value:
            # Decrement old status count
            old_status_key = {
                FileStatus.PENDING.value: 'total',
                FileStatus.IN_PROGRESS.value: None,
                FileStatus.SUCCESS.value: 'completed',
                FileStatus.FAILED.value: 'failed',
                FileStatus.SKIPPED.value: 'skipped'
            }.get(previous_status)
            
            if old_status_key and old_status_key != 'total':
                self.state['statistics'][old_status_key] -= 1
            
            # Increment new status count
            new_status_key = {
                FileStatus.PENDING.value: None,
                FileStatus.IN_PROGRESS.value: None,
                FileStatus.SUCCESS.value: 'completed',
                FileStatus.FAILED.value: 'failed',
                FileStatus.SKIPPED.value: 'skipped'
            }.get(status.value)
            
            if new_status_key:
                self.state['statistics'][new_status_key] += 1
        
        # Store additional metadata
        for key, value in kwargs.items():
            file_state[key] = value
        
        # Track attempts for failed files
        if status == FileStatus.FAILED:
            file_state['attempts'] = file_state.get('attempts', 0) + 1
        
        self._save_state()
        
        logger.debug(f"File status updated: {Path(file_path).name} → {status.value}")
    
    def get_pending_files(self) -> List[str]:
        """Get list of files that haven't been processed yet"""
        return [
            file_state['path']
            for file_state in self.state['files'].values()
            if file_state['status'] in [
                FileStatus.PENDING.value,
                FileStatus.FAILED.value  # Retry failed files
            ]
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current batch statistics"""
        return {
            **self.state['statistics'],
            'success_rate': (
                self.state['statistics']['completed'] / self.state['statistics']['total'] * 100
                if self.state['statistics']['total'] > 0 else 0
            )
        }
    
    def _save_state(self):
        """Persist state to disk"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def cleanup(self):
        """Remove state file after successful completion"""
        try:
            self.state_file.unlink()
            logger.info(f"Cleaned up batch state: {self.batch_id}")
        except Exception as e:
            logger.warning(f"Could not clean up state file: {e}")
```

### Phase 2.2: Enhanced Batch Processor with Recovery

**File**: `transcription/batch_processor.py` (MODIFICATIONS)

```python
def batch_transcribe_files(
    audio_files: List[str],
    model_size: str = WHISPER_MODEL,
    language: str = DEFAULT_LANGUAGE,
    max_workers: Optional[int] = None,
    use_multiprocessing: bool = True,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    enable_resume: bool = True,
    max_retries: int = 2,
    transcriber: Optional[AudioTranscriber] = None
) -> Dict[str, Any]:
    """
    Enhanced batch transcription with resume and retry capabilities.
    
    Args:
        enable_resume: Resume from previous failed batch
        max_retries: Maximum retry attempts per file
        ...existing args...
    """
    from transcription.batch_state_manager import BatchState, FileStatus
    from datetime import datetime
    import uuid
    
    batch_id = str(uuid.uuid4())[:8] + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_state = BatchState(batch_id)
    
    # Register all files
    for audio_file in audio_files:
        batch_state.add_file(audio_file)
    
    batch_state._save_state()
    
    batch_transcriber = BatchTranscriber(
        model_size=model_size,
        language=language,
        max_workers=max_workers,
        use_multiprocessing=use_multiprocessing,
        transcriber=transcriber
    )
    
    return batch_transcriber.transcribe_batch(
        audio_files,
        progress_callback=progress_callback,
        batch_state=batch_state,
        max_retries=max_retries
    )
```

---

## 🎯 Phase 3: Progress & Monitoring (Weeks 9-10)

### Phase 3.1: Event-Driven Progress System

**Current Problem**: Progress updates fire at arbitrary 5% intervals, missing intermediate milestones.

**File**: `transcription/progress_tracker.py` (NEW)

```python
"""
Progress Tracker Module
Event-driven progress tracking with milestone callbacks
"""

from typing import Callable, Optional, List
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """Progress event types"""
    STARTED = "started"
    SEGMENT_COMPLETED = "segment_completed"
    MILESTONE = "milestone"  # 25%, 50%, 75%, 100%
    QUALITY_WARNING = "quality_warning"
    ERROR = "error"
    COMPLETED = "completed"

class ProgressTracker:
    """
    Event-driven progress tracking for transcription operations.
    Replaces percentage-based updates with meaningful milestones.
    """
    
    def __init__(self, total_segments: int, callback: Optional[Callable] = None):
        """
        Initialize progress tracker.
        
        Args:
            total_segments: Total number of segments to process
            callback: Callback function(event_type, data) for progress updates
        """
        self.total_segments = max(total_segments, 1)
        self.completed_segments = 0
        self.callback = callback
        self.start_time = datetime.now()
        self.milestones_hit = set()
        
        if self.callback:
            self._emit_event(EventType.STARTED, {
                'total_segments': total_segments,
                'timestamp': self.start_time.isoformat()
            })
    
    def segment_completed(self, segment_data: dict):
        """
        Record segment completion and emit events.
        
        Args:
            segment_data: Information about the completed segment
        """
        self.completed_segments += 1
        
        # Emit segment event
        if self.callback:
            self._emit_event(EventType.SEGMENT_COMPLETED, {
                'segment_number': self.completed_segments,
                'total': self.total_segments,
                'segment_data': segment_data
            })
        
        # Check for milestones (25%, 50%, 75%, 100%)
        progress_percent = int((self.completed_segments / self.total_segments) * 100)
        milestone = (progress_percent // 25) * 25
        
        if milestone not in self.milestones_hit and milestone > 0:
            self.milestones_hit.add(milestone)
            elapsed = (datetime.now() - self.start_time).total_seconds()
            eta_seconds = (elapsed / self.completed_segments) * (self.total_segments - self.completed_segments)
            
            if self.callback:
                self._emit_event(EventType.MILESTONE, {
                    'milestone_percent': milestone,
                    'completed': self.completed_segments,
                    'total': self.total_segments,
                    'elapsed_seconds': elapsed,
                    'eta_seconds': eta_seconds
                })
    
    def quality_warning(self, warning: str, severity: str = 'medium'):
        """Emit quality warning event"""
        if self.callback:
            self._emit_event(EventType.QUALITY_WARNING, {
                'message': warning,
                'severity': severity,  # 'low'|'medium'|'high'
                'segment_number': self.completed_segments
            })
    
    def error_occurred(self, error: str):
        """Emit error event"""
        if self.callback:
            self._emit_event(EventType.ERROR, {
                'message': error,
                'segment_number': self.completed_segments
            })
    
    def completed(self):
        """Record completion and emit final event"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        if self.callback:
            self._emit_event(EventType.COMPLETED, {
                'total_segments': self.completed_segments,
                'total_time_seconds': total_time,
                'avg_time_per_segment': total_time / self.completed_segments if self.completed_segments > 0 else 0
            })
    
    def _emit_event(self, event_type: EventType, data: dict):
        """Emit progress event"""
        try:
            self.callback(event_type, data)
        except Exception as e:
            logger.error(f"Error in progress callback: {e}")
```

---

## 🎯 Phase 4: Memory & Performance Profiling (Weeks 11-12)

### Phase 4.1: Memory Monitoring

**File**: `core/memory_monitor.py` (NEW)

```python
"""
Memory Monitor Module
Tracks memory usage and provides warnings before OOM conditions
"""

import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryMonitor:
    """
    Monitors memory usage and alerts when approaching limits.
    Useful for batch processing large files.
    """
    
    def __init__(self, warning_threshold_percent: float = 80.0):
        """
        Initialize memory monitor.
        
        Args:
            warning_threshold_percent: Alert when memory usage exceeds this percentage
        """
        self.warning_threshold = warning_threshold_percent
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        
        logger.info(f"Memory monitor initialized. Initial: {self.initial_memory:.1f}MB")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get current memory usage statistics.
        
        Returns:
            Dictionary with memory metrics in MB
        """
        mem_info = self.process.memory_info()
        virtual_mem = psutil.virtual_memory()
        
        current_process_mb = mem_info.rss / (1024 * 1024)
        memory_increase = current_process_mb - self.initial_memory
        
        return {
            'process_memory_mb': current_process_mb,
            'memory_increase_mb': memory_increase,
            'system_memory_percent': virtual_mem.percent,
            'available_memory_mb': virtual_mem.available / (1024 * 1024),
            'timestamp': datetime.now().isoformat()
        }
    
    def check_memory_health(self) -> Dict[str, Any]:
        """
        Check memory health and return warnings if necessary.
        
        Returns:
            Dictionary with health status and warnings
        """
        stats = self.get_memory_stats()
        
        warnings = []
        status = 'healthy'
        
        # Check system memory usage
        if stats['system_memory_percent'] > self.warning_threshold:
            warnings.append(
                f"System memory usage at {stats['system_memory_percent']:.1f}% "
                f"(available: {stats['available_memory_mb']:.1f}MB)"
            )
            status = 'warning'
        
        # Check process memory growth
        if stats['memory_increase_mb'] > 2000:  # 2GB growth
            warnings.append(
                f"Process memory growth: {stats['memory_increase_mb']:.1f}MB. "
                f"Consider reducing batch size."
            )
            status = 'warning'
        
        return {
            'status': status,
            'warnings': warnings,
            'memory_stats': stats
        }
    
    def should_continue_batch(self) -> bool:
        """
        Determine if batch processing should continue.
        
        Returns:
            True if safe to continue, False if approaching OOM
        """
        health = self.check_memory_health()
        
        for warning in health['warnings']:
            logger.warning(f"Memory: {warning}")
        
        # Stop if system memory exceeds 95% or available memory < 500MB
        stats = health['memory_stats']
        if stats['system_memory_percent'] > 95 or stats['available_memory_mb'] < 500:
            logger.error("Memory threshold exceeded. Halting batch processing.")
            return False
        
        return True
```

---

## 🎯 Phase 5: Code Quality & Testing (Weeks 13-14)

### Phase 5.1: Reduce Code Duplication

**Current Problem**: `AudioTranscriber` and `ModelManager` both calculate quality metrics.

**Action Items**:

1. **Create single source of truth** - Move quality metrics to `QualityMetricsCalculator` (Phase 1.2)
2. **Update imports**:
   - `AudioTranscriber` → use `QualityMetricsCalculator`
   - `ModelManager` → use `QualityMetricsCalculator`

### Phase 5.2: Comprehensive Test Suite

**File**: `tests/test_segment_analyzer.py` (NEW)

```python
"""
Tests for Segment Analyzer module
"""

import pytest
from transcription.segment_analyzer import SegmentAnalyzer, SegmentMetrics

class TestSegmentAnalyzer:
    
    def test_analyze_segments_fast_speaker(self):
        """Test adaptive threshold for fast speaker"""
        analyzer = SegmentAnalyzer()
        
        # Fast speaker: ~2.5 wps
        segments = [
            {'start': 0, 'end': 1, 'text': 'Hello how are you', 'confidence': -0.2},
            {'start': 1.2, 'end': 2, 'text': 'doing today', 'confidence': -0.3},
            {'start': 2.1, 'end': 3, 'text': 'everything good', 'confidence': -0.1},
        ]
        
        analysis = analyzer.analyze_segments(segments)
        
        assert analysis['speech_rate'] > 2.0, "Should detect fast speech rate"
        assert analysis['adaptive_threshold'] > 0.5, "Should use larger threshold"
    
    def test_merge_decision_logic(self):
        """Test merge decision logic"""
        analyzer = SegmentAnalyzer()
        
        current = {'start': 0, 'end': 1, 'text': 'Hello', 'confidence': -0.2}
        next_seg = {'start': 1.2, 'end': 2, 'text': 'world', 'confidence': -0.3}
        analysis = {'adaptive_threshold': 0.5}
        
        should_merge, reason = analyzer.should_merge_segments(current, next_seg, analysis)
        
        assert should_merge == True, "Should merge segments with acceptable gap"
        assert 'gap_acceptable' in reason or 'gap_too_large' in reason

# Additional tests...
```

---

## 📊 Implementation Timeline

| Phase | Week | Component | Effort | Priority |
|-------|------|-----------|--------|----------|
| **1** | 1-2 | Segment Analyzer | 6h | **HIGH** |
| **1** | 2-3 | Quality Metrics | 4h | **HIGH** |
| **1** | 4 | Integration & Testing | 4h | **HIGH** |
| **2** | 5-6 | Batch State Manager | 6h | **HIGH** |
| **2** | 7-8 | Resume & Retry Logic | 4h | **HIGH** |
| **3** | 9 | Progress Tracker | 4h | **MEDIUM** |
| **4** | 10 | Memory Monitor | 3h | **MEDIUM** |
| **5** | 11 | Reduce Duplication | 3h | **MEDIUM** |
| **5** | 12-14 | Comprehensive Testing | 8h | **HIGH** |
| | **Total** | | **42 hours** | |

---

## 🚀 Deployment Strategy

### Stage 1: Feature Branch Development
1. Create feature branch: `feature/phase-1-adaptive-merging`
2. Implement all Phase 1 components
3. Write unit tests (90%+ coverage)
4. Code review with focus on backward compatibility

### Stage 2: Integration Testing
1. Test with existing batch processor
2. Verify no regression in performance
3. Run benchmark suite
4. Document API changes

### Stage 3: Beta Release (v2.2.0-beta)
1. Deploy to select users
2. Collect feedback on adaptive merging quality
3. Monitor memory usage in production
4. Iterate on thresholds

### Stage 4: Stable Release (v2.2.0)
1. Address beta feedback
2. Publish migration guide
3. Update documentation
4. Tag release

---

## 🔧 Implementation Quick Start

### To Implement Phase 1.1 (Segment Analyzer):

```bash
# 1. Create new file
touch transcription/segment_analyzer.py

# 2. Copy code from Phase 1.1.1 above

# 3. Create test file
touch tests/test_segment_analyzer.py

# 4. Run tests
pytest tests/test_segment_analyzer.py -v

# 5. Integrate into AudioTranscriber
# Edit transcription/transcribe.py:
# - Import SegmentAnalyzer
# - Replace _merge_segments_smart() calls with _merge_segments_adaptive()

# 6. Run integration tests
pytest tests/test_integration_suite.py::test_adaptive_merging -v
```

### Dependencies to Add

```txt
# setup/requirements.txt - add these if not present:
psutil>=5.9.0          # For memory monitoring
numpy>=1.21.0          # Already present, but needed for statistics
```

---

## 📈 Success Metrics

After implementing all phases, track these metrics:

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Merge Accuracy** | Static threshold | +15% better merges | Manual QA + metrics |
| **Failed Batch Recovery** | 0% (fail + restart) | 95% resume rate | Batch state tracking |
| **Memory Efficiency** | Unmonitored | -20% peak usage | Memory monitor stats |
| **Progress Granularity** | 5% intervals | Segment-level events | Event tracking |
| **Code Duplication** | Moderate | -40% duplication | SonarQube analysis |
| **Test Coverage** | ~60% | 90%+ | pytest --cov |

---

## 🎓 Learning Resources

For developers implementing this roadmap:

1. **Statistical Methods**: Understanding `stdev`, percentiles for distribution analysis
2. **State Management**: JSON serialization, atomic writes for crash-safety
3. **Memory Profiling**: Using `psutil` for system monitoring
4. **Event-Driven Architecture**: Callback patterns and event emission
5. **Concurrency**: Process vs. thread trade-offs for different workloads

---

## ❓ FAQ

**Q: Why replace static thresholds with adaptive ones?**  
A: Speech cadence varies (0.5s gap means different things at 80 vs. 150 wpm). Adaptive thresholds respect context.

**Q: Why track batch state in JSON?**  
A: Humans can inspect/edit state files; enables resume after crashes without losing progress.

**Q: What's the performance impact of memory monitoring?**  
A: ~1-2% overhead; acceptable for batch operations that already take minutes.

**Q: Can I implement phases out of order?**  
A: Phase 1 (algorithms) should come first. Phases 2-4 are independent and can be reordered.

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-04  
**Maintained By**: Development Team  
**Next Review**: After Phase 1 completion
