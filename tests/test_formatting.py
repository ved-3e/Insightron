#!/usr/bin/env python3
"""
Test script to demonstrate text formatting capabilities
"""

from transcription.text_formatter import format_transcript

# Sample transcript (your example)
sample_text = """one thing that I have recognized is that see I am the molar-type face of clearing and I am purifying my earth element and also my cellular intelligence is getting sharper and also all the cells are being out-chose to divine frequencies and also this is the last step of completing the 3D Transcendence and being liberated while living. What happens is that some certain karma manifests as things like the past reminders of... there isn't exact connection between what I'm experiencing and what my internal state says about the incident. There's things happening sharp, disturbing, things happening and they dissolve in minutes, not in minutes, in seconds. They dissolve in the things that happen through me. I take longer sleep than usual and my detox is really higher. Those are the common entries. But external things, subtle karma or the liberation or something strikes my mind for the good happens only after these disturbing incidents and then my mind goes on taking those and I get clarity on what to do on my projects, where to move towards and what to seek. Yet I didn't reach my full productivity. I feel very tired and also all of the energy is going for the Mooladhara to purify and transcend itself, to transform itself. Yet this is living ahead in sectors. So wonderful, so cosmical that I feel the Arjuna to the Krishna, the cosmic consciousness itself. And this clarity is superb."""

def test_formatting():
    print("Text Formatting Test")
    print("=" * 50)
    
    print("\nOriginal Text:")
    print("-" * 30)
    print(sample_text)
    
    print("\nAuto Formatting:")
    print("-" * 30)
    auto_formatted = format_transcript(sample_text, "auto")
    print(auto_formatted)
    
    print("\nParagraph Formatting (3 sentences per paragraph):")
    print("-" * 30)
    paragraph_formatted = format_transcript(sample_text, "paragraphs")
    print(paragraph_formatted)
    
    print("\nMinimal Formatting (5 sentences per paragraph):")
    print("-" * 30)
    minimal_formatted = format_transcript(sample_text, "minimal")
    print(minimal_formatted)

if __name__ == "__main__":
    test_formatting()
