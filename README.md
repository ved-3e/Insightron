# 🎤 Insightron v2.0.0 - Next-Gen AI Transcriber

**Transform audio into beautifully structured insights with lightning-fast precision.**

Insightron is a next-generation transcription application powered by **faster-whisper** (CTranslate2), featuring a stunning dark-themed GUI, batch processing capabilities, and seamless Obsidian integration. Experience up to **6x faster transcription** with **Distil-Whisper** models, instant model reuse, and optimized realtime performance.

## ✨ Key Features

### 🚀 **Performance & Reliability**
- **⚡ faster-whisper Engine**: Up to **4x faster** transcription using CTranslate2 optimization
- **🔥 Distil-Whisper Support**: Up to **6x faster** inference with `distil-medium.en` and `distil-large-v2`
- **🔄 Instant Model Reuse**: Zero-delay start for subsequent transcriptions
- **🧠 Lower Memory Usage**: INT8 quantization for efficient CPU processing
- **🎯 GPU Acceleration**: Automatic CUDA detection for maximum speed
- **📊 Real-time Progress**: Segment-level progress updates for smooth UX
- **💾 Smart File Operations**: Atomic writes prevent data corruption
- **🔧 Cross-Platform**: Seamless Windows, macOS, and Linux support
- **🔴 Realtime Transcription**: Low-latency live audio capture with automatic Obsidian note saving

### 🎨 **Modern Dark-Black Theme** ✨
- **Pure Black Background**: Material Dark theme perfect for OLED screens
- **Premium Color Palette**: 
  - 🔵 Bright Blue for Model selection
  - 🟣 Purple for Language selection
  - 🟢 Emerald for Formatting options
- **Tabbed Interface**: Dedicated tabs for Single File, Batch Mode, and Realtime
- **Settings Persistence**: Your preferences automatically saved
- **Compact Timestamped Logs**: Terminal-style output with `[HH:MM:SS]` timestamps
- **Smooth Hover Effects**: Premium animations throughout the UI

### 🎵 **Audio Excellence**
- **Universal Format Support**: MP3, WAV, M4A, FLAC, MP4, OGG, AAC, WMA
- **Smart Format Detection**: Automatic audio format recognition
- **Quality Optimization**: Model-specific parameters for best results
- **File Size Validation**: Automatic 500MB limit checking
- **Enhanced Audio Processing**: Improved librosa and soundfile integration

### 🌍 **Multi-Language Support**
- **100+ Languages**: Support for all Whisper-supported languages including English, Spanish, French, German, Chinese, Japanese, Arabic, Hindi, and many more
- **Auto-Detection**: Intelligent language detection for multilingual content
- **Manual Selection**: Choose specific languages for optimal accuracy
- **UTF-8 Encoding**: Perfect support for non-Latin scripts and special characters
- **Language-Aware Processing**: Optimized transcription parameters for each language

### 📝 **Intelligent Text Processing**
- **Smart Formatting**: Auto-detects paragraph breaks and sentence structure
- **Filler Word Removal**: Cleans up "um", "uh", and repetitive phrases
- **Transcription Fixes**: Corrects common Whisper AI errors
- **Multiple Styles**: Auto, paragraph, and minimal formatting options

### 🔗 **Obsidian Integration**
- **Seamless Workflow**: Direct save to your Obsidian vault
- **Rich Metadata**: Duration, file size, language, processing time
- **Timestamp Support**: Optional segment-by-segment timestamps
- **Tag System**: Automatic tagging for easy organization

## 🚀 Quick Start

### 1. **One-Click Installation**

```bash
# Download and setup Insightron
git clone https://github.com/ved-3e/Insightron.git
cd Insightron

# Automated setup (recommended)
python setup.py

# Windows users - use the enhanced installer
install_windows.bat

# Cross-platform installer
python install_dependencies.py

# Or manual installation
pip install -r requirements.txt
```

### 2. **Configuration**

Update `config.py` with your Obsidian vault path:

