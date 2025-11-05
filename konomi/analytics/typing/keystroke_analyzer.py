"""
⌨️ Typing Analytics Module
Measures typing patterns, predicts intended input, calculates cognitive entropy
"""
import time
import asyncio
from typing import List, Dict, Tuple, Optional
from collections import deque
from dataclasses import dataclass, field
import numpy as np
from difflib import SequenceMatcher
import re


@dataclass
class KeystrokeEvent:
    """Single keystroke event"""
    timestamp: float
    char: str
    is_backspace: bool = False
    is_correction: bool = False
    interval: float = 0.0  # Time since last keystroke


@dataclass
class TypingSession:
    """Complete typing session data"""
    session_id: str
    start_time: float
    keystrokes: List[KeystrokeEvent] = field(default_factory=list)
    corrections: int = 0
    total_chars: int = 0
    raw_text: str = ""
    final_text: str = ""


class TypingAnalytics:
    """
    Typing Analytics Engine

    Tracks:
    - Keystroke timing and patterns
    - Error rates and correction behavior
    - Typing speed (WPM, chars/sec)
    - Cognitive load indicators
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize typing analytics

        Args:
            window_size: Number of recent keystrokes to analyze
        """
        self.window_size = window_size
        self.sessions: Dict[str, TypingSession] = {}
        self.current_session: Optional[TypingSession] = None

        # Rolling statistics
        self.keystroke_intervals = deque(maxlen=window_size)
        self.error_positions = deque(maxlen=window_size)

        # Common typo patterns
        self.typo_patterns: Dict[str, str] = {}

    def start_session(self, session_id: str) -> TypingSession:
        """Start new typing session"""
        session = TypingSession(
            session_id=session_id,
            start_time=time.time()
        )
        self.sessions[session_id] = session
        self.current_session = session
        return session

    def record_keystroke(self, char: str, is_backspace: bool = False) -> KeystrokeEvent:
        """
        Record single keystroke

        Args:
            char: Character typed
            is_backspace: Whether this is a backspace/correction

        Returns:
            KeystrokeEvent
        """
        if not self.current_session:
            self.start_session(f"session_{int(time.time())}")

        session = self.current_session
        current_time = time.time()

        # Calculate interval from last keystroke
        interval = 0.0
        if session.keystrokes:
            interval = current_time - session.keystrokes[-1].timestamp

        event = KeystrokeEvent(
            timestamp=current_time,
            char=char,
            is_backspace=is_backspace,
            is_correction=is_backspace,
            interval=interval
        )

        session.keystrokes.append(event)
        self.keystroke_intervals.append(interval)

        if is_backspace:
            session.corrections += 1
        else:
            session.total_chars += 1
            session.raw_text += char

        return event

    def record_text_input(self, text: str) -> List[KeystrokeEvent]:
        """
        Record complete text input with simulated timing

        Args:
            text: Input text

        Returns:
            List of keystroke events
        """
        events = []
        for char in text:
            event = self.record_keystroke(char)
            events.append(event)
        return events

    def calculate_wpm(self, session_id: Optional[str] = None) -> float:
        """
        Calculate words per minute

        Args:
            session_id: Session to analyze (current if None)

        Returns:
            Words per minute
        """
        session = self.sessions.get(session_id) if session_id else self.current_session
        if not session or not session.keystrokes:
            return 0.0

        duration = time.time() - session.start_time
        if duration < 0.1:
            return 0.0

        # Standard: 5 chars = 1 word
        words = session.total_chars / 5
        minutes = duration / 60

        return words / minutes if minutes > 0 else 0.0

    def calculate_accuracy(self, session_id: Optional[str] = None) -> float:
        """
        Calculate typing accuracy

        Args:
            session_id: Session to analyze (current if None)

        Returns:
            Accuracy percentage (0-100)
        """
        session = self.sessions.get(session_id) if session_id else self.current_session
        if not session or session.total_chars == 0:
            return 100.0

        # Accuracy = (total - corrections) / total
        accuracy = ((session.total_chars - session.corrections) / session.total_chars) * 100
        return max(0.0, min(100.0, accuracy))

    def get_typing_rhythm(self) -> Dict[str, float]:
        """
        Analyze typing rhythm from keystroke intervals

        Returns:
            Dictionary with rhythm metrics
        """
        if len(self.keystroke_intervals) < 2:
            return {
                "mean_interval": 0.0,
                "std_interval": 0.0,
                "rhythm_consistency": 0.0
            }

        intervals = np.array(list(self.keystroke_intervals))
        intervals = intervals[intervals > 0]  # Remove zero intervals

        if len(intervals) == 0:
            return {
                "mean_interval": 0.0,
                "std_interval": 0.0,
                "rhythm_consistency": 0.0
            }

        mean_interval = float(np.mean(intervals))
        std_interval = float(np.std(intervals))

        # Rhythm consistency: lower std = more consistent
        rhythm_consistency = 1.0 / (1.0 + std_interval) if std_interval > 0 else 1.0

        return {
            "mean_interval": mean_interval,
            "std_interval": std_interval,
            "rhythm_consistency": rhythm_consistency,
            "chars_per_second": 1.0 / mean_interval if mean_interval > 0 else 0.0
        }

    def detect_typo_patterns(self, intended: str, actual: str) -> List[Tuple[str, str]]:
        """
        Detect typo patterns by comparing intended vs actual text

        Args:
            intended: What was meant to be typed
            actual: What was actually typed

        Returns:
            List of (wrong, correct) tuples
        """
        patterns = []

        # Use sequence matcher to find differences
        matcher = SequenceMatcher(None, actual, intended)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                wrong = actual[i1:i2]
                correct = intended[j1:j2]
                patterns.append((wrong, correct))

                # Store in typo patterns
                self.typo_patterns[wrong] = correct

        return patterns

    def get_session_stats(self, session_id: Optional[str] = None) -> Dict:
        """
        Get comprehensive session statistics

        Args:
            session_id: Session to analyze (current if None)

        Returns:
            Dictionary with all statistics
        """
        session = self.sessions.get(session_id) if session_id else self.current_session
        if not session:
            return {}

        duration = time.time() - session.start_time
        rhythm = self.get_typing_rhythm()

        return {
            "session_id": session.session_id,
            "duration_seconds": duration,
            "total_keystrokes": len(session.keystrokes),
            "total_chars": session.total_chars,
            "corrections": session.corrections,
            "wpm": self.calculate_wpm(session_id),
            "accuracy": self.calculate_accuracy(session_id),
            "chars_per_second": rhythm['chars_per_second'],
            "rhythm_consistency": rhythm['rhythm_consistency'],
            "mean_keystroke_interval": rhythm['mean_interval'],
            "std_keystroke_interval": rhythm['std_interval'],
        }


if __name__ == "__main__":
    # Test typing analytics
    print("⌨️ Typing Analytics Test\n")

    analytics = TypingAnalytics()

    # Simulate typing with errors
    analytics.start_session("test1")

    # Type "hello world" with some errors
    text = "helo wrold"  # Intentional typos
    for char in text:
        analytics.record_keystroke(char)
        time.sleep(0.1)  # Simulate typing delay

    # Corrections
    for _ in range(2):
        analytics.record_keystroke('', is_backspace=True)

    analytics.record_keystroke('l')
    analytics.record_keystroke('d')

    # Get stats
    stats = analytics.get_session_stats()
    print("Session Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Detect patterns
    patterns = analytics.detect_typo_patterns("hello world", "helo wrold")
    print(f"\nTypo patterns detected: {patterns}")

    print("\n✓ Typing analytics test complete!")
