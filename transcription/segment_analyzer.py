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
        
        avg_gap = statistics.mean(gaps) if gaps else 0.3
        std_dev_gap = statistics.stdev(gaps) if len(gaps) > 1 else 0
        avg_duration = statistics.mean(durations) if durations else 3.0
        avg_speech_rate = statistics.mean(speech_rates) if speech_rates else 1.5
        
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
        if std_dev_gap > 0.2 and avg_gap > 0:
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

