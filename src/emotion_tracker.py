"""
Emotion Tracker for DreamTalk Emotion Engine.

Provides sentiment analysis (VADER) and an EMA-based affective state tracker
with 12 discrete mood states and three intensity levels.
"""

import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class EmotionAnalyzer:
    """
    Affective Analysis Unit.
    Uses VADER to analyze the emotional tone of the user's text.
    """
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        logging.debug("EmotionAnalyzer initialized with VADER.")

    def analyze_text(self, text: str) -> float:
        """
        Returns a compound sentiment score from -1.0 to +1.0.
        """
        scores = self.analyzer.polarity_scores(text)
        return scores['compound']


class AffectiveStateTracker:
    """
    Maintains the avatar's internal emotional state using an Exponential
    Moving Average.  Produces a rich emotion-state dict:
        {mood, intensity, valence, is_hostile}
    """

    HOSTILE_WORDS = {
        # word -> weight  (higher = more hostile)
        "hate": 1.0, "slap": 1.0, "fuck": 1.2, "bitch": 1.2,
        "shit": 1.0, "shut up": 0.9, "idiot": 0.9, "dumb": 0.8,
        "stupid": 0.8, "annoying": 0.7, "angry": 0.6, "kill": 1.2,
        "die": 1.1, "bad": 0.4, "worst": 0.8, "useless": 0.9,
        "trash": 0.9, "pathetic": 1.0, "garbage": 0.9, "suck": 0.8,
        "terrible": 0.7, "awful": 0.7, "disgusting": 0.9,
    }

    def __init__(self, initial_mood: str = "calm", alpha: float = 0.35):
        self.current_mood = initial_mood
        self.current_valence = 0.0          # continuous, -1 … +1
        self.current_intensity = "low"      # low / medium / high
        self.alpha = alpha
        self._hostility_score = 0.0         # accumulated hostility

    # ------------------------------------------------------------------
    def _compute_hostility(self, text: str) -> float:
        """Weighted hostility score for the message (0 = none, >1 = very hostile)."""
        text_lower = text.lower()
        score = sum(w for kw, w in self.HOSTILE_WORDS.items() if kw in text_lower)
        return score

    def _intensity_from_valence(self, valence: float) -> str:
        mag = abs(valence)
        if mag >= 0.45:
            return "high"
        elif mag >= 0.15:
            return "medium"
        return "low"

    # ------------------------------------------------------------------
    def update_state(self, user_text: str, user_sentiment: float) -> dict:
        """
        Update internal state.  Returns a rich dict:
            {mood, intensity, valence, is_hostile}
        """
        # 1. EMA on valence
        self.current_valence = (
            self.alpha * user_sentiment
            + (1 - self.alpha) * self.current_valence
        )

        # 2. Hostility tracking (decays slightly each turn)
        msg_hostility = self._compute_hostility(user_text)
        self._hostility_score = max(0, self._hostility_score * 0.6 + msg_hostility)
        is_hostile = self._hostility_score >= 0.5

        # 3. Intensity
        self.current_intensity = self._intensity_from_valence(self.current_valence)

        # 4. Mood mapping
        self.current_mood = self._map_mood(self.current_valence, is_hostile,
                                           self._hostility_score)
        return {
            "mood": self.current_mood,
            "intensity": self.current_intensity,
            "valence": self.current_valence,
            "is_hostile": is_hostile,
        }

    # ------------------------------------------------------------------
    def _map_mood(self, valence: float, is_hostile: bool,
                  hostility_score: float) -> str:
        """
        12-state mood mapping that distinguishes hostile negativity from
        genuine sadness, and adds sarcasm / playfulness.
        """
        # ── Hostile track ──────────────────────────────────────────────
        if is_hostile:
            if valence < -0.4:
                return "furious"
            if valence < -0.15:
                return "defensive"
            if valence < -0.05:
                return "annoyed"
            # could be hostile words with neutral sentiment → sarcasm
            if hostility_score >= 1.0:
                return "sarcastic"
            return "annoyed"

        # ── Positive track ─────────────────────────────────────────────
        if valence >= 0.5:
            return "excited"
        if valence >= 0.25:
            return "joyful"
        if valence >= 0.1:
            return "playful"

        # ── Neutral band ───────────────────────────────────────────────
        if valence > -0.1:
            return "calm"

        # ── Negative (non-hostile) track ───────────────────────────────
        if valence > -0.25:
            return "concerned"
        if valence > -0.45:
            return "sympathetic"
        return "empathetic"

    # ------------------------------------------------------------------
    def get_current_mood(self) -> str:
        return self.current_mood


# -----------------------------------------------------------------------
# Quick standalone test
# -----------------------------------------------------------------------
if __name__ == "__main__":
    analyzer = EmotionAnalyzer()
    tracker = AffectiveStateTracker()

    print("--- Emotion Tracker Test ---")
    test_inputs = [
        "Hello, it's nice to meet you.",
        "I had a really terrible day today, everything went wrong.",
        "That's so frustrating!",
        "you are just a shit ai",
        "you dont listen to me",
        "But then I found out I got the job!",
        "I am so incredibly happy right now!",
    ]

    for user_input in test_inputs:
        sentiment = analyzer.analyze_text(user_input)
        state = tracker.update_state(user_input, sentiment)
        print(f"User: '{user_input}'")
        print(f"  -> Sentiment: {sentiment:.4f}  Valence: {state['valence']:.4f}")
        print(f"  -> Mood: {state['mood']}  Intensity: {state['intensity']}  Hostile: {state['is_hostile']}\n")
