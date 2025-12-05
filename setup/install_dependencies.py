#!/usr/bin/env python3
"""
Insightron v2.2.0 - Enhanced Dependency Installer
Cross-platform installer with Windows optimization, better error handling,
and comprehensive dependency management for the Whisper AI transcription tool.
"""

import subprocess
import sys
import os
import shutil
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

def check_rust_installed():
    """Check if Rust/Cargo is installed and add to PATH if found in default location."""
    if shutil.which("cargo"):
        return True
    
    # Check default Windows location
    cargo_home = Path.home() / ".cargo" / "bin"
    if cargo_home.exists() and (cargo_home / "cargo.exe").exists():
        print(f"⚠️  Found Cargo at {cargo_home}, but it's not in PATH.")
        print("   Adding it to PATH for this session...")
        os.environ["PATH"] += os.pathsep + str(cargo_home)
        return True
    
    return False

def run_command(command, description, exit_on_fail=False):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}...")
    try:
        # Use shell=True for windows compatibility with some commands
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        if exit_on_fail:
            sys.exit(1)
        return False

def main():
    """Main installation process"""
    print("🎤 Insightron v2.2.0 - Enhanced Dependency Installer")
    print("=" * 60)
    
    # Display platform information
    import platform
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    
    # Check Python version compatibility
    if sys.version_info.minor >= 13:
        print("\n⚠️  WARNING: You are using Python 3.{}".format(sys.version_info.minor))
        print("   Many scientific packages (like onnxruntime) do not yet support Python 3.13+.")
        print("   We STRONGLY recommend using Python 3.10, 3.11, or 3.12.")
        print("   The installation is likely to fail.\n")
        response = input("   Do you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Check for Rust
    rust_available = check_rust_installed()
    if not rust_available:
        print("⚠️  Rust/Cargo not found. Some packages (like tokenizers) may fail to install")
        print("   if pre-built wheels are not available for your Python version.")
        print("   If installation fails, please install Rust from https://rustup.rs/")

    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        print("❌ Failed to upgrade pip. Please check your Python installation.")
        # Continue anyway as it might not be critical
    
    # Install NumPy with pre-compiled wheel (Windows-specific)
    print("\n🔧 Installing NumPy with Windows-optimized approach...")
    
    # Try different NumPy installation strategies
    numpy_commands = [
        f"{sys.executable} -m pip install numpy --prefer-binary --upgrade",
        f"{sys.executable} -m pip install numpy --only-binary=all"
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
    
    # Get script directory for proper path resolution
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Install other dependencies
    print("\n📦 Installing other dependencies...")
    requirements_path = script_dir / "setup" / "requirements.txt"
    if not requirements_path.exists():
         # Fallback if running from setup dir
         requirements_path = script_dir / "requirements.txt"
         if not requirements_path.exists():
             print("❌ ERROR: requirements.txt not found")
             print(f"   Searched in: {script_dir}")
             print("   Please run this script from the Insightron root directory")
             return False

    if not run_command(f"{sys.executable} -m pip install -r {requirements_path} --prefer-binary", "Installing requirements"):
        print("❌ Failed to install some dependencies via requirements.txt")
        
        # Specific check for tokenizers
        print("\n🔍 Attempting to fix common issues...")
        if not run_command(f"{sys.executable} -m pip install tokenizers --prefer-binary", "Installing tokenizers separately"):
             print("❌ Failed to install 'tokenizers'.")
             if not rust_available:
                 print("💡 It looks like you need to install Rust to build 'tokenizers' from source.")
                 print("   Please install Rust from: https://rustup.rs/")
                 return False
        
        # Try minimal requirements
        print("\n⚠️  Trying minimal requirements...")
        minimal_req_path = script_dir / "setup" / "requirements-minimal.txt"
        if not minimal_req_path.exists():
            minimal_req_path = script_dir / "requirements-minimal.txt"
            if not minimal_req_path.exists():
                print("❌ ERROR: requirements-minimal.txt not found")
                return False
            
        if not run_command(f"{sys.executable} -m pip install -r {minimal_req_path} --prefer-binary", "Installing minimal requirements"):
             print("❌ Minimal installation also failed.")
             return False

    # Verify installation
    print("\n🔍 Verifying installation...")
    try:
        import numpy
        import faster_whisper
        import librosa
        import soundfile
        import pydub
        import customtkinter
        import sounddevice
        print("✅ All core dependencies are working!")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        # Adjust import path if needed
        sys.path.append(os.getcwd())
        try:
             from transcription.transcribe import AudioTranscriber
             print("✅ Transcription module loaded successfully!")
        except ImportError:
             print("⚠️  Could not load AudioTranscriber (might be path issue), but dependencies look ok.")
             
        return True
    except ImportError as e:
        print(f"❌ Verification failed: {e}")
        print("💡 Try running: python scripts/troubleshoot.py")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Installation completed successfully!")
        print("   You can now run:")
        print("   • python insightron.py    # GUI mode (recommended)")
        print("   • python cli.py audio.mp3  # Command line mode")
        print("   • python scripts/troubleshoot.py  # For diagnostics")
    else:
        print("\n💥 Installation failed. Please check the errors above.")
        print("   Try running: python scripts/troubleshoot.py")
        sys.exit(1)
