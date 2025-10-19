#!/usr/bin/env python3
"""
Performance Benchmark Suite for Insightron
Measures performance metrics and provides optimization recommendations.
"""

import time
import psutil
import sys
import os
from pathlib import Path
import tempfile
import logging
from typing import Dict, List, Tuple
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from transcribe import AudioTranscriber
from text_formatter import TextFormatter, format_transcript
from utils import create_markdown

# Configure logging
logging.basicConfig(level=logging.WARNING)

class PerformanceBenchmark:
    """Comprehensive performance benchmarking for Insightron components."""
    
    def __init__(self):
        self.results = {}
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict:
        """Get system information for context."""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'python_version': sys.version,
            'platform': sys.platform
        }
    
    def benchmark_text_formatter(self) -> Dict:
        """Benchmark text formatter performance."""
        print("🧪 Benchmarking Text Formatter...")
        
        formatter = TextFormatter()
        
        # Test data of varying sizes
        test_cases = [
            ("Small text", "Hello world this is a test sentence."),
            ("Medium text", "Hello world this is a test sentence. " * 50),
            ("Large text", "Hello world this is a test sentence. " * 500),
            ("Very large text", "Hello world this is a test sentence. " * 2000)
        ]
        
        results = {}
        
        for name, text in test_cases:
            print(f"  Testing {name} ({len(text)} chars)...")
            
            # Test clean_text
            start_time = time.time()
            cleaned = formatter.clean_text(text)
            clean_time = time.time() - start_time
            
            # Test format_text
            start_time = time.time()
            formatted = formatter.format_text(text)
            format_time = time.time() - start_time
            
            # Test custom structure
            start_time = time.time()
            custom = formatter.format_with_custom_structure(text, 3)
            custom_time = time.time() - start_time
            
            results[name] = {
                'text_length': len(text),
                'clean_time': clean_time,
                'format_time': format_time,
                'custom_time': custom_time,
                'total_time': clean_time + format_time + custom_time,
                'chars_per_second': len(text) / (clean_time + format_time + custom_time)
            }
        
        return results
    
    def benchmark_markdown_creation(self) -> Dict:
        """Benchmark markdown creation performance."""
        print("🧪 Benchmarking Markdown Creation...")
        
        test_cases = [
            ("Small transcript", "This is a short transcript."),
            ("Medium transcript", "This is a medium length transcript. " * 100),
            ("Large transcript", "This is a large transcript with many sentences. " * 1000),
            ("Very large transcript", "This is a very large transcript with many sentences. " * 5000)
        ]
        
        results = {}
        
        for name, text in test_cases:
            print(f"  Testing {name} ({len(text)} chars)...")
            
            start_time = time.time()
            markdown = create_markdown(
                filename="benchmark_test",
                text=text,
                date="2024-01-01 12:00:00",
                duration="10:00",
                model="medium",
                duration_seconds=600.0,
                file_size_mb=5.0,
                language="en",
                segments=[{'start': 0, 'end': 600, 'text': text}]
            )
            end_time = time.time()
            
            results[name] = {
                'text_length': len(text),
                'markdown_length': len(markdown),
                'creation_time': end_time - start_time,
                'chars_per_second': len(text) / (end_time - start_time)
            }
        
        return results
    
    def benchmark_memory_usage(self) -> Dict:
        """Benchmark memory usage patterns."""
        print("🧪 Benchmarking Memory Usage...")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024**2)  # MB
        
        # Test text formatter memory usage
        formatter = TextFormatter()
        large_text = "This is a test sentence. " * 10000
        
        memory_before = process.memory_info().rss / (1024**2)
        formatted_text = formatter.format_text(large_text)
        memory_after = process.memory_info().rss / (1024**2)
        
        formatter_memory = memory_after - memory_before
        
        # Test markdown creation memory usage
        memory_before = process.memory_info().rss / (1024**2)
        markdown = create_markdown(
            filename="memory_test",
            text=large_text,
            date="2024-01-01 12:00:00",
            duration="10:00",
            model="medium",
            duration_seconds=600.0,
            file_size_mb=5.0,
            language="en"
        )
        memory_after = process.memory_info().rss / (1024**2)
        
        markdown_memory = memory_after - memory_before
        
        return {
            'initial_memory_mb': initial_memory,
            'formatter_memory_mb': formatter_memory,
            'markdown_memory_mb': markdown_memory,
            'total_memory_mb': memory_after - initial_memory
        }
    
    def benchmark_concurrent_operations(self) -> Dict:
        """Benchmark concurrent text processing operations."""
        print("🧪 Benchmarking Concurrent Operations...")
        
        import threading
        import queue
        
        formatter = TextFormatter()
        test_text = "This is a test sentence for concurrent processing. " * 100
        results_queue = queue.Queue()
        
        def process_text(text_id):
            start_time = time.time()
            result = formatter.format_text(test_text)
            end_time = time.time()
            results_queue.put({
                'thread_id': text_id,
                'processing_time': end_time - start_time,
                'result_length': len(result)
            })
        
        # Test with different numbers of concurrent threads
        thread_counts = [1, 2, 4, 8]
        results = {}
        
        for thread_count in thread_counts:
            print(f"  Testing with {thread_count} threads...")
            
            threads = []
            start_time = time.time()
            
            for i in range(thread_count):
                thread = threading.Thread(target=process_text, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            
            # Collect results
            thread_results = []
            while not results_queue.empty():
                thread_results.append(results_queue.get())
            
            results[f'{thread_count}_threads'] = {
                'total_time': end_time - start_time,
                'thread_count': thread_count,
                'avg_processing_time': sum(r['processing_time'] for r in thread_results) / len(thread_results),
                'throughput': thread_count / (end_time - start_time)
            }
        
        return results
    
    def run_all_benchmarks(self) -> Dict:
        """Run all benchmarks and return comprehensive results."""
        print("🚀 Starting Insightron Performance Benchmarks")
        print("=" * 60)
        
        all_results = {
            'system_info': self.system_info,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'text_formatter': self.benchmark_text_formatter(),
            'markdown_creation': self.benchmark_markdown_creation(),
            'memory_usage': self.benchmark_memory_usage(),
            'concurrent_operations': self.benchmark_concurrent_operations()
        }
        
        self.results = all_results
        return all_results
    
    def print_summary(self):
        """Print a summary of benchmark results."""
        if not self.results:
            print("No benchmark results available. Run benchmarks first.")
            return
        
        print("\n" + "=" * 60)
        print("📊 BENCHMARK SUMMARY")
        print("=" * 60)
        
        # System info
        print(f"🖥️  System: {self.system_info['cpu_count']} cores, {self.system_info['memory_gb']}GB RAM")
        print(f"🐍 Python: {self.system_info['python_version'].split()[0]}")
        
        # Text formatter performance
        print("\n📝 Text Formatter Performance:")
        for name, data in self.results['text_formatter'].items():
            print(f"  {name}: {data['chars_per_second']:.0f} chars/sec")
        
        # Markdown creation performance
        print("\n📄 Markdown Creation Performance:")
        for name, data in self.results['markdown_creation'].items():
            print(f"  {name}: {data['chars_per_second']:.0f} chars/sec")
        
        # Memory usage
        print(f"\n💾 Memory Usage:")
        print(f"  Text Formatter: {self.results['memory_usage']['formatter_memory_mb']:.1f} MB")
        print(f"  Markdown Creation: {self.results['memory_usage']['markdown_memory_mb']:.1f} MB")
        
        # Concurrent operations
        print(f"\n🔄 Concurrent Operations:")
        for name, data in self.results['concurrent_operations'].items():
            print(f"  {name}: {data['throughput']:.2f} ops/sec")
    
    def save_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON file."""
        if not self.results:
            print("No benchmark results to save.")
            return
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📁 Results saved to: {filename}")
    
    def get_recommendations(self) -> List[str]:
        """Get performance optimization recommendations based on results."""
        recommendations = []
        
        if not self.results:
            return ["Run benchmarks first to get recommendations"]
        
        # Text formatter recommendations
        text_perf = self.results['text_formatter']
        avg_chars_per_sec = sum(data['chars_per_second'] for data in text_perf.values()) / len(text_perf)
        
        if avg_chars_per_sec < 1000:
            recommendations.append("Text formatter performance is slow. Consider optimizing regex patterns.")
        
        # Memory usage recommendations
        memory_usage = self.results['memory_usage']
        if memory_usage['total_memory_mb'] > 100:
            recommendations.append("High memory usage detected. Consider processing smaller chunks.")
        
        # Concurrent operations recommendations
        concurrent = self.results['concurrent_operations']
        single_thread_throughput = concurrent['1_threads']['throughput']
        multi_thread_throughput = max(data['throughput'] for data in concurrent.values())
        
        if multi_thread_throughput < single_thread_throughput * 1.5:
            recommendations.append("Limited concurrency benefits. Consider thread pool optimization.")
        
        # System recommendations
        if self.system_info['memory_gb'] < 4:
            recommendations.append("Low memory system. Use smaller models or process shorter audio files.")
        
        if self.system_info['cpu_count'] < 4:
            recommendations.append("Limited CPU cores. Consider using smaller models for better performance.")
        
        return recommendations

def main():
    """Main benchmark execution function."""
    print("🎤 Insightron Performance Benchmark Suite")
    print("=" * 60)
    
    benchmark = PerformanceBenchmark()
    
    try:
        # Run all benchmarks
        results = benchmark.run_all_benchmarks()
        
        # Print summary
        benchmark.print_summary()
        
        # Get recommendations
        recommendations = benchmark.get_recommendations()
        if recommendations:
            print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Save results
        benchmark.save_results()
        
        print(f"\n✅ Benchmark completed successfully!")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
