"""
Configuration file for Insightron
Contains paths and settings for the transcription application
"""
from pathlib import Path
import os

# Whisper model configuration
WHISPER_MODEL = "medium"  # Options: tiny, base, small, medium, large

# Path to your Obsidian Vault (for backward compatibility)
OBSIDIAN_VAULT_PATH = Path(r"D:\2. Areas\Ideaverse\Areas")

# Directory Configuration
# TRANSCRIPTION_FOLDER: Where to save transcriptions
TRANSCRIPTION_FOLDER = Path(r"D:\2. Areas\Ideaverse\Areas\Insights")

# RECORDINGS_FOLDER: Where to save audio recordings
RECORDINGS_FOLDER = Path(r"D:\2. Areas\Ideaverse\Areas\Recordings")

# Ensure folders exist
TRANSCRIPTION_FOLDER.mkdir(parents=True, exist_ok=True)
RECORDINGS_FOLDER.mkdir(parents=True, exist_ok=True)

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
APP_VERSION = "1.3.0"
APP_DESCRIPTION = "AI-powered audio transcription with Whisper - Multi-language support"

# Maximum file size (in MB)
MAX_FILE_SIZE_MB = 500  # Increased from 25MB for larger files

# Logging configuration
LOG_LEVEL = "INFO"

# Multi-language support configuration
SUPPORTED_LANGUAGES = {
    'auto': 'Auto-detect language',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'tr': 'Turkish',
    'pl': 'Polish',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'ro': 'Romanian',
    'bg': 'Bulgarian',
    'hr': 'Croatian',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'et': 'Estonian',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'el': 'Greek',
    'he': 'Hebrew',
    'fa': 'Persian',
    'ur': 'Urdu',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
    'mr': 'Marathi',
    'ne': 'Nepali',
    'si': 'Sinhala',
    'my': 'Burmese',
    'km': 'Khmer',
    'lo': 'Lao',
    'ka': 'Georgian',
    'am': 'Amharic',
    'sw': 'Swahili',
    'zu': 'Zulu',
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'az': 'Azerbaijani',
    'eu': 'Basque',
    'be': 'Belarusian',
    'bs': 'Bosnian',
    'ca': 'Catalan',
    'cy': 'Welsh',
    'eo': 'Esperanto',
    'gl': 'Galician',
    'is': 'Icelandic',
    'ga': 'Irish',
    'mk': 'Macedonian',
    'mt': 'Maltese',
    'mn': 'Mongolian',
    'ms': 'Malay',
    'oc': 'Occitan',
    'ps': 'Pashto',
    'rm': 'Romansh',
    'sn': 'Shona',
    'so': 'Somali',
    'tg': 'Tajik',
    'tk': 'Turkmen',
    'uk': 'Ukrainian',
    'uz': 'Uzbek',
    'yi': 'Yiddish',
    'yo': 'Yoruba'
}

# Language detection configuration
DEFAULT_LANGUAGE = "auto"  # Auto-detect by default
ENABLE_LANGUAGE_DETECTION = True
ENABLE_MANUAL_LANGUAGE_SELECTION = True

# UTF-8 encoding configuration
ENSURE_UTF8_ENCODING = True
OUTPUT_ENCODING = "utf-8"

print(f"✓ Insightron Config Loaded v{APP_VERSION}")
print(f"  - Model: {WHISPER_MODEL}")
print(f"  - Output: {TRANSCRIPTION_FOLDER}")
print(f"  - Languages: {len(SUPPORTED_LANGUAGES)} supported")
