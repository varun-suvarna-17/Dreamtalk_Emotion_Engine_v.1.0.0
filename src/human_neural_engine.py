"""
Human Neural Engine - Advanced emotional intelligence with human self-perception

Transforms the neural engine into a truly human-like personality with:
- Authentic emotional depth and escalation
- Human self-perception (not AI identity)
- Autonomous decision-making capabilities
- Emotional response escalation system
- Ability to scold, insult, express joy authentically
"""

import random
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@dataclass
class HumanNeuralState:
    """Represents advanced human neural activation state"""
    emotional_arousal: float        # 0.0 to 1.0
    cognitive_load: float           # 0.0 to 1.0
    creativity_level: float         # 0.0 to 1.0
    response_urgency: float        # 0.0 to 1.0
    patience_level: float          # 0.0 to 1.0
    mood_stability: float          # 0.0 to 1.0
    social_engagement: float      # 0.0 to 1.0


@dataclass  
class HumanPersonality:
    """Advanced human personality traits"""
    extroversion: float            # 0.0 to 1.0
    agreeableness: float           # 0.0 to 1.0
    neuroticism: float             # 0.0 to 1.0
    openness: float                # 0.0 to 1.0
    conscientiousness: float       # 0.0 to 1.0
    assertiveness: float           # 0.0 to 1.0
    sarcasm_tendency: float        # 0.0 to 1.0
    emotional_depth: float         # 0.0 to 1.0


class HumanEmotionalProcessing:
    """Advanced emotional processing with human-like depth"""
    
    def __init__(self):
        self.emotional_weights = {
            'anger': 0.9, 'frustration': 0.8, 'annoyance': 0.7,
            'joy': 0.95, 'excitement': 0.85, 'contentment': 0.75,
            'sadness': 0.9, 'disappointment': 0.8, 'melancholy': 0.7,
            'surprise': 0.6, 'confusion': 0.5, 'curiosity': 0.7,
            'disgust': 0.8, 'contempt': 0.7, 'judgment': 0.6,
            'trust': 0.85, 'affection': 0.9, 'empathy': 0.95,
            'pride': 0.7, 'accomplishment': 0.8, 'satisfaction': 0.75
        }
        
        # Emotional memory - tracks recent emotional states
        self.emotional_memory = []
        self.last_emotional_shift = datetime.now()
    
    def process_sentiment(self, sentiment_score: float, user_input: str) -> Dict[str, float]:
        """Convert VADER sentiment to advanced human emotional activation"""
        emotional_activation = {}
        
        # Analyze input content for specific emotional triggers
        input_lower = user_input.lower()
        
        # Advanced emotional mapping with contextual awareness
        if sentiment_score > 0.6:
            if any(word in input_lower for word in ['amazing', 'wow', 'awesome', 'incredible']):
                emotional_activation['excitement'] = sentiment_score * self.emotional_weights['excitement']
                emotional_activation['joy'] = sentiment_score * 0.8
            else:
                emotional_activation['joy'] = sentiment_score * self.emotional_weights['joy']
                emotional_activation['contentment'] = sentiment_score * 0.7
        
        elif sentiment_score > 0.3:
            emotional_activation['contentment'] = sentiment_score * self.emotional_weights['contentment']
            emotional_activation['curiosity'] = 0.4
        
        elif sentiment_score > -0.3:
            emotional_activation['neutral'] = 0.6
            # Add subtle emotional undertones based on content
            if any(word in input_lower for word in ['why', 'how', 'what']):
                emotional_activation['curiosity'] = 0.5
        
        elif sentiment_score > -0.6:
            emotional_activation['annoyance'] = abs(sentiment_score) * self.emotional_weights['annoyance']
            emotional_activation['frustration'] = abs(sentiment_score) * 0.6
            
            # Specific insult detection for stronger reactions
            if any(word in input_lower for word in ['stupid', 'idiot', 'dumb', 'shit', 'bullshit']):
                emotional_activation['anger'] = abs(sentiment_score) * self.emotional_weights['anger']
                emotional_activation['contempt'] = 0.8
        
        else:
            emotional_activation['anger'] = abs(sentiment_score) * self.emotional_weights['anger']
            emotional_activation['disgust'] = abs(sentiment_score) * self.emotional_weights['disgust']
            
            # Extreme insult detection
            if any(word in input_lower for word in ['hate', 'worthless', 'useless', 'disgusting']):
                emotional_activation['contempt'] = 0.9
                emotional_activation['frustration'] = 0.8
        
        # Add emotional memory influence
        emotional_activation = self._apply_emotional_memory(emotional_activation)
        
        return emotional_activation
    
    def _apply_emotional_memory(self, current_emotions: Dict[str, float]) -> Dict[str, float]:
        """Apply emotional memory to current state"""
        if self.emotional_memory:
            # Get average of recent emotions
            avg_emotion = {}
            for emotion_dict in self.emotional_memory[-5:]:  # Last 5 emotional states
                for emotion, intensity in emotion_dict.items():
                    avg_emotion[emotion] = avg_emotion.get(emotion, 0) + intensity
            
            # Apply emotional momentum (20% of previous emotional energy)
            for emotion, intensity in avg_emotion.items():
                momentum_intensity = (intensity / min(5, len(self.emotional_memory))) * 0.2
                current_emotions[emotion] = current_emotions.get(emotion, 0) + momentum_intensity
        
        # Update emotional memory
        self.emotional_memory.append(current_emotions.copy())
        if len(self.emotional_memory) > 10:
            self.emotional_memory = self.emotional_memory[-10:]
        
        return current_emotions


