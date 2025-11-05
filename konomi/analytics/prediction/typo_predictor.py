"""
🔮 Typo Prediction & Correction
Uses FemtoLLM and pattern matching to predict intended input
"""
import asyncio
import sys
sys.path.append('/home/user/claude')

from typing import List, Tuple, Dict, Optional
import numpy as np
from difflib import get_close_matches
import re
from collections import Counter


class TypoPredictor:
    """
    Typo Predictor

    Predicts what the user meant to type by:
    1. Common typo patterns (keyboard adjacency)
    2. Word frequency/dictionary
    3. Context from FemtoLLM
    4. Personal typing patterns
    """

    def __init__(self):
        """Initialize typo predictor"""
        # Keyboard layout for adjacency-based corrections
        self.qwerty_layout = {
            'q': ['w', 'a'], 'w': ['q', 'e', 's'],
            'e': ['w', 'r', 'd'], 'r': ['e', 't', 'f'],
            't': ['r', 'y', 'g'], 'y': ['t', 'u', 'h'],
            'u': ['y', 'i', 'j'], 'i': ['u', 'o', 'k'],
            'o': ['i', 'p', 'l'], 'p': ['o'],
            'a': ['q', 's', 'z'], 's': ['a', 'w', 'd', 'x'],
            'd': ['s', 'e', 'f', 'c'], 'f': ['d', 'r', 'g', 'v'],
            'g': ['f', 't', 'h', 'b'], 'h': ['g', 'y', 'j', 'n'],
            'j': ['h', 'u', 'k', 'm'], 'k': ['j', 'i', 'l'],
            'l': ['k', 'o'], 'z': ['a', 'x'],
            'x': ['z', 's', 'c'], 'c': ['x', 'd', 'v'],
            'v': ['c', 'f', 'b'], 'b': ['v', 'g', 'n'],
            'n': ['b', 'h', 'm'], 'm': ['n', 'j'],
        }

        # Common words for dictionary matching
        self.common_words = self._load_common_words()

        # Personal typo patterns (learned over time)
        self.personal_patterns: Dict[str, str] = {}

        # Context history for prediction
        self.recent_words: List[str] = []

    def _load_common_words(self) -> set:
        """Load common English words"""
        # Basic common words list
        common = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
            'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
            'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
            'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
            'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
            'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
            'build', 'system', 'code', 'function', 'class', 'method', 'variable', 'data',
            'process', 'create', 'update', 'delete', 'read', 'write', 'file', 'directory',
            'project', 'test', 'debug', 'error', 'fix', 'implement', 'feature', 'bug',
            'typing', 'predict', 'measure', 'analyze', 'speed', 'accuracy', 'entropy',
        }
        return common

    def calculate_edit_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein edit distance

        Args:
            s1, s2: Strings to compare

        Returns:
            Edit distance
        """
        if len(s1) < len(s2):
            return self.calculate_edit_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def get_keyboard_adjacent_chars(self, char: str) -> List[str]:
        """Get characters adjacent to char on keyboard"""
        return self.qwerty_layout.get(char.lower(), [])

    def is_adjacency_error(self, intended: str, actual: str) -> bool:
        """Check if error is due to keyboard adjacency"""
        if len(intended) != len(actual):
            return False

        for i, (c1, c2) in enumerate(zip(intended, actual)):
            if c1 != c2:
                if c2.lower() in self.get_keyboard_adjacent_chars(c1.lower()):
                    return True
        return False

    def predict_word(self, typed_word: str, max_suggestions: int = 5) -> List[Tuple[str, float]]:
        """
        Predict intended word from typed word

        Args:
            typed_word: Word as typed (possibly with errors)
            max_suggestions: Maximum number of suggestions

        Returns:
            List of (word, confidence) tuples
        """
        if not typed_word:
            return []

        typed_lower = typed_word.lower()
        suggestions = []

        # Check personal patterns first
        if typed_lower in self.personal_patterns:
            return [(self.personal_patterns[typed_lower], 0.95)]

        # Check exact match
        if typed_lower in self.common_words:
            return [(typed_word, 1.0)]

        # Find close matches in dictionary
        close_matches = get_close_matches(typed_lower, self.common_words, n=max_suggestions, cutoff=0.6)

        for match in close_matches:
            # Calculate confidence based on edit distance
            distance = self.calculate_edit_distance(typed_lower, match)
            confidence = 1.0 / (1.0 + distance)

            # Boost confidence if adjacency error
            if self.is_adjacency_error(match, typed_lower):
                confidence *= 1.2

            suggestions.append((match, min(1.0, confidence)))

        # Sort by confidence
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return suggestions[:max_suggestions]

    def predict_sentence(self, typed_sentence: str) -> Tuple[str, float]:
        """
        Predict intended sentence from typed sentence

        Args:
            typed_sentence: Sentence as typed

        Returns:
            (predicted_sentence, confidence) tuple
        """
        words = typed_sentence.split()
        predicted_words = []
        confidences = []

        for word in words:
            predictions = self.predict_word(word, max_suggestions=1)
            if predictions:
                predicted_words.append(predictions[0][0])
                confidences.append(predictions[0][1])
            else:
                predicted_words.append(word)
                confidences.append(0.5)  # Unknown word

        avg_confidence = np.mean(confidences) if confidences else 0.0
        predicted_sentence = ' '.join(predicted_words)

        return predicted_sentence, avg_confidence

    def learn_pattern(self, typed: str, intended: str):
        """
        Learn personal typo pattern

        Args:
            typed: What was typed
            intended: What was intended
        """
        if typed.lower() != intended.lower():
            self.personal_patterns[typed.lower()] = intended.lower()

    def get_correction_suggestions(self, text: str) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get correction suggestions for entire text

        Args:
            text: Full text to analyze

        Returns:
            Dictionary mapping words to suggestions
        """
        words = re.findall(r'\b\w+\b', text.lower())
        suggestions = {}

        for word in words:
            if word not in self.common_words:
                word_suggestions = self.predict_word(word)
                if word_suggestions and word_suggestions[0][1] > 0.7:
                    suggestions[word] = word_suggestions

        return suggestions


