"""
Configuration file for Insightron
Contains paths and settings for the transcription application
"""
from pathlib import Path
import os

# Whisper model configuration
WHISPER_MODEL = "medium"  # Options: tiny, base, small, medium, large

# Path to your Obsidian Vault
OBSIDIAN_VAULT_PATH = Path(r"D:\2. Areas\IdeaVerse\Areas")

# Folder inside vault for transcription outputs
TRANSCRIPTION_FOLDER = OBSIDIAN_VAULT_PATH / "Insights"

# Ensure folder exists
TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)

# Supported audio formats
SUPPORTED_FORMATS = {
    '.mp3', '.wav', '.m4a', '.flac', 
    '.mp4', '.ogg', '.aac', '.wma'
}

# Whisper model information
WHISPER_MODELS = {
    'tiny': {'size': '~39M params', 'speed': 'Fastest', 'accuracy': 'Good'},
    'base': {'size': '~74M params', 'speed': 'Fast', 'accuracy': 'Better'},
    'small': {'size': '~244M params', 'speed': 'Moderate', 'accuracy': 'Good'},
    'medium': {'size': '~769M params', 'speed': 'Slower', 'accuracy': 'Very Good'},
    'large': {'size': '~1550M params', 'speed': 'Slowest', 'accuracy': 'Best'}
}

# Formatting styles
FORMATTING_STYLES = {
    'auto': 'Smart paragraph breaks based on content',
    'paragraphs': 'New paragraph every 3 sentences',
    'minimal': 'New paragraph every 5 sentences'
}

# Application metadata
APP_NAME = "Insightron"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered audio transcription with Whisper"

# Maximum file size (in MB)
MAX_FILE_SIZE_MB = 500  # Increased from 25MB for larger files

# Logging configuration
LOG_LEVEL = "INFO"

print(f"✓ Insightron Config Loaded")
print(f"  - Model: {WHISPER_MODEL}")
print(f"  - Output: {TRANSCRIPTION_FOLDER}")
print(f"  - Vault: {OBSIDIAN_VAULT_PATH}")