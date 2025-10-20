#!/usr/bin/env python3
"""
Insightron v1.0.0 - Enhanced Troubleshooting Script
Comprehensive diagnostic and repair tool for Whisper AI Transcriber
Helps diagnose and fix common installation issues with detailed reporting
"""

import sys
import subprocess
import platform
import os

def check_system_info():
    """Display system information"""
    print("🖥️  System Information")
    print("=" * 40)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python executable: {sys.executable}")
    print()

def check_pip():
    """Check pip installation and version"""
    print("📦 Checking pip...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pip version: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ pip not available: {e}")
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

def install_package(package_name):
    """Install a package"""
    print(f"🔄 Installing {package_name}...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                      check=True, capture_output=True)
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e.stderr}")
        return False

def fix_common_issues():
    """Try to fix common installation issues"""
    print("\n🔧 Attempting to fix common issues...")
    
    # Upgrade pip
    print("1. Upgrading pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        print("✅ pip upgraded")
    except:
        print("⚠️  Could not upgrade pip")
    
    # Install wheel
    print("2. Installing wheel...")
    install_package("wheel")
    
    # Install setuptools
    print("3. Installing setuptools...")
    install_package("setuptools")

def main():
    """Main troubleshooting function"""
    print("🔍 Insightron v1.0.0 - Enhanced Troubleshooter")
    print("=" * 60)
    
    check_system_info()
    
    # Check pip
    if not check_pip():
        print("❌ pip is not available. Please install pip first.")
        return
    
    # Fix common issues
    fix_common_issues()
    
    print("\n📋 Checking required packages...")
    print("-" * 30)
    
    required_packages = [
        "numpy",
        "scipy", 
        "tqdm",
        "librosa",
        "soundfile",
        "pydub",
        "whisper",
        "colorama"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("\n🔄 Attempting to install missing packages...")
        
        for package in missing_packages:
            if package == "whisper":
                install_package("openai-whisper")
            else:
                install_package(package)
    else:
        print("\n✅ All required packages are installed!")
    
    print("\n🧪 Testing imports...")
    print("-" * 20)
    
    test_imports = [
        ("numpy", "import numpy"),
        ("scipy", "import scipy"),
        ("tqdm", "import tqdm"),
        ("librosa", "import librosa"),
        ("soundfile", "import soundfile"),
        ("pydub", "import pydub"),
        ("whisper", "import whisper"),
        ("colorama", "import colorama"),
        ("tkinter", "import tkinter")
    ]
    
    for name, import_code in test_imports:
        try:
            exec(import_code)
            print(f"✅ {name} import successful")
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
    
    print("\n🎯 Recommendations:")
    print("-" * 20)
    
    if platform.system() == "Windows":
        print("• If you get Microsoft Visual C++ errors, install Visual Studio Build Tools")
        print("• Try running as Administrator if permission errors occur")
        print("• Consider using conda instead of pip: conda install -c conda-forge whisper")
        print("• Use the Windows installer: install_windows.bat")
    
    print("• If librosa fails, try: pip install librosa --no-cache-dir")
    print("• If whisper fails, try: pip install openai-whisper --no-cache-dir")
    print("• For audio issues, install ffmpeg: https://ffmpeg.org/download.html")
    print("• Try minimal installation: pip install -r requirements-minimal.txt")
    print("• Run enhanced installer: python install_dependencies.py")
    
    print("\n🚀 Quick Start:")
    print("• GUI Mode: python insightron.py")
    print("• CLI Mode: python cli.py audio.mp3")
    print("• Setup: python setup.py")
    
    print("\n✨ Troubleshooting complete!")

if __name__ == "__main__":
    main()
