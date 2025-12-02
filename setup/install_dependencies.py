#!/usr/bin/env python3
"""
Insightron v1.0.0 - Enhanced Dependency Installer
Cross-platform installer with Windows optimization, better error handling,
and comprehensive dependency management for the Whisper AI transcription tool.
"""

import subprocess
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
        pass

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main installation process"""
    print("🎤 Insightron v1.0.0 - Enhanced Dependency Installer")
    print("=" * 60)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("⚠️  This installer is optimized for Windows")
        print("   For other platforms, use: pip install -r requirements.txt")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        print("❌ Failed to upgrade pip. Please check your Python installation.")
        return False
    
    # Install NumPy with pre-compiled wheel (Windows-specific)
    print("\n🔧 Installing NumPy with Windows-optimized approach...")
    
    # Try different NumPy installation strategies
    numpy_commands = [
        "python -m pip install numpy --only-binary=all --upgrade",
        "python -m pip install numpy --prefer-binary"
    ]
    
    numpy_installed = False
    for cmd in numpy_commands:
        if run_command(cmd, f"Installing NumPy with: {cmd.split()[-1]}"):
            numpy_installed = True
            break
    
    if not numpy_installed:
        print("❌ Failed to install NumPy. Please try installing Visual Studio Build Tools:")
        print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        return False
    
    # Install other dependencies
    print("\n📦 Installing other dependencies...")
    if not run_command("python -m pip install -r requirements.txt", "Installing requirements"):
        print("❌ Failed to install some dependencies")
        return False
    
    # Verify installation
    print("\n🔍 Verifying installation...")
    try:
        import numpy
        import whisper
        import librosa
        import tkinter
        import soundfile
        import pydub
        print("✅ All core dependencies are working!")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        from transcribe import AudioTranscriber
        print("✅ Transcription module loaded successfully!")
        return True
    except ImportError as e:
        print(f"❌ Verification failed: {e}")
        print("💡 Try running: python troubleshoot.py")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Installation completed successfully!")
        print("   You can now run:")
        print("   • python insightron.py    # GUI mode (recommended)")
        print("   • python cli.py audio.mp3  # Command line mode")
        print("   • python troubleshoot.py  # For diagnostics")
    else:
        print("\n💥 Installation failed. Please check the errors above.")
        print("   Try running: python troubleshoot.py")
        sys.exit(1)