```python
# Path to your Obsidian Vault
OBSIDIAN_VAULT_PATH = Path(r"D:\2. Areas\IdeaVerse\Areas")

# Folder inside vault for insights
TRANSCRIPTION_FOLDER = OBSIDIAN_VAULT_PATH / "Insights"
```

### 3. **Launch Insightron**

**🎨 GUI Mode (Recommended):**
```bash
python insightron.py
```

**⚡ Command Line Mode:**
```bash
# Basic transcription with auto-detection
python cli.py audio.mp3

# Advanced options with language selection
python cli.py audio.wav -m large -v -f paragraphs -l es

# Multi-language examples
python cli.py spanish_audio.mp3 -l es -m medium
python cli.py french_audio.wav -l fr -f auto
python cli.py chinese_audio.m4a -l zh -m large
python cli.py arabic_audio.mp3 -l ar -v
```

## 📖 Usage Guide

### **GUI Interface**

#### **Single File Mode**
1. **Launch**: Run `python insightron.py`
2. **Select Tab**: Use "Single File" tab (default)
3. **Choose Audio**: Click "📁 Choose Audio File"
4. **Configure Settings**: Select Model (try `distil-medium.en` for speed!), Language, and Formatting
5. **Transcribe**: Click "⚡ Start Transcription"
6. **Monitor**: Watch real-time progress in the status bar and timestamped log
7. **Review**: Open output folder when complete

#### **Batch Mode** 📦
1. **Switch Tab**: Click "Batch Mode" tab
2. **Select Files**: 
   - Click "📄 Choose Files" to select multiple audio files
   - OR click "📂 Choose Folder" to process an entire folder
3. **Process**: Click "⚡ Process All Files"
4. **Monitor**: Track progress as each file is completed in the log
5. **Review**: Check summary statistics when finished

#### **Realtime Mode** 🔴
1. **Switch Tab**: Click "Realtime" tab
2. **Configure**: Select Model and Language
3. **Start**: Click "🔴 Start Recording"
4. **Speak**: Speak into your microphone
5. **Visualize**: See real-time audio levels and text generation
6. **Stop**: Click "⏹️ Stop Recording" to save audio and transcript

### **Command Line Interface**

```bash
# Basic usage
python cli.py audio.mp3

# With specific model
python cli.py audio.mp3 -m large

# Custom formatting
python cli.py audio.mp3 -f paragraphs

# Verbose output
python cli.py audio.mp3 -v

# Custom output location
python cli.py audio.mp3 -o /path/to/output.md

# Quiet mode (minimal output)
python cli.py audio.mp3 -q
```

### **CLI Options**

| Option | Description | Default |
|--------|-------------|---------|
| `-m, --model` | Whisper model size (tiny, base, small, medium, large, distil-medium.en, distil-large-v2) | medium |
| `-f, --format` | Text formatting (auto, paragraphs, minimal) | auto |
| `-l, --language` | Language code (en, es, fr, de, zh, ja, ar, etc.) or 'auto' | auto |
| `-v, --verbose` | Enable detailed progress output | False |
| `-o, --output` | Custom output file path | Auto-generated |
| `-q, --quiet` | Suppress all output except errors | False |

## 📁 Project Structure

```
insightron/
├── insightron.py                 # 🚀 Main application entry point
├── gui.py                  # 🎨 Modern CustomTkinter GUI
├── cli.py                  # ⚡ Command line interface
├── batch_processor.py      # 📦 Batch processing for multiple files
├── realtime_transcriber.py # 🔴 Real-time audio transcription engine
├── transcribe.py           # 🧠 Core transcription engine
├── text_formatter.py       # 📝 Intelligent text processing
├── utils.py                # 🔧 Utility functions
├── config.py               # ⚙️ Configuration settings
├── setup.py                # 🛠️ Automated setup script
├── troubleshoot.py         # 🔍 Enhanced diagnostic and repair tool
├── install_dependencies.py # 📦 Cross-platform dependency installer
├── install_windows.bat     # 📦 Windows-optimized installer
├── requirements.txt        # 📦 Full dependencies (v2.0.0)
├── requirements-minimal.txt # 📦 Minimal dependencies
├── test_formatting.py      # 🧪 Text formatting tests
├── test_macos_gui.py       # 🧪 GUI interface tests
└── README.md              # 📖 This documentation
```

