"""
Neural Emotion Engine - Mimicking Human Brain Decision Making

Replaces template-based responses with true neural decision-making:
- Emotional Processing Layer (Amygdala analog)
- Personality Synthesis Layer (Prefrontal Cortex analog) 
- Creative Generation Layer (Neocortex analog)
"""

import random
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@dataclass
class NeuralState:
    """Represents the current neural activation state"""
    emotional_arousal: float  # 0.0 to 1.0
    cognitive_load: float    # 0.0 to 1.0
    creativity_level: float  # 0.0 to 1.0
    response_urgency: float  # 0.0 to 1.0


@dataclass  
class PersonalityProfile:
    """Core personality traits that influence response style"""
    extroversion: float      # 0.0 to 1.0 (talkative vs reserved)
    agreeableness: float     # 0.0 to 1.0 (cooperative vs antagonistic)
    neuroticism: float       # 0.0 to 1.0 (emotional stability)
    openness: float          # 0.0 to 1.0 (creative vs conventional)
    conscientiousness: float # 0.0 to 1.0 (organized vs spontaneous)


class EmotionalProcessingLayer:
    """Mimics amygdala/limbic system - raw emotional processing"""
    
    def __init__(self):
        self.emotional_weights = {
            'anger': 0.8, 'fear': 0.6, 'joy': 0.9, 'sadness': 0.7,
            'surprise': 0.5, 'disgust': 0.4, 'trust': 0.85
        }
    
    def process_sentiment(self, sentiment_score: float) -> Dict[str, float]:
        """Convert VADER sentiment to emotional activation"""
        emotional_activation = {}
        
        # Neural emotional mapping
        if sentiment_score > 0.5:
            emotional_activation['joy'] = sentiment_score * self.emotional_weights['joy']
            emotional_activation['trust'] = sentiment_score * 0.7
        elif sentiment_score > 0.2:
            emotional_activation['joy'] = sentiment_score * 0.6
            emotional_activation['surprise'] = 0.3
        elif sentiment_score > -0.2:
            emotional_activation['neutral'] = 0.5
        elif sentiment_score > -0.5:
            emotional_activation['sadness'] = abs(sentiment_score) * 0.7
            emotional_activation['fear'] = abs(sentiment_score) * 0.4
        else:
            emotional_activation['anger'] = abs(sentiment_score) * self.emotional_weights['anger']
            emotional_activation['disgust'] = abs(sentiment_score) * 0.5
        
        return emotional_activation


class PersonalitySynthesisLayer:
    """Mimics prefrontal cortex - personality and decision making"""
    
    def __init__(self):
        # Core personality profile (configurable)
        self.profile = PersonalityProfile(
            extroversion=0.8,      # Quite talkative
            agreeableness=0.6,    # Moderately cooperative  
            neuroticism=0.4,      # Emotionally stable
            openness=0.9,         # Very creative
            conscientiousness=0.5 # Balanced organization
        )
    
    def determine_response_style(self, emotional_activation: Dict[str, float], 
                               neural_state: NeuralState) -> Dict[str, float]:
        """Decide response characteristics based on personality and emotion"""
        
        style = {
            'formality': 0.2 + (1 - self.profile.extroversion) * 0.3,
            'warmth': self.profile.agreeableness * 0.8,
            'creativity': self.profile.openness * neural_state.creativity_level,
            'directness': 0.7 - (self.profile.agreeableness * 0.4),
            'length': 0.5 + (self.profile.extroversion * 0.3) - (neural_state.response_urgency * 0.4)
        }
        
        # Emotional adjustments
        if 'anger' in emotional_activation:
            style['directness'] += 0.3
            style['warmth'] -= 0.4
            style['length'] -= 0.3
        
        if 'joy' in emotional_activation:
            style['warmth'] += 0.2
            style['creativity'] += 0.2
        
        return style


