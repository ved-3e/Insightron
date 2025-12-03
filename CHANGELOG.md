Here is a Keep a Changelog–style `CHANGELOG.md` you can drop into your repo and tweak dates as needed.[1]

# Changelog

All notable changes to Insightron will be documented in this file.[1]

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).[1]

## [2.0.0] - 2025-12-03

### Added
- ✅ **Model Manager & Caching**: Central `ModelManager` for sharing a single Whisper/faster-whisper model instance across single, batch, and realtime modes, eliminating repeated load delays.[1]
- ✅ **Distil-Whisper Models**: Support for `distil-medium.en` and `distil-large-v2` for significantly faster English transcription.[1]
- ✅ **Realtime Buffering**: Deque-based buffering for smoother, low-latency realtime transcription and reduced CPU overhead.[1]
- ✅ **Benchmark Suite**: `benchmark_insightron.py`, sample audio, and `benchmark_results.json` to measure performance across models and modes.[1]

### Changed
- 🔄 **Batch Processing**: Batch mode now reuses a shared model instance for all files to maximize throughput.[1]
- 🔄 **Decoding Strategy**: Smarter beam search defaults with dynamic beam size tuned for either speed or accuracy.[1]
- 🔄 **Configuration**: `config.yaml` extended with model, device, and compute-type options aligned with the new Model Manager.[1]
- 🔄 **Architecture**: Project modularized into `core`, `transcription`, `realtime`, `gui`, `setup`, `scripts`, and `tests` for clearer separation of concerns.[1]

### Technical Details
- Added a centralized `ModelManager` used across CLI, GUI, batch, and realtime pipelines.[1]
- Updated `config.yaml` schema to capture model preferences, device selection, and compute type (e.g., INT8).[1]
- Refactored core logic from `insightron.py` into dedicated modules under `core/`, `transcription/`, and `realtime/`.[1]
- Introduced benchmarking flow that generates test audio, runs single, batch, and realtime simulations, and saves metrics to JSON.[1]

***

## [1.3.0] - 2025-12-01

### Added
- ✅ **Realtime Mode (GUI)**: New “Realtime” tab for live microphone transcription with on-screen text as you speak.[1]
- ✅ **Audio Level Visualization**: Dynamic audio meter to monitor input levels during recording.[1]
- ✅ **Dual Saving**: Automatic saving of both raw audio (e.g., WAV) and Markdown transcript for each realtime session.[1]
- ✅ **Realtime Obsidian Integration**: Realtime transcripts saved directly into the configured Obsidian vault folder.[1]

### Changed
- 🔄 **User Settings**: `user_settings.json` extended to persist realtime preferences (model, language, folders).[1]
- 🔄 **Status & Logging**: GUI log and status bar updated to show realtime recording state, latency, and save locations.[1]

### Technical Details
- Added a dedicated `realtime/` module for microphone capture, buffering, and streaming transcription.[1]
- Integrated realtime pipeline with existing formatting and Markdown export to keep output consistent.[1]

***

## [1.2.0] - 2025-12-01

### Added
- ✅ **faster-whisper Backend**: Migrated core transcription engine from `openai-whisper` to `faster-whisper` (CTranslate2).[1]
- ✅ **INT8 Quantization**: Support for compute-type selection (e.g., `int8`) to optimize CPU performance.[1]
- ✅ **GPU Auto-Detection**: Automatic use of CUDA GPU when available for major speedups.[1]

### Changed
- 🔄 **Performance**: Up to roughly 4x faster transcription on CPU/GPU with significantly lower RAM usage, especially for medium/large models.[1]
- 🔄 **Progress Reporting**: Improved segment-level progress updates for smoother UX in both CLI and GUI.[1]

### Technical Details
- Updated transcription pipeline to call faster-whisper models with configurable device and compute-type parameters.[1]
- Adjusted default model recommendations and docs to highlight `distil-medium.en` and faster-whisper–based models.[1]

***

## [1.1.0] - 2025-10-20

### Added
- ✅ **Multi-Language Support**: Comprehensive support for 100+ languages via Whisper’s full language set.[1]
  - Auto-detection of language from audio content.[1]
  - Manual language selection for improved accuracy.[1]
  - Coverage of major, European, Asian, and Middle Eastern/African languages, plus many more.[1]
- ✅ **UTF-8 Encoding**: Proper handling of non-Latin scripts and special characters in all transcripts.[1]
- ✅ **GUI Language Selector**: Easy language selection directly in the graphical interface.[1]
- ✅ **CLI Language Support**: Command-line language selection via `-l/--language`.[1]
- ✅ **Language Validation**: Automatic fallback to auto-detection for invalid or unsupported language codes.[1]
- ✅ **Enhanced Logging**: More detailed language detection and processing information in logs.[1]

### Changed
- 🔄 **Version**: Updated from v1.0.0 to v1.1.0.[1]
- 🔄 **Documentation**: Added comprehensive multi-language examples and usage guides in README and usage docs.[1]
- 🔄 **Configuration**: Introduced language-related configuration options to `config` and runtime settings.[1]
- 🔄 **Transcription Engine**: Extended to support language-specific parameters and behavior.[1]
- 🔄 **GUI Interface**: Added a language dropdown with all supported language options.[1]
- 🔄 **CLI Interface**: Extended CLI parser to accept `-l, --language` for language selection.[1]

### Technical Details
- Added `SUPPORTED_LANGUAGES` configuration mapping for 100+ languages.[1]
- Enhanced the transcription classes and functions to accept a language parameter.[1]
- Improved UTF-8 handling throughout the pipeline for international character sets.[1]
- Implemented validation and fallback logic when an unsupported language is requested.[1]

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

***

## [1.0.0] – 2025-10-20

### Added
- ✅ Initial public release of Insightron.[1]
- ✅ Whisper AI integration with multiple model sizes (tiny, base, small, medium, large).[1]
- ✅ Modern macOS-inspired dark GUI interface.[1]
- ✅ Command-line interface with rich options for model, language, formatting, and output paths.[1]
- ✅ Obsidian integration for seamless, Markdown-first note-taking workflows.[1]
- ✅ Smart text formatting with multiple styles (auto, paragraphs, minimal, etc.).[1]
- ✅ Comprehensive audio format support (MP3, WAV, M4A, FLAC, MP4, OGG, AAC, WMA).[1]
- ✅ Atomic file operations to ensure data safety during writes.[1]
- ✅ Progress tracking and real-time status updates during transcription.[1]
- ✅ Cross-platform compatibility (Windows, macOS, Linux).[1]
- ✅ Robust error handling and validation for files, paths, and runtime issues.[1]
- ✅ Detailed documentation and examples for both GUI and CLI usage.[1]
- ✅ Performance-oriented defaults and memory-efficient processing.[1]
- ✅ Audio metadata extraction (duration, size, etc.) embedded in output.[1]
- ✅ Timestamp support for transcript segments.[1]
- ✅ Rich Markdown output with Obsidian-friendly frontmatter and metadata.[1]
- ✅ Troubleshooting and diagnostic helpers for installation and runtime issues.[1]

***

**Legend:**
- ✅ Added  
- 🔄 Changed  
- ❌ Deprecated  
- 🗑️ Removed  
- 🐛 Fixed  
- 🔒 Security  