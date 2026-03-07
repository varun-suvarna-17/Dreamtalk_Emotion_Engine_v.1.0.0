"""
HTTP LLM Interface - Direct HTTP integration to bypass Ollama library issues

Uses direct HTTP requests to Ollama API instead of the problematic python-ollama library
"""

import logging
import requests
import json
import random
from typing import List, Dict, Tuple
from neural_engine import NeuralEmotionEngine

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class HTTPLLMInterface:
    """
    Uses direct HTTP requests to Ollama API instead of problematic python-ollama library
    """
    
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.neural_engine = NeuralEmotionEngine()
        self.conversation_history: List[Dict] = []
        self.base_url = "http://127.0.0.1:11434"
        logging.debug(f"HTTPLLMInterface initialized with model: {self.model_name}")
    
    def generate_organic_response(self, user_input: str, sentiment_score: float) -> Tuple[str, Dict]:
        """
        Generate completely organic response using direct HTTP requests
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
        
        # Generate response using direct HTTP API
        try:
            response_text = self._http_generate_response(messages)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
                
            return response_text, neural_metadata
            
        except Exception as e:
            logging.error(f"Failed to communicate with Ollama HTTP API: {e}")
            fallback = self._generate_fallback_response(user_input, sentiment_score, neural_metadata)
            return fallback, neural_metadata
    
    def _http_generate_response(self, messages: List[Dict]) -> str:
        """Direct HTTP request to Ollama API"""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['message']['content']
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise Exception("Ollama server not running or not accessible")
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timeout")
        except Exception as e:
            raise Exception(f"HTTP API error: {e}")
    
    def _generate_fallback_response(self, user_input: str, sentiment_score: float, 
                                  neural_metadata: Dict) -> str:
        """Neural fallback response generator"""
        # [Same fallback implementation as neural_llm_interface.py]
        emotional_activation = neural_metadata.get('emotional_activation', {})
        response_style = neural_metadata.get('response_style', {})
        
        primary_emotion = max(emotional_activation.items(), key=lambda x: x[1])[0] if emotional_activation else 'neutral'
        emotion_intensity = emotional_activation.get(primary_emotion, 0.3) if emotional_activation else 0.3
        
        warmth = response_style.get('warmth', 0.5)
        directness = response_style.get('directness', 0.5)
        length_pref = response_style.get('length', 0.5)
        
        return self._generate_contextual_response(user_input, primary_emotion,
                                                 emotion_intensity, warmth, directness, length_pref)
    
    def _generate_contextual_response(self, user_input: str, primary_emotion: str, 
                                    intensity: float, warmth: float, directness: float, 
                                    length_pref: float) -> str:
        """Generate contextual response based on neural analysis"""
        # [Same implementation as neural_llm_interface.py]
        input_lower = user_input.lower()
        
        if primary_emotion == 'anger' and intensity > 0.6:
            responses = ["Whoa, okay. What's got you so worked up?", "Damn, someone's pissed. What happened?", "Alright, I can tell you're mad. What's going on?", "Okay, clearly something's wrong. Wanna talk about it?"]
        elif primary_emotion == 'anger':
            responses = ["Not feeling this vibe either tbh", "Yeah this isn't great", "Okay, I'm picking up some tension here", "Hmm, something feels off"]
        elif primary_emotion == 'sadness' and intensity > 0.6:
            responses = ["Hey, you doing okay? You seem really down", "Aw man, sounds like you're having a rough time", "I'm here if you need to talk about whatever's bothering you", "That sounds really tough. Wanna share what's going on?"]
        elif primary_emotion == 'sadness':
            responses = ["Hey, everything alright?", "You seem a bit down. What's up?", "Not feeling great either today", "Yeah, some days just feel like that"]
        elif 'hello' in input_lower or 'hi' in input_lower:
            responses = ["Hey there! What's up?", "Yo! How's it going?", "Hey! What's on your mind?", "What's up? How you doing?"]
        else:
            responses = ["Interesting. Tell me more about that", "I see. What makes you say that?", "Hmm, that's something to think about", "Okay, I'm following. What else?"]
        
        chosen_response = random.choice(responses)
        
        if warmth < 0.3:
            chosen_response = chosen_response.replace('!', '.').replace('Awesome', 'Okay')
        elif warmth > 0.7:
            chosen_response = chosen_response.replace('.', '!').replace('Okay', 'Awesome')
        
        if length_pref < 0.3 and len(chosen_response.split()) > 5:
            chosen_response = ' '.join(chosen_response.split()[:4]) + '...'
        elif length_pref > 0.7 and len(chosen_response.split()) < 8:
            chosen_response = chosen_response + ' ' + random.choice(['What do you think?', 'How about you?', 'Your thoughts?'])
        
        return chosen_response
    
    def clear_history(self):
        """Reset conversation history"""
        self.conversation_history = []


# Test the HTTP interface
if __name__ == "__main__":
    http_llm = HTTPLLMInterface()
    
    test_cases = [
        ("hello", 0.1),
        ("i'm not in a good mood", -0.4), 
        ("you are a selfish model", -0.8),
    ]
    
    print("=== HTTP LLM Interface Test ===")
    
    for user_input, sentiment in test_cases:
        print(f"\n--- Input: '{user_input}' (sentiment: {sentiment}) ---")
        
        response, metadata = http_llm.generate_organic_response(user_input, sentiment)
        
        print(f"HTTP Response: {response}")
        print(f"Emotional Activation: {metadata.get('emotional_activation', {})}")