## 🌍 Multi-Language Support

### **Supported Languages**

Insightron supports **100+ languages** including all major world languages:

#### **Major Languages**
- **English** (en) - Default, highest accuracy
- **Spanish** (es) - Español
- **French** (fr) - Français  
- **German** (de) - Deutsch
- **Chinese** (zh) - 中文 (Mandarin)
- **Japanese** (ja) - 日本語
- **Korean** (ko) - 한국어
- **Arabic** (ar) - العربية
- **Hindi** (hi) - हिन्दी
- **Russian** (ru) - Русский
- **Portuguese** (pt) - Português
- **Italian** (it) - Italiano

#### **Additional Languages**
- **European**: Dutch, Swedish, Norwegian, Danish, Finnish, Polish, Czech, Hungarian, Romanian, Bulgarian, Croatian, Slovak, Slovenian, Estonian, Latvian, Lithuanian, Greek, Welsh, Irish, Maltese, Albanian, Basque, Catalan, Galician
- **Asian**: Thai, Vietnamese, Burmese, Khmer, Lao, Mongolian, Tamil, Telugu, Malayalam, Kannada, Gujarati, Punjabi, Marathi, Nepali, Sinhala, Bengali
- **Middle Eastern/African**: Persian, Urdu, Hebrew, Amharic, Swahili, Zulu, Afrikaans
- **And many more...**

### **Language Usage Examples**

```bash
# Auto-detection (recommended for most cases)
python cli.py audio.mp3 -l auto

# Specific language selection for better accuracy
python cli.py spanish_meeting.mp3 -l es -m medium
python cli.py french_podcast.wav -l fr -m large
python cli.py chinese_lecture.m4a -l zh -v
python cli.py arabic_news.mp3 -l ar -f paragraphs
python cli.py hindi_interview.wav -l hi -m medium
```

### **Language Selection Tips**

- **Auto-detection**: Use `auto` or leave blank for most cases - Whisper is very good at detecting languages
- **Manual selection**: Specify language for better accuracy, especially with:
  - Background noise or poor audio quality
  - Mixed-language content where you want to prioritize one language
  - Less common languages where auto-detection might be uncertain
- **UTF-8 Support**: All non-Latin scripts (Chinese, Arabic, Hindi, etc.) are fully supported with proper UTF-8 encoding

## 🎯 Whisper Model Guide

### **Model Comparison**

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| **tiny** | ~39 MB | ⚡⚡⚡ | ⭐⭐ | Quick drafts, testing |
| **base** | ~74 MB | ⚡⚡ | ⭐⭐⭐ | Balanced performance |
| **small** | ~244 MB | ⚡ | ⭐⭐⭐⭐ | High quality, good speed |
| **medium** | ~769 MB | ⚡ | ⭐⭐⭐⭐⭐ | **Recommended** |
| **large-v2** | ~1550 MB | ⚡ | ⭐⭐⭐⭐⭐ | Maximum accuracy |
| **distil-medium.en** | ~394 MB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | **Best Speed/Accuracy** (English only) |
| **distil-large-v2** | ~756 MB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | High accuracy, faster than large |

### **Performance Tips**

- **RAM**: 4GB+ recommended for medium model, 8GB+ for large
- **Storage**: ~2GB for all models combined
- **CPU**: Multi-core processor recommended
- **GPU**: CUDA support available for 3-5x speedup

## 📊 Output Format

Transcripts are saved as beautifully formatted Markdown files with rich metadata:

