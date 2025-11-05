"""
🧠 Cognitive Entropy Measurement
Measures cognitive load, stress, fatigue from typing patterns
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time
from collections import deque


@dataclass
class CognitiveState:
    """Snapshot of cognitive state"""
    timestamp: float
    entropy: float  # Shannon entropy of keystroke intervals
    cognitive_load: float  # 0-1 scale
    stress_level: float  # 0-1 scale
    fatigue_level: float  # 0-1 scale
    flow_state: float  # 0-1 scale (1 = high flow)
    confidence: float  # Prediction confidence


class CognitiveEntropyAnalyzer:
    """
    Cognitive Entropy Analyzer

    Analyzes typing patterns to infer cognitive state:
    - Entropy: Randomness in typing rhythm
    - Cognitive load: Mental effort required
    - Stress: Anxiety/pressure indicators
    - Fatigue: Tiredness indicators
    - Flow: Deep focus state
    """

    def __init__(self, window_size: int = 50):
        """
        Initialize cognitive analyzer

        Args:
            window_size: Number of keystrokes to analyze
        """
        self.window_size = window_size
        self.keystroke_intervals = deque(maxlen=window_size)
        self.error_rates = deque(maxlen=window_size)
        self.pause_durations = deque(maxlen=window_size)

        # Historical states
        self.state_history: List[CognitiveState] = []

        # Baseline measurements (adaptive)
        self.baseline_interval = 0.15  # 150ms baseline
        self.baseline_entropy = 1.0

    def calculate_shannon_entropy(self, intervals: np.ndarray) -> float:
        """
        Calculate Shannon entropy of keystroke intervals

        High entropy = irregular/random typing
        Low entropy = consistent/rhythmic typing

        Args:
            intervals: Array of keystroke intervals

        Returns:
            Entropy value
        """
        if len(intervals) < 2:
            return 0.0

        # Discretize intervals into bins
        bins = 10
        hist, _ = np.histogram(intervals, bins=bins)
        hist = hist[hist > 0]  # Remove empty bins

        # Normalize to probabilities
        probs = hist / hist.sum()

        # Calculate Shannon entropy: H = -Σ(p * log2(p))
        entropy = -np.sum(probs * np.log2(probs))

        return float(entropy)

    def calculate_cognitive_load(self,
                                 intervals: np.ndarray,
                                 error_rate: float,
                                 pauses: np.ndarray) -> float:
        """
        Calculate cognitive load indicator

        High load indicators:
        - Longer intervals (thinking time)
        - More errors
        - Frequent pauses
        - High variance

        Args:
            intervals: Keystroke intervals
            error_rate: Error/correction rate
            pauses: Long pause durations

        Returns:
            Cognitive load (0-1)
        """
        if len(intervals) < 2:
            return 0.0

        # Factor 1: Mean interval vs baseline
        mean_interval = np.mean(intervals)
        interval_factor = min(1.0, mean_interval / (self.baseline_interval * 2))

        # Factor 2: Error rate
        error_factor = min(1.0, error_rate)

        # Factor 3: Pause frequency and duration
        pause_factor = 0.0
        if len(pauses) > 0:
            mean_pause = np.mean(pauses)
            pause_factor = min(1.0, mean_pause / 2.0)  # 2s pause = max factor

        # Factor 4: Variance (inconsistency)
        variance_factor = min(1.0, np.std(intervals) / mean_interval) if mean_interval > 0 else 0.0

        # Weighted combination
        cognitive_load = (
            0.3 * interval_factor +
            0.3 * error_factor +
            0.2 * pause_factor +
            0.2 * variance_factor
        )

        return float(np.clip(cognitive_load, 0.0, 1.0))

    def calculate_stress_level(self,
                               intervals: np.ndarray,
                               error_rate: float) -> float:
        """
        Calculate stress level indicator

        High stress indicators:
        - Very fast typing (rushing)
        - Burst patterns (uneven)
        - High error rate
        - Low rhythm consistency

        Args:
            intervals: Keystroke intervals
            error_rate: Error/correction rate

        Returns:
            Stress level (0-1)
        """
        if len(intervals) < 2:
            return 0.0

        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        # Factor 1: Very fast typing (< 50ms avg)
        speed_stress = 1.0 - min(1.0, mean_interval / 0.05) if mean_interval < 0.1 else 0.0

        # Factor 2: High variance (inconsistency)
        cv = std_interval / mean_interval if mean_interval > 0 else 0.0
        variance_stress = min(1.0, cv)

        # Factor 3: Error rate
        error_stress = error_rate

        # Factor 4: Burst detection (rapid then slow)
        burst_stress = 0.0
        if len(intervals) > 5:
            # Look for rapid changes in pace
            interval_diff = np.diff(intervals)
            burst_stress = min(1.0, np.std(interval_diff) / mean_interval) if mean_interval > 0 else 0.0

        # Weighted combination
        stress = (
            0.2 * speed_stress +
            0.3 * variance_stress +
            0.3 * error_stress +
            0.2 * burst_stress
        )

        return float(np.clip(stress, 0.0, 1.0))

    def calculate_fatigue_level(self,
                                intervals: np.ndarray,
                                session_duration: float) -> float:
        """
        Calculate fatigue level indicator

        High fatigue indicators:
        - Gradually slowing down
        - Longer pauses over time
        - Decreased accuracy over time

        Args:
            intervals: Keystroke intervals
            session_duration: Time since session start (seconds)

        Returns:
            Fatigue level (0-1)
        """
        if len(intervals) < 10:
            return 0.0

        # Factor 1: Trend in intervals (slowing down)
        # Linear regression slope
        x = np.arange(len(intervals))
        slope = np.polyfit(x, intervals, 1)[0]

        # Positive slope = slowing down
        trend_fatigue = min(1.0, max(0.0, slope * 100)) if slope > 0 else 0.0

        # Factor 2: Session duration (longer = more fatigue)
        duration_fatigue = min(1.0, session_duration / 3600)  # Max at 1 hour

        # Factor 3: Recent intervals vs early intervals
        if len(intervals) > 20:
            early = np.mean(intervals[:10])
            recent = np.mean(intervals[-10:])
            slowdown_fatigue = min(1.0, (recent - early) / early) if early > 0 and recent > early else 0.0
        else:
            slowdown_fatigue = 0.0

        # Weighted combination
        fatigue = (
            0.4 * trend_fatigue +
            0.3 * duration_fatigue +
            0.3 * slowdown_fatigue
        )

        return float(np.clip(fatigue, 0.0, 1.0))

    def calculate_flow_state(self,
                            intervals: np.ndarray,
                            error_rate: float) -> float:
        """
        Calculate flow state indicator

        High flow indicators:
        - Consistent rhythm (low variance)
        - Optimal speed (not too fast/slow)
        - Low error rate
        - Sustained performance

        Args:
            intervals: Keystroke intervals
            error_rate: Error/correction rate

        Returns:
            Flow state (0-1, 1 = high flow)
        """
        if len(intervals) < 10:
            return 0.0

        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        cv = std_interval / mean_interval if mean_interval > 0 else 1.0

        # Factor 1: Rhythm consistency (low CV = high consistency)
        consistency_flow = 1.0 - min(1.0, cv)

        # Factor 2: Optimal speed (100-200ms is "flow zone")
        speed_optimal = 1.0 - abs(mean_interval - 0.15) / 0.15
        speed_flow = max(0.0, min(1.0, speed_optimal))

        # Factor 3: Low error rate
        accuracy_flow = 1.0 - error_rate

        # Factor 4: Stability over time (minimal drift)
        if len(intervals) > 20:
            early_mean = np.mean(intervals[:10])
            recent_mean = np.mean(intervals[-10:])
            drift = abs(recent_mean - early_mean) / early_mean if early_mean > 0 else 0.0
            stability_flow = 1.0 - min(1.0, drift)
        else:
            stability_flow = consistency_flow

        # Weighted combination
        flow = (
            0.35 * consistency_flow +
            0.25 * speed_flow +
            0.25 * accuracy_flow +
            0.15 * stability_flow
        )

        return float(np.clip(flow, 0.0, 1.0))

    def analyze_state(self,
                     keystroke_intervals: List[float],
                     corrections: int,
                     total_keystrokes: int,
                     session_duration: float) -> CognitiveState:
        """
        Analyze current cognitive state from typing data

        Args:
            keystroke_intervals: List of recent keystroke intervals
            corrections: Number of corrections made
            total_keystrokes: Total keystrokes
            session_duration: Session duration in seconds

        Returns:
            CognitiveState object
        """
        if not keystroke_intervals or len(keystroke_intervals) < 2:
            return CognitiveState(
                timestamp=time.time(),
                entropy=0.0,
                cognitive_load=0.0,
                stress_level=0.0,
                fatigue_level=0.0,
                flow_state=0.0,
                confidence=0.0
            )

        intervals = np.array(keystroke_intervals)
        intervals = intervals[intervals > 0]  # Remove zero intervals

        if len(intervals) < 2:
            return CognitiveState(
                timestamp=time.time(),
                entropy=0.0,
                cognitive_load=0.0,
                stress_level=0.0,
                fatigue_level=0.0,
                flow_state=0.0,
                confidence=0.0
            )

        # Calculate error rate
        error_rate = corrections / total_keystrokes if total_keystrokes > 0 else 0.0

        # Find pauses (intervals > 1 second)
        pauses = intervals[intervals > 1.0]

        # Calculate all metrics
        entropy = self.calculate_shannon_entropy(intervals)
        cognitive_load = self.calculate_cognitive_load(intervals, error_rate, pauses)
        stress_level = self.calculate_stress_level(intervals, error_rate)
        fatigue_level = self.calculate_fatigue_level(intervals, session_duration)
        flow_state = self.calculate_flow_state(intervals, error_rate)

        # Confidence based on sample size
        confidence = min(1.0, len(intervals) / self.window_size)

        state = CognitiveState(
            timestamp=time.time(),
            entropy=entropy,
            cognitive_load=cognitive_load,
            stress_level=stress_level,
            fatigue_level=fatigue_level,
            flow_state=flow_state,
            confidence=confidence
        )

        self.state_history.append(state)

        return state

    def get_state_interpretation(self, state: CognitiveState) -> str:
        """
        Get human-readable interpretation of cognitive state

        Args:
            state: CognitiveState to interpret

        Returns:
            Interpretation string
        """
        interpretations = []

        # Entropy
        if state.entropy > 2.5:
            interpretations.append("🌊 High variability - mind wandering or multitasking")
        elif state.entropy < 1.0:
            interpretations.append("🎯 Very consistent - deep focus or automation")

        # Cognitive load
        if state.cognitive_load > 0.7:
            interpretations.append("🧠 High cognitive load - complex thinking required")
        elif state.cognitive_load < 0.3:
            interpretations.append("✨ Low cognitive load - easy/familiar task")

        # Stress
        if state.stress_level > 0.7:
            interpretations.append("⚡ High stress - rushing or anxious")
        elif state.stress_level < 0.3:
            interpretations.append("😌 Low stress - calm and relaxed")

        # Fatigue
        if state.fatigue_level > 0.7:
            interpretations.append("😴 High fatigue - consider taking a break")
        elif state.fatigue_level < 0.3:
            interpretations.append("⚡ Fresh and energized")

        # Flow
        if state.flow_state > 0.7:
            interpretations.append("🌊 In flow state - optimal performance zone")
        elif state.flow_state < 0.3:
            interpretations.append("🔄 Struggling to find rhythm")

        return " | ".join(interpretations) if interpretations else "📊 Neutral state"


if __name__ == "__main__":
    # Test cognitive entropy analyzer
    print("🧠 Cognitive Entropy Analyzer Test\n")

    analyzer = CognitiveEntropyAnalyzer()

    # Simulate different typing patterns

    # Pattern 1: Consistent (flow state)
    print("Pattern 1: Consistent typing (flow)")
    intervals_flow = np.random.normal(0.15, 0.02, 50).tolist()
    state = analyzer.analyze_state(intervals_flow, 2, 50, 30.0)
    print(f"  Entropy: {state.entropy:.3f}")
    print(f"  Cognitive Load: {state.cognitive_load:.3f}")
    print(f"  Stress: {state.stress_level:.3f}")
    print(f"  Fatigue: {state.fatigue_level:.3f}")
    print(f"  Flow: {state.flow_state:.3f}")
    print(f"  Interpretation: {analyzer.get_state_interpretation(state)}\n")

    # Pattern 2: Stressed (fast, erratic)
    print("Pattern 2: Stressed typing")
    intervals_stress = np.random.exponential(0.08, 50).tolist()
    state = analyzer.analyze_state(intervals_stress, 15, 50, 30.0)
    print(f"  Entropy: {state.entropy:.3f}")
    print(f"  Stress: {state.stress_level:.3f}")
    print(f"  Interpretation: {analyzer.get_state_interpretation(state)}\n")

    # Pattern 3: Fatigued (slowing down)
    print("Pattern 3: Fatigued typing")
    intervals_fatigue = [0.1 + i * 0.01 for i in range(50)]
    state = analyzer.analyze_state(intervals_fatigue, 5, 50, 1800.0)
    print(f"  Fatigue: {state.fatigue_level:.3f}")
    print(f"  Interpretation: {analyzer.get_state_interpretation(state)}\n")

    print("✓ Cognitive entropy analyzer test complete!")
