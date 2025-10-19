#!/usr/bin/env python3
"""
Enhanced Text Formatter for Insightron
Intelligently formats transcribed text with proper structure, punctuation, and paragraph breaks.
Optimized for performance and accuracy with improved error handling.
"""

import re
import logging
from typing import List, Tuple, Dict, Set
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextFormatter:
    """
    Enhanced text formatter with improved performance and accuracy.
    Uses caching and optimized regex patterns for better speed.
    """
    
    def __init__(self):
        # Common sentence starters that indicate new paragraphs (converted to sets for O(1) lookup)
        self.paragraph_starters: Set[str] = {
            "what happens is", "what i notice is", "what i realize is",
            "the thing is", "the problem is", "the issue is",
            "however", "but", "yet", "so", "and so", "therefore",
            "meanwhile", "additionally", "furthermore", "moreover",
            "on the other hand", "in contrast", "similarly",
            "first", "second", "third", "finally", "lastly",
            "in conclusion", "to summarize", "overall"
        }
        
        # Transitional phrases that often start new thoughts (converted to sets)
        self.transition_phrases: Set[str] = {
            "what i'm experiencing", "what i feel", "what i think",
            "the way i see it", "from my perspective", "in my view",
            "i notice that", "i realize that", "i understand that",
            "i believe that", "i think that", "i feel that"
        }
        
        # Common filler words and repetitions to clean up (converted to sets)
        self.filler_words: Set[str] = {
            "um", "uh", "ah", "er", "like", "you know", "i mean",
            "basically", "actually", "literally", "honestly",
            "so", "and so", "and then", "and also", "and"
        }
        
        # Pre-compiled regex patterns for better performance
        self._whitespace_pattern = re.compile(r'\s+')
        self._punctuation_spacing_pattern = re.compile(r'\s+([,.!?;:])')
        self._punctuation_after_pattern = re.compile(r'([,.!?;:])([a-zA-Z])')
        self._sentence_split_pattern = re.compile(r'[.!?]+')
        
        # Common transcription fixes (pre-compiled for performance)
        self._transcription_fixes = [
            (re.compile(r'\bmolar-type\b', re.IGNORECASE), 'Mooladhara'),
            (re.compile(r'\bmooladhara\b', re.IGNORECASE), 'Mooladhara'),
            (re.compile(r'\b3d\b', re.IGNORECASE), '3D'),
            (re.compile(r'\bout-chose\b', re.IGNORECASE), 'outsourced'),
            (re.compile(r'\bout-chose to\b', re.IGNORECASE), 'outsourced to'),
            (re.compile(r'\btranscendence\b', re.IGNORECASE), 'transcendence'),
            (re.compile(r'\bcosmical\b', re.IGNORECASE), 'cosmic'),
            (re.compile(r'\bcosmic consciousness\b', re.IGNORECASE), 'cosmic consciousness'),
            (re.compile(r'\bkrishna\b', re.IGNORECASE), 'Krishna'),
            (re.compile(r'\barjuna\b', re.IGNORECASE), 'Arjuna'),
            (re.compile(r'\bdetox\b', re.IGNORECASE), 'detox'),
            (re.compile(r'\bkarma\b', re.IGNORECASE), 'karma'),
            (re.compile(r'\bdivine\b', re.IGNORECASE), 'divine'),
            (re.compile(r'\bcellular\b', re.IGNORECASE), 'cellular'),
            (re.compile(r'\btranscend\b', re.IGNORECASE), 'transcend'),
            (re.compile(r'\bliberation\b', re.IGNORECASE), 'liberation'),
            (re.compile(r'\bconsciousness\b', re.IGNORECASE), 'consciousness'),
            (re.compile(r'\bpurify\b', re.IGNORECASE), 'purify'),
            (re.compile(r'\bpurifying\b', re.IGNORECASE), 'purifying'),
            (re.compile(r'\bmanifest\b', re.IGNORECASE), 'manifest'),
            (re.compile(r'\bmanifestation\b', re.IGNORECASE), 'manifestation'),
            (re.compile(r'\bproductivity\b', re.IGNORECASE), 'productivity'),
            (re.compile(r'\bclarity\b', re.IGNORECASE), 'clarity'),
            (re.compile(r'\bguidance\b', re.IGNORECASE), 'guidance'),
            (re.compile(r'\brevelation\b', re.IGNORECASE), 'revelation'),
            (re.compile(r'\battachments\b', re.IGNORECASE), 'attachments'),
            (re.compile(r'\boperating\b', re.IGNORECASE), 'operating')
        ]
        
        logger.info("TextFormatter initialized with optimized patterns")

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize the transcribed text with optimized performance.
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Cleaned and normalized text
        """
        if not text or not text.strip():
            return ""
        
        # Remove extra whitespace using pre-compiled pattern
        text = self._whitespace_pattern.sub(' ', text.strip())
        
        # Fix common transcription errors
        text = self._fix_common_errors(text)
        
        # Remove excessive filler words
        text = self._remove_excessive_fillers(text)
        
        return text

    def _fix_common_errors(self, text: str) -> str:
        """
        Fix common transcription errors using pre-compiled patterns for better performance.
        
        Args:
            text: Text to fix
            
        Returns:
            Text with common errors fixed
        """
        for pattern, replacement in self._transcription_fixes:
            text = pattern.sub(replacement, text)
        
        return text

    def _remove_excessive_fillers(self, text: str) -> str:
        """Remove excessive filler words while preserving natural flow"""
        words = text.split()
        cleaned_words = []
        i = 0
        
        while i < len(words):
            word = words[i].lower().strip('.,!?;:')
            
            # Check if it's a filler word
            if word in self.filler_words:
                # Count consecutive filler words
                filler_count = 0
                j = i
                while j < len(words) and words[j].lower().strip('.,!?;:') in self.filler_words:
                    filler_count += 1
                    j += 1
                
                # Only keep one filler word if there are many
                if filler_count > 2:
                    cleaned_words.append(words[i])
                    i = j
                else:
                    cleaned_words.append(words[i])
                    i += 1
            else:
                cleaned_words.append(words[i])
                i += 1
        
        return ' '.join(cleaned_words)

    def add_punctuation(self, text: str) -> str:
        """Add proper punctuation to the text"""
        # Ensure text ends with punctuation
        if not text.rstrip().endswith(('.', '!', '?')):
            text = text.rstrip() + '.'
        
        # Fix common punctuation issues
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Remove spaces before punctuation
        text = re.sub(r'([,.!?;:])([a-zA-Z])', r'\1 \2', text)  # Add space after punctuation
        text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
        
        return text

    def detect_paragraph_breaks(self, text: str) -> List[Tuple[int, int]]:
        """Detect where paragraph breaks should be inserted"""
        sentences = self._split_into_sentences(text)
        paragraph_breaks = []
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower().strip()
            
            # Check if this sentence should start a new paragraph
            should_break = False
            
            # Check for paragraph starters
            for starter in self.paragraph_starters:
                if sentence_lower.startswith(starter):
                    should_break = True
                    break
            
            # Check for transition phrases
            for phrase in self.transition_phrases:
                if phrase in sentence_lower:
                    should_break = True
                    break
            
            # Check for long pauses (indicated by certain patterns)
            if self._indicates_long_pause(sentence):
                should_break = True
            
            if should_break and i > 0:  # Don't break at the first sentence
                paragraph_breaks.append(i)
        
        return paragraph_breaks

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - can be enhanced with more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _indicates_long_pause(self, sentence: str) -> bool:
        """Check if a sentence indicates a long pause or topic change"""
        # Look for patterns that suggest a pause or topic change
        pause_indicators = [
            r'\b(and|but|so|yet|however|meanwhile|additionally)\b',
            r'\b(what|how|why|when|where)\b.*\b(is|was|are|were)\b',
            r'\b(the|this|that)\b.*\b(thing|problem|issue|matter)\b',
            r'\b(i|we|you|they)\b.*\b(notice|realize|understand|think|feel)\b'
        ]
        
        for pattern in pause_indicators:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True
        
        return False

    def format_text(self, text: str) -> str:
        """Main formatting function that structures the text"""
        # Clean the text
        text = self.clean_text(text)
        
        # Add punctuation
        text = self.add_punctuation(text)
        
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return text
        
        # Detect paragraph breaks
        paragraph_breaks = self.detect_paragraph_breaks(text)
        
        # Build formatted text
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences):
            # Add paragraph break if needed
            if i in paragraph_breaks:
                formatted_sentences.append('')  # Empty line for paragraph break
            
            # Clean up the sentence
            sentence = sentence.strip()
            if sentence:
                # Capitalize first letter
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                formatted_sentences.append(sentence)
        
        # Join sentences with proper spacing
        result = []
        for sentence in formatted_sentences:
            if sentence:  # Non-empty sentence
                result.append(sentence)
            else:  # Empty line for paragraph break
                result.append('')
        
        return '\n'.join(result)

    def format_with_custom_structure(self, text: str, max_sentences_per_paragraph: int = 3) -> str:
        """Format text with custom paragraph structure"""
        text = self.clean_text(text)
        text = self.add_punctuation(text)
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return text
        
        paragraphs = []
        current_paragraph = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                current_paragraph.append(sentence)
            
            # Check if we should start a new paragraph
            should_break = (
                len(current_paragraph) >= max_sentences_per_paragraph or
                i in self.detect_paragraph_breaks(text) or
                i == len(sentences) - 1  # Last sentence
            )
            
            if should_break and current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
        
        return '\n\n'.join(paragraphs)

def format_transcript(text: str, style: str = "auto") -> str:
    """Convenience function to format transcript text"""
    formatter = TextFormatter()
    
    if style == "auto":
        return formatter.format_text(text)
    elif style == "paragraphs":
        return formatter.format_with_custom_structure(text, max_sentences_per_paragraph=3)
    elif style == "minimal":
        return formatter.format_with_custom_structure(text, max_sentences_per_paragraph=5)
    else:
        return formatter.format_text(text)
