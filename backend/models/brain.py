"""
Multi-layer Brain Simulation for DreamTalk.
Amygdala (Emotional), Hippocampus (Memory), Prefrontal Cortex (Rational), Neocortex (Creative).
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class BigFiveTraits:
    extroversion: float      # 0 to 1
    agreeableness: float     # 0 to 1
    neuroticism: float       # 0 to 1
    openness: float          # 0 to 1
    conscientiousness: float # 0 to 1

class NeuralBrainSimulation:
    def __init__(self, traits: Optional[BigFiveTraits] = None):
        self.traits = traits or BigFiveTraits(0.5, 0.5, 0.4, 0.8, 0.5)
        self.arousal_baseline = self.traits.neuroticism * 0.5
        self.cognitive_load = 0.0

    def process_decision(self, user_input: str, emotion: Dict, context: Dict) -> Dict:
        """Process decision through multi-layer brain model."""
        
        # 1. Amygdala (Emotional Layer)
        # Raw emotional intensity and survival instincts
        emotional_intensity = abs(emotion["vad"][1])
        is_hostile = emotion["vad"][0] < -0.6 and emotion["vad"][1] > 0.5
        
        # 2. Hippocampus (Memory Layer)
        # Recall past interactions to influence current decision
        memory_resonance = self._calculate_memory_resonance(context["ltm"])
        
        # 3. Prefrontal Cortex (Rational Layer)
        # Conflict resolution between raw emotion and logic
        rational_override = self._calculate_rational_override(emotional_intensity)
        
        # 4. Neocortex (Creative Layer)
        # Creative response styling and pattern generation
        creativity_level = self.traits.openness * (1.0 - rational_override)
        
        # 5. Behavioral Randomness (Controlled)
        spontaneity = random.uniform(0, 0.2) * self.traits.openness
        
        # 6. Response Delay Simulation (Thinking Time)
        delay = self._calculate_response_delay(len(user_input), emotional_intensity)
        
        return {
            "layers": {
                "amygdala": {"intensity": emotional_intensity, "hostile": is_hostile},
                "hippocampus": {"resonance": memory_resonance},
                "pfc": {"rational_override": rational_override},
                "neocortex": {"creativity": creativity_level}
            },
            "spontaneity": spontaneity,
            "delay_ms": int(delay * 1000)
        }

    def _calculate_memory_resonance(self, ltm: List[Dict]) -> float:
        """Calculate how much past memories should influence the current state."""
        if not ltm: return 0.0
        # More memories = higher resonance, up to a point
        return min(1.0, len(ltm) * 0.1)

    def _calculate_rational_override(self, emotional_intensity: float) -> float:
        """High emotional intensity reduces rational control (PFC)."""
        # Conscientiousness helps maintain rational control
        # Neuroticism makes it harder to maintain control
        base_override = self.traits.conscientiousness * 0.7
        emotion_impact = emotional_intensity * (1.0 + self.traits.neuroticism)
        return max(0.1, base_override - (emotion_impact * 0.5))

    def _calculate_response_delay(self, input_len: int, emotional_intensity: float) -> float:
        """Simulate time taken to process complex emotional states."""
        base_delay = 0.5  # Min delay
        # More complex input or higher emotional load = longer delay
        complexity_delay = (input_len / 100) * 0.5
        emotional_delay = emotional_intensity * 1.5
        # Extroverts might respond faster
        extroversion_bonus = self.traits.extroversion * 0.5
        
        total_delay = base_delay + complexity_delay + emotional_delay - extroversion_bonus
        return max(0.5, min(4.0, total_delay))

    def update_traits(self, new_traits: BigFiveTraits):
        self.traits = new_traits
