#!/usr/bin/env python3
"""
Whisper AI Transcriber - Main Application
A modern GUI application for transcribing audio files using OpenAI's Whisper AI
and saving the results to your Obsidian workspace.
"""

import os
import sys
import argparse
from pathlib import Path

# Fix for MKL memory allocation error
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'

# Force UTF-8 output on Windows (use reconfigure to avoid closing stdout)
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        # Fallback: ignore if reconfigure fails
        pass

# Add current directory to Python path  
sys.path.append(str(Path(__file__).parent))

try:
    from gui.gui import InsightronGUI
    import customtkinter as ctk
    from transcription.batch_processor import batch_transcribe_files
    from core.config import WHISPER_MODEL, DEFAULT_LANGUAGE
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies:")
    print("pip install -r setup/requirements.txt")
    sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import faster_whisper
    except ImportError:
        missing_deps.append("faster-whisper")
    
    try:
        import librosa
    except ImportError:
        missing_deps.append("librosa")
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install them using:")
        print("pip install -r setup/requirements.txt")
        return False
    
    return True

def check_obsidian_path():
    """Check if Obsidian path is configured correctly"""
    from core.config import OBSIDIAN_VAULT_PATH, TRANSCRIPTION_FOLDER
    
    if not OBSIDIAN_VAULT_PATH.exists():
        print(f"⚠️  Warning: Obsidian vault path doesn't exist: {OBSIDIAN_VAULT_PATH}")
        print("Please update the OBSIDIAN_VAULT_PATH in config.py")
        return False
    
    if not TRANSCRIPTION_FOLDER.exists():
        print(f"📁 Creating transcription folder: {TRANSCRIPTION_FOLDER}")
        TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)
    
    return True

def run_gui():
    """Run the GUI application"""
    print("✅ All checks passed!")
    print("🚀 Starting GUI application...")
    
    try:
        # Create and run the GUI
        # System settings for CustomTkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        
        root = ctk.CTk()
        app = InsightronGUI(root)
        
        # Center the window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def run_batch(args):
    """Run batch processing from CLI"""
    print("🚀 Starting Batch Processing...")
    
    input_path = Path(args.input)
    audio_files = []
    
    if input_path.is_file():
        audio_files = [str(input_path)]
    elif input_path.is_dir():
        # Find all supported audio files
        supported_exts = {'.mp3', '.wav', '.m4a', '.flac', '.mp4', '.ogg', '.aac', '.wma'}
        for ext in supported_exts:
            audio_files.extend([str(p) for p in input_path.glob(f"*{ext}")])
    else:
        print(f"❌ Error: Input path not found: {input_path}")
        sys.exit(1)
        
    if not audio_files:
        print(f"❌ No audio files found in: {input_path}")
        sys.exit(1)
        
    print(f"Found {len(audio_files)} files to process.")
    
    try:
        results = batch_transcribe_files(
            audio_files=audio_files,
            model_size=args.model,
            language=args.language,
            max_workers=args.workers,
            use_multiprocessing=True,
            progress_callback=lambda c, t, f: print(f"[{c}/{t}] Processing: {f}")
        )
        
        print("\nBatch Processing Complete!")
        print(f"Total time: {results['statistics']['total_time_seconds']:.2f}s")
        print(f"Successful: {len(results['successful'])}")
        print(f"Failed: {len(results['failed'])}")
        
        if results['failed']:
            print("\nFailed files:")
            for fail in results['failed']:
                print(f" - {fail['file']}: {fail['error']}")
                
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")
        sys.exit(1)

def main():
    """Main application entry point"""
    print("🎤 Whisper AI Transcriber")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Obsidian path
    if not check_obsidian_path():
        print("Please fix the configuration and try again.")
        sys.exit(1)
        
    # Parse arguments
    parser = argparse.ArgumentParser(description="Insightron - AI Audio Transcriber")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Run batch transcription')
    batch_parser.add_argument('--input', '-i', required=True, help='Input file or directory')
    batch_parser.add_argument('--workers', '-w', type=int, default=None, help='Number of worker processes')
    batch_parser.add_argument('--model', '-m', default=WHISPER_MODEL, help='Whisper model size')
    batch_parser.add_argument('--language', '-l', default=DEFAULT_LANGUAGE, help='Language code')
    
    args = parser.parse_args()
    
    if args.command == 'batch':
        run_batch(args)
    else:
        run_gui()

if __name__ == "__main__":
    main()