#!/usr/bin/env python3
"""
Whisper AI Transcriber - Main Application
A modern GUI application for transcribing audio files using OpenAI's Whisper AI
and saving the results to your Obsidian workspace.
"""

import sys
import os
from pathlib import Path

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
    from gui import InsightronGUI
    import tkinter as tk
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import whisper
    except ImportError:
        missing_deps.append("openai-whisper")
    
    try:
        import librosa
    except ImportError:
        missing_deps.append("librosa")
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter (usually comes with Python)")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install them using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_obsidian_path():
    """Check if Obsidian path is configured correctly"""
    from config import OBSIDIAN_VAULT_PATH, TRANSCRIPTION_FOLDER
    
    if not OBSIDIAN_VAULT_PATH.exists():
        print(f"⚠️  Warning: Obsidian vault path doesn't exist: {OBSIDIAN_VAULT_PATH}")
        print("Please update the OBSIDIAN_VAULT_PATH in config.py")
        return False
    
    if not TRANSCRIPTION_FOLDER.exists():
        print(f"📁 Creating transcription folder: {TRANSCRIPTION_FOLDER}")
        TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)
    
    return True

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
    
    print("✅ All checks passed!")
    print("🚀 Starting GUI application...")
    
    try:
        # Create and run the GUI
        root = tk.Tk()
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

if __name__ == "__main__":
    main()
