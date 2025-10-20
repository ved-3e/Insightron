# Changelog

All notable changes to Insightron will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-01-15

### Added
- **Multi-Language Support**: Comprehensive support for 100+ languages
  - Auto-detection of language from audio content
  - Manual language selection for improved accuracy
  - Support for all Whisper-supported languages including:
    - Major languages: English, Spanish, French, German, Chinese, Japanese, Korean, Arabic, Hindi, Russian, Portuguese, Italian
    - European languages: Dutch, Swedish, Norwegian, Danish, Finnish, Polish, Czech, Hungarian, Romanian, Bulgarian, Croatian, Slovak, Slovenian, Estonian, Latvian, Lithuanian, Greek, Welsh, Irish, Maltese, Albanian, Basque, Catalan, Galician
    - Asian languages: Thai, Vietnamese, Burmese, Khmer, Lao, Mongolian, Tamil, Telugu, Malayalam, Kannada, Gujarati, Punjabi, Marathi, Nepali, Sinhala, Bengali
    - Middle Eastern/African languages: Persian, Urdu, Hebrew, Amharic, Swahili, Zulu, Afrikaans
    - And many more
- **UTF-8 Encoding**: Proper handling of non-Latin scripts and special characters
- **GUI Language Selector**: Easy language selection in the graphical interface
- **CLI Language Support**: Command-line language selection with `-l` flag
- **Language Validation**: Automatic fallback to auto-detection for invalid languages
- **Enhanced Logging**: Better language detection and processing information

### Changed
- **Version**: Updated from v1.0.0 to v1.1.0
- **Documentation**: Comprehensive multi-language examples and usage guides
- **Configuration**: Added language support configuration options
- **Transcription Engine**: Enhanced to support language-specific parameters
- **GUI Interface**: Added language selection dropdown with 100+ language options
- **CLI Interface**: Added `-l, --language` parameter for language selection

### Technical Details
- Added `SUPPORTED_LANGUAGES` configuration with 100+ language mappings
- Enhanced `AudioTranscriber` class with language support
- Updated `transcribe_file` method to accept language parameter
- Improved UTF-8 encoding handling for international character sets
- Added language validation and fallback mechanisms
- Enhanced error handling for language-related issues

### Examples
```bash
# Auto-detection (recommended)
python cli.py audio.mp3 -l auto

# Specific languages
python cli.py spanish_audio.mp3 -l es -m medium
python cli.py french_audio.wav -l fr -m large
python cli.py chinese_audio.m4a -l zh -v
python cli.py arabic_audio.mp3 -l ar -f paragraphs
python cli.py hindi_audio.wav -l hi -m medium
```

## [1.0.0] - 2024-01-01

### Added
- Initial release of Insightron
- Whisper AI integration with 5 model sizes (tiny, base, small, medium, large)
- Modern macOS-inspired GUI interface
- Command-line interface with comprehensive options
- Obsidian integration for seamless note-taking workflow
- Smart text formatting with multiple styles
- Comprehensive audio format support (MP3, WAV, M4A, FLAC, MP4, OGG, AAC, WMA)
- Atomic file operations for data safety
- Progress tracking and real-time updates
- Cross-platform compatibility (Windows, macOS, Linux)
- Comprehensive error handling and validation
- Detailed documentation and examples
- Performance optimization and memory efficiency
- Audio metadata extraction and processing
- Timestamp support for transcript segments
- Rich markdown output with frontmatter
- Troubleshooting and diagnostic tools

---

**Legend:**
- ✅ Added
- 🔄 Changed  
- ❌ Deprecated
- 🗑️ Removed
- 🐛 Fixed
- 🔒 Security
