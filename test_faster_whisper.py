import sys
import time
from pathlib import Path

def test_faster_whisper():
    print("🧪 Testing faster-whisper installation...")
    
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper imported successfully")
    except ImportError:
        print("❌ faster-whisper not found. Please run: pip install -r requirements.txt")
        return

    print("\n🔄 Loading 'tiny' model (int8)...")
    start_time = time.time()
    try:
        model = WhisperModel("tiny", device="auto", compute_type="int8")
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f}s")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    print("\n✨ System is ready for high-performance transcription!")
    print("   Run 'python insightron.py' to start the GUI.")

if __name__ == "__main__":
    test_faster_whisper()
