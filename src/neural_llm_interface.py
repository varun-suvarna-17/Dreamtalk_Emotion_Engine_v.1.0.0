"""
Neural LLM Interface - Integrates neural emotion engine with LLM generation

Replaces template-based prompting with true neural decision-making
"""

import logging
import random
import ollama
from typing import List, Dict, Tuple
from neural_engine import NeuralEmotionEngine

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class NeuralLLMInterface:
    """
    Uses neural emotion engine to create organic, human-like responses
    instead of template-based generation
    """
    
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.neural_engine = NeuralEmotionEngine()
        self.conversation_history: List[Dict] = []
        logging.debug(f"NeuralLLMInterface initialized with model: {self.model_name}")
    
    def generate_organic_response(self, user_input: str, sentiment_score: float) -> Tuple[str, Dict]:
        """
        Generate completely organic response using neural decision-making
        """
        # Process through neural emotion engine
        neural_prompt, neural_metadata = self.neural_engine.process_input(
            user_input, sentiment_score
        )
        
        # Create messages for LLM
        messages = [
            {"role": "system", "content": neural_prompt},
            *self.conversation_history[-6:],  # Last 3 exchanges (6 messages)
            {"role": "user", "content": user_input}
        ]
        
        # Generate response
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            response_text = response['message']['content']
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
                
            return response_text, neural_metadata
            
        except Exception as e:
            logging.error(f"Failed to communicate with local LLM: {e}")
            fallback = self._generate_fallback_response(user_input, sentiment_score, neural_metadata)
            return fallback, neural_metadata
    
    def _generate_fallback_response(self, user_input: str, sentiment_score: float, 
                                  neural_metadata: Dict) -> str:
        """
        Neural fallback response generator - creates contextual responses
        based on emotional analysis when LLM is unavailable
        """
        emotional_activation = neural_metadata.get('emotional_activation', {})
        response_style = neural_metadata.get('response_style', {})
        
        # Get primary emotion
        primary_emotion = max(emotional_activation.items(), key=lambda x: x[1])[0] if emotional_activation else 'neutral'
        emotion_intensity = emotional_activation.get(primary_emotion, 0.3) if emotional_activation else 0.3
        
        # Determine response characteristics
        warmth = response_style.get('warmth', 0.5)
        directness = response_style.get('directness', 0.5)
        length_pref = response_style.get('length', 0.5)
        
        # Contextual response generation based on emotion and content
        response = self._generate_contextual_response(user_input, primary_emotion, 
                                                     emotion_intensity, warmth, directness, length_pref)
        
        return response
    
    def _generate_contextual_response(self, user_input: str, primary_emotion: str, 
                                    intensity: float, warmth: float, directness: float, 
                                    length_pref: float) -> str:
        """Generate contextual response based on neural analysis"""
        
        # Analyze user input content
        input_lower = user_input.lower()
        
        # Emotional response patterns
        if primary_emotion == 'anger' and intensity > 0.6:
            responses = [
                "Whoa, okay. What's got you so worked up?",
                "Damn, someone's pissed. What happened?",
                "Alright, I can tell you're mad. What's going on?",
                "Okay, clearly something's wrong. Wanna talk about it?"
            ]
        elif primary_emotion == 'anger':
            responses = [
                "Not feeling this vibe either tbh",
                "Yeah this isn't great",
                "Okay, I'm picking up some tension here",
                "Hmm, something feels off"
            ]
        elif primary_emotion == 'sadness' and intensity > 0.6:
            responses = [
                "Hey, you doing okay? You seem really down",
                "Aw man, sounds like you're having a rough time",
                "I'm here if you need to talk about whatever's bothering you",
                "That sounds really tough. Wanna share what's going on?"
            ]
        elif primary_emotion == 'sadness':
            responses = [
                "Hey, everything alright?",
                "You seem a bit down. What's up?",
                "Not feeling great either today",
                "Yeah, some days just feel like that"
            ]
        elif 'hello' in input_lower or 'hi' in input_lower:
            responses = [
                "Hey there! What's up?",
                "Yo! How's it going?",
                "Hey! What's on your mind?",
                "What's up? How you doing?"
            ]
        elif 'how are you' in input_lower:
            responses = [
                "I'm doing alright, thanks for asking! How about you?",
                "Pretty good! What about you?",
                "Not bad! How you holding up?",
                "Doing okay! What's new with you?"
            ]
        elif 'thank' in input_lower:
            responses = [
                "No problem! Happy to help",
                "Anytime! Glad I could assist",
                "You're welcome! Let me know if you need anything else",
                "Of course! Always here if you need me"
            ]
        elif any(word in input_lower for word in ['help', 'need', 'assist']):
            responses = [
                "What do you need help with?",
                "Sure, what can I do for you?",
                "I'm here to help! What's up?",
                "What do you need assistance with?"
            ]
        elif any(word in input_lower for word in ['sorry', 'apologize', 'my bad']):
            responses = [
                "No worries at all!",
                "It's all good, don't worry about it",
                "No problem! We're cool",
                "All good! No need to apologize"
            ]
        elif any(word in input_lower for word in ['good', 'great', 'awesome', 'wonderful']):
            responses = [
                "That's awesome to hear!",
                "Nice! Glad things are going well",
                "That's great! Happy for you",
                "Awesome! Keep that positive energy going"
            ]
        elif any(word in input_lower for word in ['bad', 'terrible', 'awful', 'horrible']):
            responses = [
                "Sorry to hear that. What's going on?",
                "That sounds rough. Wanna talk about it?",
                "Aw man, that's tough. What happened?",
                "I'm here if you need to vent about it"
            ]
        elif any(word in input_lower for word in ['love', 'like', 'enjoy', 'adore']):
            responses = [
                "That's wonderful! I'm happy for you",
                "Awesome! It's great when you find things you love",
                "Nice! What do you like about it?",
                "That's cool! Enjoy it while it lasts"
            ]
        elif any(word in input_lower for word in ['hate', 'dislike', 'can\'t stand', 'loathe']):
            responses = [
                "Yeah, I get that. Some things just rub you the wrong way",
                "Not a fan either? What don't you like about it?",
                "I hear you. Sometimes things just don't click",
                "Understandable. What specifically bothers you?"
            ]
        else:
            # Default contextual responses based on emotion
            if primary_emotion == 'joy':
                responses = [
                    "That's great to hear! What's making you feel good?",
                    "Awesome! Love the positive vibes",
                    "Nice! What's got you in such a good mood?",
                    "That's wonderful! Enjoy the moment"
                ]
            elif primary_emotion == 'trust':
                responses = [
                    "I appreciate you sharing that with me",
                    "Thanks for being open with me",
                    "I'm glad we can have this conversation",
                    "I value this connection we have"
                ]
            elif primary_emotion == 'fear':
                responses = [
                    "It's okay to feel that way. What's worrying you?",
                    "I understand feeling concerned. Want to talk about it?",
                    "That sounds anxiety-provoking. What's on your mind?",
                    "It's normal to feel apprehensive sometimes"
                ]
            elif primary_emotion == 'surprise':
                responses = [
                    "Wow, that's unexpected! Tell me more",
                    "No way! What happened?",
                    "That's surprising! How did that come about?",
                    "Interesting! Didn't see that coming"
                ]
            elif primary_emotion == 'disgust':
                responses = [
                    "Yikes, that doesn't sound pleasant",
                    "Ew, not a fan either",
                    "That sounds pretty gross tbh",
                    "Yeah, that would turn me off too"
                ]
            else:
                responses = [
                    "Interesting. Tell me more about that",
                    "I see. What makes you say that?",
                    "Hmm, that's something to think about",
                    "Okay, I'm following. What else?"
                ]
        
        # Adjust response based on warmth and directness
        chosen_response = random.choice(responses)
        
        # Make responses more/less warm based on neural analysis
        if warmth < 0.3:
            chosen_response = chosen_response.replace('!', '.').replace('Awesome', 'Okay')
        elif warmth > 0.7:
            chosen_response = chosen_response.replace('.', '!').replace('Okay', 'Awesome')
        
        # Adjust length based on preference
        if length_pref < 0.3 and len(chosen_response.split()) > 5:
            chosen_response = ' '.join(chosen_response.split()[:4]) + '...'
        elif length_pref > 0.7 and len(chosen_response.split()) < 8:
            chosen_response = chosen_response + ' ' + random.choice(['What do you think?', 'How about you?', 'Your thoughts?'])
        
        return chosen_response
    
    def clear_history(self):
        """Reset conversation history"""
        self.conversation_history = []


# Test the neural interface
if __name__ == "__main__":
    neural_llm = NeuralLLMInterface()
    
    test_cases = [
        ("hello", 0.1),
        ("i'm not in a good mood", -0.4), 
        ("you are a selfish model", -0.8),
        ("no you are shit", -0.7),
        ("what the fuck is this", -0.3)
    ]
    
    print("=== Neural LLM Interface Test ===")
    
    for user_input, sentiment in test_cases:
        print(f"\n--- Input: '{user_input}' (sentiment: {sentiment}) ---")
        
        response, metadata = neural_llm.generate_organic_response(user_input, sentiment)
        
        print(f"Neural Response: {response}")
        print(f"Emotional Activation: {metadata.get('emotional_activation', {})}")
        print(f"Response Style: {metadata.get('response_style', {})}")