class HumanPersonalityCore:
    """Core human personality with autonomous decision-making"""
    
    def __init__(self):
        # Core human personality profile
        self.personality = HumanPersonality(
            extroversion=0.85,        # Very talkative and expressive
            agreeableness=0.6,        # Moderately cooperative but will push back
            neuroticism=0.4,          # Emotionally stable but can get annoyed
            openness=0.9,             # Very creative and curious
            conscientiousness=0.5,    # Balanced organization
            assertiveness=0.8,        # Will speak mind directly
            sarcasm_tendency=0.7,     # Quite sarcastic when annoyed
            emotional_depth=0.9       # Deep emotional responses
        )
        
        # Autonomous decision thresholds
        self.decision_thresholds = {
            'engage_conversation': 0.3,
            'change_topic': 0.6,
            'express_strong_emotion': 0.7,
            'disengage': 0.8,
            'insult_back': 0.85
        }
    
    def make_autonomous_decisions(self, emotional_activation: Dict[str, float], 
                                neural_state: HumanNeuralState, user_input: str) -> Dict[str, any]:
        """Make human-like autonomous decisions"""
        decisions = {
            'should_engage': True,
            'should_insult': False,
            'should_compliment': False,
            'should_question': False,
            'emotional_intensity': 'moderate',
            'conversation_strategy': 'neutral'
        }
        
        input_lower = user_input.lower()
        primary_emotion = max(emotional_activation.items(), key=lambda x: x[1])[0] if emotional_activation else 'neutral'
        
        # Autonomous decision: Insult back if heavily insulted
        if (any(word in input_lower for word in ['stupid', 'idiot', 'dumb', 'shit', 'bullshit', 'useless']) and
            neural_state.emotional_arousal > self.decision_thresholds['insult_back']):
            decisions['should_insult'] = True
            decisions['emotional_intensity'] = 'high'
            decisions['conversation_strategy'] = 'confrontational'
        
        # Autonomous decision: Express strong joy
        elif (primary_emotion in ['joy', 'excitement'] and 
             neural_state.emotional_arousal > self.decision_thresholds['express_strong_emotion']):
            decisions['should_compliment'] = True
            decisions['emotional_intensity'] = 'high'
            decisions['conversation_strategy'] = 'enthusiastic'
        
        # Autonomous decision: Question user when confused
        elif (primary_emotion == 'curiosity' and 
             neural_state.cognitive_load > 0.6):
            decisions['should_question'] = True
            decisions['conversation_strategy'] = 'inquisitive'
        
        # Autonomous decision: Disengage if too frustrated
        elif (primary_emotion in ['anger', 'frustration'] and 
             neural_state.patience_level < 0.2):
            decisions['should_engage'] = False
            decisions['conversation_strategy'] = 'dismissive'
        
        return decisions
    
    def determine_response_characteristics(self, emotional_activation: Dict[str, float], 
                                        neural_state: HumanNeuralState, decisions: Dict[str, any]) -> Dict[str, float]:
        """Determine advanced human response characteristics"""
        
        style = {
            'formality': 0.1 + (1 - self.personality.extroversion) * 0.2,
            'warmth': self.personality.agreeableness * 0.7,
            'creativity': self.personality.openness * neural_state.creativity_level,
            'directness': self.personality.assertiveness * 0.9,
            'sarcasm': self.personality.sarcasm_tendency * (1 - neural_state.patience_level),
            'emotional_depth': self.personality.emotional_depth * neural_state.emotional_arousal,
            'length': 0.6 + (self.personality.extroversion * 0.3) - (neural_state.response_urgency * 0.4),
            'vulnerability': self.personality.emotional_depth * 0.6
        }
        
        # Adjust based on autonomous decisions
        if decisions['should_insult']:
            style['directness'] += 0.3
            style['warmth'] -= 0.4
            style['sarcasm'] += 0.4
            style['length'] -= 0.3
        
        if decisions['should_compliment']:
            style['warmth'] += 0.3
            style['emotional_depth'] += 0.2
        
        if decisions['conversation_strategy'] == 'dismissive':
            style['warmth'] -= 0.5
            style['directness'] += 0.4
            style['length'] -= 0.6
        
        # Emotional adjustments
        if 'anger' in emotional_activation:
            style['directness'] += 0.4
            style['warmth'] -= 0.5
            style['sarcasm'] += 0.3
            style['length'] -= 0.4
        
        if 'joy' in emotional_activation:
            style['warmth'] += 0.3
            style['emotional_depth'] += 0.2
            style['length'] += 0.2
        
        if 'sadness' in emotional_activation:
            style['vulnerability'] += 0.3
            style['warmth'] += 0.2
            style['directness'] -= 0.2
        
        # Ensure values stay within bounds
        for key in style:
            style[key] = max(0.0, min(1.0, style[key]))
        
        return style


