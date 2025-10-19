#!/usr/bin/env python3
"""
Enhanced Setup Script for Insightron
Optimized installation process with better error handling, progress tracking,
and faster dependency management for the Whisper AI transcription project.
"""

import subprocess
import sys
import os
import time
import logging
from pathlib import Path
from typing import List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command: str, description: str, timeout: int = 300) -> Tuple[bool, str]:
    """
    Run a command with enhanced error handling and timeout support.
    
    Args:
        command: Command to execute
        description: Human-readable description of the command
        timeout: Timeout in seconds (default: 5 minutes)
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    logger.info(f"Executing: {description}")
    print(f"Running: {description}...")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Command completed in {elapsed:.1f}s")
        print(f"SUCCESS: {description} completed successfully ({elapsed:.1f}s)")
        return True, result.stdout
        
    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after {timeout}s"
        logger.error(error_msg)
        print(f"TIMEOUT: {description} timed out after {timeout}s")
        return False, error_msg
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed with return code {e.returncode}: {e.stderr}"
        logger.error(error_msg)
        print(f"ERROR: {description} failed:")
        print(f"Error: {e.stderr}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        print(f"ERROR: {description} failed with unexpected error: {e}")
        return False, error_msg

def check_python_version() -> bool:
    """
    Check if Python version is compatible with Insightron.
    
    Returns:
        True if compatible, False otherwise
    """
    version = sys.version_info
    min_version = (3, 8)
    
    if version[:2] < min_version:
        logger.error(f"Python {min_version[0]}.{min_version[1]}+ required, got {version.major}.{version.minor}")
        print("Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    logger.info(f"Python version check passed: {version.major}.{version.minor}.{version.micro}")
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies() -> bool:
    """
    Install required dependencies with optimized installation strategy.
    
    Returns:
        True if installation successful, False otherwise
    """
    logger.info("Starting dependency installation process")
    print("\n📦 Installing dependencies...")
    
    # Upgrade pip first with timeout
    success, _ = run_command(
        f"{sys.executable} -m pip install --upgrade pip", 
        "Upgrading pip",
        timeout=120
    )
    if not success:
        logger.warning("pip upgrade failed, continuing with installation")
        print("Warning: pip upgrade failed, continuing anyway...")
    
    # Try installing from requirements.txt first
    logger.info("Attempting installation from requirements.txt")
    success, output = run_command(
        f"{sys.executable} -m pip install -r requirements.txt --no-cache-dir", 
        "Installing from requirements.txt",
        timeout=600  # 10 minutes for full installation
    )
    
    if success:
        logger.info("Successfully installed from requirements.txt")
        print("Successfully installed from requirements.txt")
        return True
    
    logger.warning("requirements.txt installation failed, trying minimal installation")
    print("requirements.txt failed, trying minimal installation...")
    
    # Fallback to minimal requirements
    success, output = run_command(
        f"{sys.executable} -m pip install -r requirements-minimal.txt --no-cache-dir", 
        "Installing minimal requirements",
        timeout=300  # 5 minutes for minimal installation
    )
    
    if success:
        logger.info("Successfully installed minimal requirements")
        print("Successfully installed minimal requirements")
        return True
    
    logger.error("Both installation methods failed")
    print("Both installation methods failed")
    print("Try running: python troubleshoot.py")
    return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    try:
        from config import TRANSCRIPTION_FOLDER
        TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Created transcription folder: {TRANSCRIPTION_FOLDER}")
        return True
    except Exception as e:
        print(f"Failed to create directories: {e}")
        return False

def test_installation():
    """Test if the installation works"""
    print("\nTesting installation...")
    
    try:
        # Test imports
        import whisper
        import librosa
        import tkinter
        print("All core modules imported successfully")
        
        # Test basic functionality
        from transcribe import AudioTranscriber
        print("Transcription module loaded successfully")
        
        return True
    except ImportError as e:
        print(f"Import test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Whisper AI Transcriber Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\nSetup failed during dependency installation")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\nSetup failed during directory creation")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\nSetup failed during testing")
        sys.exit(1)
    
    print("\nSetup completed successfully!")
    print("\nYou can now run the application:")
    print("   python main.py          # GUI mode")
    print("   python cli.py audio.mp3 # CLI mode")
    print("\nSee README.md for detailed usage instructions")

if __name__ == "__main__":
    main()
