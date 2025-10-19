#!/usr/bin/env python3
"""
Windows-compatible dependency installer for Insightron
Handles NumPy installation issues on Windows by using pre-compiled wheels
"""

import subprocess
import sys
import os
from pathlib import Path

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
    print("🎤 Insightron - Windows Dependency Installer")
    print("=" * 50)
    
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
        "python -m pip install numpy==1.24.4 --only-binary=all",
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
        print("✅ All core dependencies are working!")
        return True
    except ImportError as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Installation completed successfully!")
        print("   You can now run: python main.py")
    else:
        print("\n💥 Installation failed. Please check the errors above.")
        sys.exit(1)