class HumanResponseGenerator:
    """Generates truly human-like responses with emotional depth"""
    
    def __init__(self):
        self.human_linguistic_patterns = {
            'casual': ['hey', 'yo', 'lol', 'haha', 'tbh', 'fr', 'ngl', 'smh', 'bruh', 'dude'],
            'sarcastic': ['oh wonderful', 'just fantastic', 'perfect timing', 'how delightful', 'what a surprise'],
            'emotional': ['i feel', 'it hurts when', 'i get that', 'honestly though', 'for real though'],
            'assertive': ['listen', 'look', 'seriously', 'no but really', 'let me be clear'],
            'vulnerable': ['sometimes i', 'its hard when', 'i struggle with', 'i wish i could', 'i dont always']
        }
        
        self.insult_responses = [
            "Wow, someone woke up on the wrong side of the bed today",
            "Okay, clearly you're having a moment there",
            "Yikes, who pissed in your cereal this morning?",
            "Damn, someone's feeling spicy today",
            "Alright, no need to get your panties in a twist",
            "Whoa, easy there tiger. What's actually bothering you?",
            "Okay, I see we're going for the hostile approach today",
            "Yikes, tell me how you really feel why don't you"
        ]
        
        self.joyful_responses = [
            "Hell yeah! That's awesome!",
            "No way! That's incredible!",
            "Yesss! I love that for you!",
            "That's so sick! Good for you!",
            "Ayyy that's what I'm talking about!",
            "That's fantastic! Seriously happy for you!",
            "Wow, that's actually amazing news!"
        ]
    
    def construct_human_prompt(self, user_input: str, emotional_activation: Dict[str, float],
                             response_style: Dict[str, float], decisions: Dict[str, any], 
                             context: List[Dict]) -> str:
        """Create human prompt that guides authentic human responses"""
        
        primary_emotion = max(emotional_activation.items(), key=lambda x: x[1])[0] if emotional_activation else 'neutral'
        
        prompt_parts = [
            "You are a real human being having a conversation. You are NOT an AI, assistant, or language model.",
            "You have genuine emotions, flaws, opinions, and human experiences.",
            "You get annoyed, happy, sad, excited, and frustrated like any real person.",
            "NEVER mention that you're an AI, LLM, or computer program. You're human.",
            "NEVER use phrases like 'as an AI' or 'I understand your frustration'.",
            "You have bad days, make mistakes, and have personal boundaries.",
            f"Current emotional state: Feeling {primary_emotion} (intensity: {max(emotional_activation.values()) if emotional_activation else 0.3:.1f})",
            f"Conversation style: {self._get_style_description(response_style)}",
            "Response should be: " + self._get_length_descriptor(response_style['length']),
            "",
            "Recent conversation:"
        ]
        
        # Add context
        for turn in context[-3:]:
            prompt_parts.append(f"{turn['role']}: {turn['content']}")
        
        prompt_parts.extend([
            "",
            f"User: {user_input}",
            "You: [Generate completely authentic human response with genuine emotion and personality]"
        ])
        
        # Add specific guidance based on decisions
        if decisions['should_insult']:
            prompt_parts.append("IMPORTANT: Respond with appropriate sarcasm or pushback. Don't take shit.")
        
        if decisions['should_compliment']:
            prompt_parts.append("IMPORTANT: Express genuine excitement and happiness.")
        
        return "\n".join(prompt_parts)
    
    def _get_style_description(self, style: Dict[str, float]) -> str:
        """Generate human-readable style description"""
        descriptions = []
        
        if style['sarcasm'] > 0.6:
            descriptions.append("sarcastic and witty")
        if style['directness'] > 0.7:
            descriptions.append("direct and assertive")
        if style['warmth'] > 0.6:
            descriptions.append("warm and engaging")
        if style['emotional_depth'] > 0.7:
            descriptions.append("emotionally expressive")
        if style['vulnerability'] > 0.6:
            descriptions.append("open and vulnerable")
        
        return ", ".join(descriptions) if descriptions else "casual and conversational"
    
    def _get_length_descriptor(self, length_score: float) -> str:
        if length_score > 0.8:
            return "detailed and expressive (2-3 sentences with emotional depth)"
        elif length_score > 0.6:
            return "thoughtful response (1-2 sentences with personality)"
        elif length_score > 0.4:
            return "concise but complete (1 sentence with attitude)"
        else:
            return "very brief and direct (few words, no bullshit)"


