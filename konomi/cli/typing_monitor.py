#!/usr/bin/env python3
"""
⌨️ KONOMI Typing Monitor
Real-time typing analytics with cognitive entropy measurement
"""
import asyncio
import sys
import time
from typing import Optional
sys.path.append('/home/user/claude')

from konomi.analytics import (
    TypingAnalytics,
    CognitiveEntropyAnalyzer,
    TypoPredictor,
)


class TypingMonitor:
    """
    Interactive Typing Monitor

    Measures:
    - Typing speed (WPM)
    - Accuracy
    - Cognitive entropy
    - Stress/fatigue/flow states
    - Typo patterns and predictions
    """

    def __init__(self):
        """Initialize typing monitor"""
        self.typing_analytics = TypingAnalytics()
        self.cognitive_analyzer = CognitiveEntropyAnalyzer()
        self.typo_predictor = TypoPredictor()

        self.session_id = f"session_{int(time.time())}"

    def print_header(self):
        """Print monitor header"""
        print("\n" + "=" * 70)
        print("⌨️  KONOMI TYPING MONITOR")
        print("=" * 70)
        print("Measures: Mind Speed vs Typing Speed | Cognitive Entropy | Flow State")
        print("=" * 70 + "\n")

    def print_instructions(self):
        """Print usage instructions"""
        print("Instructions:")
        print("  1. Type naturally - the system will analyze your patterns")
        print("  2. Type 'exit' or 'quit' to end and see full analysis")
        print("  3. The system learns your typo patterns as you type")
        print()

    async def analyze_input(self, text: str) -> dict:
        """
        Analyze typed input

        Args:
            text: Input text

        Returns:
            Analysis results
        """
        # Record keystrokes (simulated timing based on text length)
        intervals = []
        for char in text:
            event = self.typing_analytics.record_keystroke(char)
            intervals.append(event.interval if event.interval > 0 else 0.15)

        # Get typing stats
        typing_stats = self.typing_analytics.get_session_stats()

        # Analyze cognitive state
        session = self.typing_analytics.current_session
        session_duration = time.time() - session.start_time if session else 0.0

        cognitive_state = self.cognitive_analyzer.analyze_state(
            keystroke_intervals=intervals,
            corrections=session.corrections if session else 0,
            total_keystrokes=session.total_chars if session else 0,
            session_duration=session_duration
        )

        # Predict intended text
        predicted_text, prediction_confidence = self.typo_predictor.predict_sentence(text)

        # Get correction suggestions
        suggestions = self.typo_predictor.get_correction_suggestions(text)

        return {
            'original': text,
            'predicted': predicted_text,
            'confidence': prediction_confidence,
            'suggestions': suggestions,
            'typing_stats': typing_stats,
            'cognitive_state': cognitive_state,
        }

    def print_realtime_feedback(self, analysis: dict):
        """
        Print real-time feedback

        Args:
            analysis: Analysis results
        """
        stats = analysis['typing_stats']
        state = analysis['cognitive_state']

        # Create status bar
        print()
        print("─" * 70)

        # Typing metrics
        print(f"⚡ Speed: {stats['wpm']:.1f} WPM | "
              f"📊 Accuracy: {stats['accuracy']:.1f}% | "
              f"⏱️  Rhythm: {stats['rhythm_consistency']:.2f}")

        # Cognitive state (with emojis for visual feedback)
        flow_emoji = "🌊" if state.flow_state > 0.7 else "🔄" if state.flow_state > 0.4 else "⚠️"
        stress_emoji = "😌" if state.stress_level < 0.3 else "😐" if state.stress_level < 0.7 else "😰"
        fatigue_emoji = "⚡" if state.fatigue_level < 0.3 else "😐" if state.fatigue_level < 0.7 else "😴"

        print(f"{flow_emoji} Flow: {state.flow_state:.2f} | "
              f"{stress_emoji} Stress: {state.stress_level:.2f} | "
              f"{fatigue_emoji} Fatigue: {state.fatigue_level:.2f}")

        # Entropy and cognitive load
        print(f"🧠 Cognitive Load: {state.cognitive_load:.2f} | "
              f"🌀 Entropy: {state.entropy:.2f}")

        # State interpretation
        interpretation = self.cognitive_analyzer.get_state_interpretation(state)
        print(f"💭 {interpretation}")

        # Predictions and suggestions
        if analysis['predicted'] != analysis['original']:
            print(f"🔮 Did you mean: '{analysis['predicted']}'? "
                  f"(confidence: {analysis['confidence']:.0%})")

        if analysis['suggestions']:
            print(f"✏️  Corrections available for: {', '.join(analysis['suggestions'].keys())}")

        print("─" * 70)

    def print_final_analysis(self):
        """Print comprehensive final analysis"""
        print("\n" + "=" * 70)
        print("📊 FINAL ANALYSIS")
        print("=" * 70 + "\n")

        # Overall typing stats
        stats = self.typing_analytics.get_session_stats()
        print("Typing Performance:")
        print(f"  Total keystrokes: {stats['total_keystrokes']}")
        print(f"  Duration: {stats['duration_seconds']:.1f}s")
        print(f"  Average WPM: {stats['wpm']:.1f}")
        print(f"  Accuracy: {stats['accuracy']:.1f}%")
        print(f"  Corrections made: {stats['corrections']}")
        print()

        # Cognitive state over time
        if len(self.cognitive_analyzer.state_history) > 0:
            states = self.cognitive_analyzer.state_history

            avg_flow = sum(s.flow_state for s in states) / len(states)
            avg_stress = sum(s.stress_level for s in states) / len(states)
            avg_fatigue = sum(s.fatigue_level for s in states) / len(states)
            avg_load = sum(s.cognitive_load for s in states) / len(states)
            avg_entropy = sum(s.entropy for s in states) / len(states)

            print("Cognitive Patterns:")
            print(f"  Average Flow State: {avg_flow:.2f} {'🌊 Excellent!' if avg_flow > 0.7 else '✨ Good' if avg_flow > 0.5 else '⚠️  Needs focus'}")
            print(f"  Average Stress: {avg_stress:.2f} {'😌 Calm' if avg_stress < 0.3 else '😐 Moderate' if avg_stress < 0.7 else '😰 High'}")
            print(f"  Average Fatigue: {avg_fatigue:.2f} {'⚡ Fresh' if avg_fatigue < 0.3 else '😐 Moderate' if avg_fatigue < 0.7 else '😴 Tired'}")
            print(f"  Average Cognitive Load: {avg_load:.2f}")
            print(f"  Average Entropy: {avg_entropy:.2f}")
            print()

        # Learned patterns
        if self.typo_predictor.personal_patterns:
            print("Learned Typo Patterns:")
            for typed, corrected in list(self.typo_predictor.personal_patterns.items())[:10]:
                print(f"  '{typed}' → '{corrected}'")
            print()

        # Mind speed vs typing speed analysis
        rhythm = self.typing_analytics.get_typing_rhythm()
        print("Mind Speed vs Typing Speed:")
        print(f"  Characters/second: {rhythm['chars_per_second']:.2f}")
        print(f"  Rhythm consistency: {rhythm['rhythm_consistency']:.2f}")

        if stats['accuracy'] < 85:
            print(f"  💭 Your mind is faster than your fingers! ({stats['accuracy']:.0f}% accuracy)")
            print(f"     Suggestion: Slow down slightly for better accuracy")
        elif rhythm['rhythm_consistency'] > 0.8:
            print(f"  ✨ Excellent synchronization! Mind and typing speed are balanced")
        else:
            print(f"  🎯 Good balance between speed and accuracy")

        print()
        print("=" * 70)

    async def run_interactive(self):
        """Run interactive typing monitor"""
        self.print_header()
        self.print_instructions()

        self.typing_analytics.start_session(self.session_id)
        print("🟢 Monitoring started. Begin typing...\n")

        while True:
            try:
                # Get input (in real system, this would capture keystrokes in real-time)
                user_input = input("Type here: ")

                if user_input.lower() in ['exit', 'quit', 'q']:
                    break

                if not user_input.strip():
                    continue

                # Analyze input
                analysis = await self.analyze_input(user_input)

                # Show real-time feedback
                self.print_realtime_feedback(analysis)

                # Learn from corrections
                if analysis['predicted'] != analysis['original']:
                    # Ask if prediction was correct
                    # (In production, this could be automatic or user-confirmed)
                    pass

            except KeyboardInterrupt:
                print("\n\n⏹️  Interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()

        # Show final analysis
        self.print_final_analysis()
        print("\n✅ Session ended. Thank you!\n")

    async def run_demo(self):
        """Run demo with sample data"""
        self.print_header()
        print("🎬 DEMO MODE - Simulating typing patterns\n")

        self.typing_analytics.start_session(self.session_id)

        # Simulate different typing patterns
        test_inputs = [
            ("Hello world", "Normal typing"),
            ("helo wrold", "With typos"),
            ("i ned to measuer my typng spede", "Multiple typos - mind faster than fingers"),
            ("konomi system is amazing", "More complex sentence"),
            ("this is a vrey logn sentence with some errros in it", "Fatigue pattern"),
        ]

        for text, description in test_inputs:
            print(f"\n📝 {description}: '{text}'")
            time.sleep(0.5)

            analysis = await self.analyze_input(text)
            self.print_realtime_feedback(analysis)

            time.sleep(1)

        # Show final analysis
        self.print_final_analysis()


async def main():
    """Main entry point"""
    monitor = TypingMonitor()

    # Check if in demo mode
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        await monitor.run_demo()
    else:
        await monitor.run_interactive()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋\n")