```markdown
---
title: my_audio_file
date: 2024-01-15 14:30:25
duration: 5:23
duration_seconds: 323.4
file_size: 12.5 MB
model: medium
language: en
formatting: auto
tags: [transcription, audio-note, whisper]
created: 2024-01-15 14:30:25
---

# 🎤 Transcription: my_audio_file

## 📊 Metadata
- **Duration:** 5:23 (323.4 seconds)
- **File Size:** 12.5 MB
- **Model:** medium
- **Language:** en
- **Formatting:** Auto
- **Transcribed:** 2024-01-15 14:30:25

## 📝 Transcript

Your beautifully formatted transcript here with intelligent paragraph breaks...

## 🕐 Timestamps

**00:00 - 00:15:** First segment of speech
**00:15 - 00:30:** Second segment of speech
...

---
*Transcribed using Insightron*  
*Generated on 2024-01-15 14:30:25*
```

## 🛠️ Troubleshooting

### **Common Issues & Solutions**

#### **Installation Problems**
```bash
# Enhanced troubleshooting
python troubleshoot.py

# Cross-platform installer
python install_dependencies.py

# Windows-specific installer
install_windows.bat

# Manual dependency installation
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

#### **Audio File Issues**
- **File too large**: Whisper has a 500MB limit (increased from 25MB) - use audio compression for larger files
- **Unsupported format**: Insightron supports MP3, WAV, M4A, FLAC, MP4, OGG, AAC, WMA
- **Corrupted file**: Try a different audio file or run diagnostics

#### **Performance Issues**
- **Slow transcription**: Use `distil-medium.en` or smaller models (tiny, base, small)
- **Memory errors**: Close other applications, use tiny model
- **GPU not detected**: Install CUDA toolkit for GPU acceleration

#### **Obsidian Integration**
- **Path not found**: Update `OBSIDIAN_VAULT_PATH` in `config.py`
- **Permission denied**: Run as administrator or check folder permissions
- **Files not appearing**: Refresh Obsidian or check the correct folder

### **System Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8+ | 3.9+ |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 2GB | 5GB+ |
| **CPU** | Dual-core | Quad-core+ |
| **OS** | Windows 10, macOS 10.14, Linux | Latest versions |

## 🧪 Testing

### **Run Tests**
```bash
# Test text formatting
python test_formatting.py

# Test GUI interface
python test_macos_gui.py

# Enhanced diagnostics
python troubleshoot.py

# Test full functionality
python -m pytest
```

### **Performance Benchmarks**
- **Tiny Model**: ~2x real-time speed
- **Base Model**: ~1.5x real-time speed  
- **Small Model**: ~1x real-time speed
- **Medium Model**: ~0.8x real-time speed
- **Large Model**: ~0.5x real-time speed
- **Distil-Medium**: ~5x real-time speed (New!)

## 🎨 Customization

### **Custom Text Formatting**
Edit `text_formatter.py` to add your own formatting rules:

```python
# Add custom transcription fixes
self._transcription_fixes.append(
    (re.compile(r'\byour_pattern\b', re.IGNORECASE), 'Your Replacement')
)
```

### **Custom Output Templates**
Modify `utils.py` to change the markdown template:

```python
def create_markdown(filename, text, date, duration, model, ...):
    # Your custom template here
    return custom_template
```

### **GUI Themes**
Update `gui.py` to modify colors and styling:

```python
self.colors = {
    'accent': '#your_color',      # Primary accent color
    'bg_primary': '#your_bg',     # Background color
    'text_primary': '#your_text', # Text color
    # ... more colors
}
```

## 📈 Performance Optimization

### **Speed Improvements**
- Use `distil-medium.en` for lightning-fast English transcription
- Use `tiny` or `base` models for faster multi-language transcription
- Enable GPU acceleration with CUDA
- Close unnecessary applications during transcription
- Use SSD storage for better I/O performance

### **Memory Optimization**
- Process shorter audio files
- Use smaller models for large files
- Enable memory-efficient processing in config

### **Quality Improvements**
- Use `medium` or `large` models for better accuracy
- Ensure good audio quality (clear speech, minimal background noise)
- Use appropriate formatting style for your content type

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### **Development Setup**
```bash
# Clone your fork
git clone https://github.com/ved-3e/Insightron.git
cd Insightron

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run enhanced diagnostics
python troubleshoot.py

