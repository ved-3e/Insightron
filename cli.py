#!/usr/bin/env python3
"""
Enhanced Command Line Interface for Insightron
Optimized CLI for quick and efficient audio transcriptions with improved UX.
"""

import sys
import argparse
import logging
import time
from pathlib import Path
from typing import Optional
from transcribe import AudioTranscriber
from config import WHISPER_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Enhanced main function with improved argument parsing and error handling."""
    parser = argparse.ArgumentParser(
        description="Insightron - Enhanced Whisper AI Transcriber CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audio.mp3                    # Basic transcription
  %(prog)s audio.wav -m large -v        # Use large model with verbose output
  %(prog)s audio.m4a -f paragraphs      # Use paragraph formatting
  %(prog)s audio.flac -m tiny -f minimal # Fast transcription with minimal formatting
        """
    )
    
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    parser.add_argument("-m", "--model", default=WHISPER_MODEL, 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size to use (default: %(default)s)")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Enable verbose output with detailed progress")
    parser.add_argument("-f", "--format", default="auto", 
                       choices=["auto", "paragraphs", "minimal"],
                       help="Text formatting style (default: %(default)s)")
    parser.add_argument("--output", "-o", type=str,
                       help="Custom output path for the transcript file")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Suppress all output except errors")
    
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check if file exists
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        logger.error(f"Audio file not found: {audio_path}")
        print(f"❌ Error: Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Validate file extension
    supported_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.mp4', '.ogg', '.aac', '.wma'}
    if audio_path.suffix.lower() not in supported_extensions:
        logger.error(f"Unsupported file format: {audio_path.suffix}")
        print(f"❌ Error: Unsupported file format: {audio_path.suffix}")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        sys.exit(1)
    
    try:
        start_time = time.time()
        
        if not args.quiet:
            print(f"🎤 Insightron - Whisper AI Transcriber")
            print(f"📁 File: {audio_path.name}")
            print(f"🤖 Model: {args.model}")
            print(f"🎨 Format: {args.format}")
            print("-" * 50)
        
        # Initialize transcriber
        logger.info(f"Initializing transcriber with model: {args.model}")
        transcriber = AudioTranscriber(args.model)
        
        # Progress callback for CLI
        def progress_callback(message: str) -> None:
            if args.verbose and not args.quiet:
                print(f"⏳ {message}")
            logger.debug(f"Progress: {message}")
        
        # Transcribe file
        logger.info(f"Starting transcription of {audio_path}")
        output_path, transcription_data = transcriber.transcribe_file(
            str(audio_path), 
            progress_callback=progress_callback,
            formatting_style=args.format
        )
        
        # Handle custom output path
        if args.output:
            custom_output = Path(args.output)
            custom_output.parent.mkdir(parents=True, exist_ok=True)
            output_path.rename(custom_output)
            output_path = custom_output
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Show results
        if not args.quiet:
            print(f"\n✅ Transcription completed in {processing_time:.1f}s!")
            print(f"📄 Output: {output_path}")
            print(f"⏱️  Duration: {transcription_data['duration']}")
            print(f"📊 File Size: {transcription_data['file_size_mb']:.1f} MB")
            print(f"🌍 Language: {transcription_data['language']}")
            print(f"📝 Characters: {len(transcription_data['text']):,}")
            
            if 'processing_time_seconds' in transcription_data:
                print(f"⚡ Processing Speed: {transcription_data.get('characters_per_second', 0):.1f} chars/sec")
            
            if args.verbose:
                print(f"\n📝 Preview of transcript:")
                print("-" * 50)
                preview = transcription_data['text'][:300]
                print(preview + "..." if len(transcription_data['text']) > 300 else preview)
        
        logger.info(f"Transcription completed successfully: {output_path}")
        
    except KeyboardInterrupt:
        logger.info("Transcription interrupted by user")
        print("\n⏹️  Transcription interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