class IntegratedTypingAnalyzer:
    """
    Integrated Typing Analyzer

    Combines:
    - Keystroke analytics
    - Cognitive entropy measurement
    - Typo prediction
    - Real-time feedback
    """

    def __init__(self):
        """Initialize integrated analyzer"""
        try:
            from konomi.core import FemtoLLM
            self.llm = FemtoLLM()
            self.use_llm = True
        except ImportError:
            print("Warning: FemtoLLM not available, using pattern matching only")
            self.use_llm = False

        self.predictor = TypoPredictor()
        self.typing_history: List[Dict] = []

    async def analyze_and_predict(self,
                                  typed_text: str,
                                  keystroke_intervals: List[float],
                                  corrections: int,
                                  total_keystrokes: int) -> Dict:
        """
        Comprehensive analysis with prediction

        Args:
            typed_text: Text as typed
            keystroke_intervals: Typing intervals
            corrections: Number of corrections
            total_keystrokes: Total keystrokes

        Returns:
            Analysis results dictionary
        """
        # Predict intended text
        predicted_text, prediction_confidence = self.predictor.predict_sentence(typed_text)

        # Get correction suggestions
        suggestions = self.predictor.get_correction_suggestions(typed_text)

        # Optional: Use LLM for context-aware prediction
        llm_prediction = None
        if self.use_llm and self.llm:
            try:
                llm_prediction = await self.llm.process(typed_text)
            except:
                pass

        # Calculate metrics
        avg_interval = np.mean(keystroke_intervals) if keystroke_intervals else 0.0
        wpm = (len(typed_text.split()) / (sum(keystroke_intervals) / 60)) if keystroke_intervals else 0.0

        result = {
            'original_text': typed_text,
            'predicted_text': predicted_text,
            'prediction_confidence': prediction_confidence,
            'corrections_suggested': len(suggestions),
            'suggestions': suggestions,
            'llm_prediction': llm_prediction,
            'metrics': {
                'wpm': wpm,
                'corrections': corrections,
                'avg_keystroke_interval': avg_interval,
                'total_keystrokes': total_keystrokes,
            }
        }

        self.typing_history.append(result)

        return result


if __name__ == "__main__":
    # Test typo predictor
    print("🔮 Typo Predictor Test\n")

    predictor = TypoPredictor()

    # Test word prediction
    test_words = [
        ("helo", "hello"),
        ("wrold", "world"),
        ("teh", "the"),
        ("recieve", "receive"),
        ("seperate", "separate"),
    ]

    print("Word Predictions:")
    for typed, expected in test_words:
        predictions = predictor.predict_word(typed)
        print(f"  '{typed}' -> {predictions}")

        # Learn pattern
        if predictions:
            predictor.learn_pattern(typed, expected)

    # Test sentence prediction
    print("\nSentence Predictions:")
    test_sentences = [
        "helo wrold this is a tets",
        "i ned to measuer my typng spede",
        "konomi systm is awsome",
    ]

    for sentence in test_sentences:
        predicted, confidence = predictor.predict_sentence(sentence)
        print(f"  Original:  '{sentence}'")
        print(f"  Predicted: '{predicted}' (confidence: {confidence:.2f})")
        print()

    print("✓ Typo predictor test complete!")