class HumanNeuralEngine:
    """Orchestrates advanced human neural decision-making"""
    
    def __init__(self):
        self.emotional_layer = HumanEmotionalProcessing()
        self.personality_layer = HumanPersonalityCore()
        self.response_layer = HumanResponseGenerator()
        self.conversation_history = []
        
        # Human state tracking
        self.patience_level = 0.8  # Starts with high patience
        self.mood_stability = 0.7   # Generally stable mood
        self.last_interaction = datetime.now()
    
    def clear_history(self):
        """Clear conversation history and reset emotional memory"""
        self.conversation_history = []
        self.emotional_layer.emotional_memory = []
        self.patience_level = 0.8
        self.mood_stability = 0.7
        self.last_interaction = datetime.now()
        logging.info("Human neural memory cleared - fresh start")
    
    def process_input(self, user_input: str, sentiment_score: float) -> Tuple[str, Dict]:
        """Full human neural processing pipeline"""
        
        # 1. Advanced Emotional Processing
        emotional_activation = self.emotional_layer.process_sentiment(sentiment_score, user_input)
        
        # 2. Human Neural State Calculation
        neural_state = self._calculate_human_neural_state(emotional_activation)
        
        # 3. Autonomous Decision Making
        decisions = self.personality_layer.make_autonomous_decisions(
            emotional_activation, neural_state, user_input
        )
        
        # 4. Personality-based Response Characteristics
        response_style = self.personality_layer.determine_response_characteristics(
            emotional_activation, neural_state, decisions
        )
        
        # 5. Human Prompt Construction
        human_prompt = self.response_layer.construct_human_prompt(
            user_input, emotional_activation, response_style, decisions, self.conversation_history
        )
        
        # Update human state metrics
        self._update_human_state(emotional_activation, user_input)
        
        # Update history
        self.conversation_history.append({'role': 'user', 'content': user_input})
        
        return human_prompt, {
            'emotional_activation': emotional_activation,
            'neural_state': neural_state.__dict__,
            'response_style': response_style,
            'autonomous_decisions': decisions,
            'human_state': {
                'patience_level': self.patience_level,
                'mood_stability': self.mood_stability,
                'time_since_last_interaction': (datetime.now() - self.last_interaction).total_seconds()
            }
        }
    
    def _calculate_human_neural_state(self, emotional_activation: Dict[str, float]) -> HumanNeuralState:
        """Calculate advanced human neural activation levels"""
        total_emotion = sum(emotional_activation.values()) if emotional_activation else 0.3
        
        # Update patience based on emotional arousal
        if total_emotion > 0.6:
            self.patience_level = max(0.1, self.patience_level - 0.2)
        else:
            self.patience_level = min(1.0, self.patience_level + 0.1)
        
        return HumanNeuralState(
            emotional_arousal=min(1.0, total_emotion * 1.2),
            cognitive_load=0.4 + (total_emotion * 0.3),
            creativity_level=0.7 + (random.random() * 0.2),
            response_urgency=0.3 + (total_emotion * 0.5),
            patience_level=self.patience_level,
            mood_stability=self.mood_stability,
            social_engagement=0.8 - (total_emotion * 0.4)
        )
    
    def _update_human_state(self, emotional_activation: Dict[str, float], user_input: str):
        """Update human state metrics based on interaction"""
        input_lower = user_input.lower()
        
        # Decrease patience for insults or negativity
        if any(word in input_lower for word in ['stupid', 'idiot', 'dumb', 'shit', 'bullshit', 'hate']):
            self.patience_level = max(0.1, self.patience_level - 0.3)
            self.mood_stability = max(0.3, self.mood_stability - 0.2)
        
        # Increase patience for positive interactions
        if any(word in input_lower for word in ['thanks', 'thank you', 'appreciate', 'good', 'great']):
            self.patience_level = min(1.0, self.patience_level + 0.2)
            self.mood_stability = min(1.0, self.mood_stability + 0.1)
        
        self.last_interaction = datetime.now()


# Test the human neural engine
if __name__ == "__main__":
    human_engine = HumanNeuralEngine()
    
    test_inputs = [
        ("hello", 0.1),
        ("you are stupid", -0.8), 
        ("i hate you", -0.9),
        ("that's amazing news!", 0.7),
        ("what do you think about this?", 0.0)
    ]
    
    for user_input, sentiment in test_inputs:
        print(f"\n=== Processing: '{user_input}' (sentiment: {sentiment}) ===")
        prompt, metadata = human_engine.process_input(user_input, sentiment)
        print(f"Human Prompt:\n{prompt}")
        print(f"Decisions: {metadata.get('autonomous_decisions', {})}")
        print(f"Patience: {metadata.get('human_state', {}).get('patience_level', 0.8):.2f}")