class CreativeGenerationLayer:
    """Mimics neocortex/temporal lobe - organic response construction"""
    
    def __init__(self):
        self.linguistic_patterns = {
            'casual': ['hey', 'yo', 'lol', 'haha', 'tbh', 'fr', 'ngl'],
            'formal': ['certainly', 'however', 'furthermore', 'additionally'],
            'emphatic': ['absolutely', 'definitely', 'seriously', 'for real'],
            'hedging': ['maybe', 'perhaps', 'sort of', 'kind of', 'a bit']
        }
    
    def construct_neural_prompt(self, user_input: str, emotional_activation: Dict[str, float],
                              response_style: Dict[str, float], context: List[Dict]) -> str:
        """Create organic prompt that guides but doesn't template the response"""
        
        # Emotional state description
        primary_emotion = max(emotional_activation.items(), key=lambda x: x[1])[0] if emotional_activation else 'neutral'
        
        prompt_parts = [
            "You are DreamTalk, a real human-like conversational partner.",
            "Generate completely organic, spontaneous responses — NO TEMPLATES.",
            "Your responses should feel like natural human conversation.",
            f"Current emotional vibe: Feeling {primary_emotion} (intensity: {max(emotional_activation.values()) if emotional_activation else 0.3:.1f})",
            f"Conversational style: {"warm and engaging" if response_style['warmth'] > 0.6 else "direct and straightforward"}",
            "Response should be: " + self._get_length_descriptor(response_style['length']),
            "",
            "Recent conversation:"
        ]
        
        # Add context
        for turn in context[-3:]:  # Last 3 turns for context
            prompt_parts.append(f"{turn['role']}: {turn['content']}")
        
        prompt_parts.extend([
            "",
            f"User: {user_input}",
            "DreamTalk: [Generate completely organic response that matches the emotional vibe and style above]"
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_length_descriptor(self, length_score: float) -> str:
        if length_score > 0.8:
            return "detailed and expressive (2-3 sentences)"
        elif length_score > 0.6:
            return "thoughtful response (1-2 sentences)"
        elif length_score > 0.4:
            return "concise but complete (1 sentence)"
        else:
            return "very brief and direct (few words)"


class NeuralEmotionEngine:
    """Orchestrates the neural decision-making process"""
    
    def __init__(self):
        self.emotional_layer = EmotionalProcessingLayer()
        self.personality_layer = PersonalitySynthesisLayer()
        self.creative_layer = CreativeGenerationLayer()
        self.conversation_history = []
    
    def process_input(self, user_input: str, sentiment_score: float) -> Tuple[str, Dict]:
        """Full neural processing pipeline"""
        
        # 1. Emotional Processing (Amygdala analog)
        emotional_activation = self.emotional_layer.process_sentiment(sentiment_score)
        
        # 2. Neural State Calculation
        neural_state = self._calculate_neural_state(emotional_activation)
        
        # 3. Personality Synthesis (Prefrontal Cortex analog)
        response_style = self.personality_layer.determine_response_style(
            emotional_activation, neural_state
        )
        
        # 4. Creative Prompt Construction (Neocortex analog)
        neural_prompt = self.creative_layer.construct_neural_prompt(
            user_input, emotional_activation, response_style, self.conversation_history
        )
        
        # Update history
        self.conversation_history.append({'role': 'user', 'content': user_input})
        
        return neural_prompt, {
            'emotional_activation': emotional_activation,
            'neural_state': neural_state.__dict__,
            'response_style': response_style
        }
    
    def _calculate_neural_state(self, emotional_activation: Dict[str, float]) -> NeuralState:
        """Calculate current neural activation levels"""
        total_emotion = sum(emotional_activation.values()) if emotional_activation else 0.3
        
        return NeuralState(
            emotional_arousal=min(1.0, total_emotion * 1.2),
            cognitive_load=0.3 + (total_emotion * 0.4),
            creativity_level=0.6 + (random.random() * 0.3),
            response_urgency=0.4 + (total_emotion * 0.4)
        )


# Test the neural engine
if __name__ == "__main__":
    engine = NeuralEmotionEngine()
    
    test_inputs = [
        ("hello", 0.1),
        ("i'm not in a good mood", -0.4), 
        ("you are a selfish model", -0.8),
        ("no you are shit", -0.7)
    ]
    
    for user_input, sentiment in test_inputs:
        print(f"\n=== Processing: '{user_input}' (sentiment: {sentiment}) ===")
        prompt, metadata = engine.process_input(user_input, sentiment)
        print(f"Neural Prompt:\n{prompt}")
        print(f"Metadata: {metadata}")