# Run tests
python -m pytest

# Format code
black *.py
```

## 🙏 Acknowledgments

- **OpenAI** for the incredible Whisper AI model
- **The open-source community** for audio processing libraries
- **Obsidian** for the excellent note-taking platform
- **Contributors** who help improve Insightron

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ved-3e/Insightron/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ved-3e/Insightron/discussions)
- **Documentation**: [Wiki](https://github.com/ved-3e/Insightron/wiki)

---

**Happy Transcribing! 🎤✨**

*Transform audio into structured wisdom — locally, beautifully, intelligently.*

**Insightron v2.0.0** - Speed, Efficiency, and Intelligence

## 🆕 What's New in v2.0.0

### **🚀 Performance Revolution**
- ✅ **Instant Model Reuse**: Implemented smart caching to eliminate model loading delays (10-20s saved per file)
- ✅ **Distil-Whisper Support**: Added `distil-medium.en` and `distil-large-v2` for **6x faster** transcription
- ✅ **Optimized Realtime**: New `deque`-based buffering for lower latency and CPU usage
- ✅ **Enhanced Batch Mode**: Shared model instance across batch files for maximum throughput
- ✅ **Smart Beam Search**: Dynamic beam size adjustment (1 for speed, 5 for accuracy)

### **Previous Updates (v1.3.0)**

### **🔴 Realtime Transcription**
- ✅ **Live Audio Capture**: Record and transcribe microphone input in real-time
- ✅ **Instant Feedback**: See text appear as you speak
- ✅ **Audio Visualization**: Dynamic audio level meter
- ✅ **Dual Saving**: Saves both audio recording (WAV) and transcription (MD)
- ✅ **Obsidian Integration**: Auto-saves directly to your vault

### **Previous Updates (v1.2.0)**

### **🚀 Performance Engine Swap**
- ✅ **faster-whisper Integration**: Migrated from `openai-whisper` to `faster-whisper` (CTranslate2)
- ✅ **4x Speed Boost**: Up to 4x faster transcription on both CPU and GPU
- ✅ **Lower Memory Usage**: Significantly reduced RAM consumption
- ✅ **INT8 Quantization**: Optimized for CPU with minimal accuracy loss
- ✅ **GPU Auto-Detection**: Automatic CUDA acceleration when available
- ✅ **Real-time Progress**: Segment-level progress tracking for smooth UX

### **🎨 Modern Dark-Black Theme**
- ✅ **Pure Black Background**: Material Dark theme (`#000000`) perfect for OLED
- ✅ **Premium Color Palette**: Bright Blue, Purple, and Emerald accents
- ✅ **Polished Cards**: Subtle borders and improved spacing
- ✅ **Enhanced Typography**: Larger icons and better font hierarchy
- ✅ **Smooth Animations**: Premium hover effects throughout

### **📦 Batch Processing**
- ✅ **Tabbed Interface**: Dedicated "Batch Mode" tab
- ✅ **Multi-File Selection**: Process multiple files or entire folders at once
- ✅ **Optimized Engine**: Reuses model instance for faster batch processing
- ✅ **Thread Pool**: Concurrent processing for maximum throughput
- ✅ **Progress Tracking**: Real-time updates for each file

### **💾 Settings Persistence**
- ✅ **Automatic Saving**: Model, Language, and Formatting preferences saved to `user_settings.json`
- ✅ **Auto-Load**: Settings restored on startup
- ✅ **Seamless UX**: No need to reconfigure every session

### **📝 Compact Timestamped Logs**
- ✅ **Terminal-Style Output**: Professional log format with `[HH:MM:SS]` timestamps
- ✅ **Smaller Font**: Consolas 11pt for compact display
- ✅ **Clean Messages**: Concise, informative status updates

### **Previous Updates (v1.1.0)**
- ✅ **100+ Languages**: Support for all Whisper-supported languages
- ✅ **UTF-8 Encoding**: Perfect support for non-Latin scripts