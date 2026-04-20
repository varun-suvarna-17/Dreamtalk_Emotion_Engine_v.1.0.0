"""
High-Performance LLM Service for DreamTalk v3.5.
Supports LLaMA 3 70B, Mixtral 8x7B, and DeepSeek with GPU acceleration.
"""

import ollama
import logging
import asyncio
from typing import List, Dict, Generator, Optional, AsyncGenerator

class LLMService:
    def __init__(self, model_name: str = "llama3:70b"):
        self.model_name = model_name
        self.system_prompt = ""
        self.context_window = 32768  # Support for long context
        
    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    async def generate_streaming(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Generate response with asynchronous streaming support and GPU acceleration."""
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages
        
        try:
            # Note: Ollama handles CUDA/GPU acceleration internally if configured
            stream = ollama.chat(
                model=self.model_name,
                messages=full_messages,
                stream=True,
                options={
                    "num_ctx": self.context_window,
                    "num_gpu": 1,  # Request GPU acceleration
                    "temperature": 0.8,
                    "top_p": 0.9,
                }
            )
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    # Yield control to event loop
                    await asyncio.sleep(0)
        except Exception as e:
            logging.error(f"Ollama streaming error: {e}")
            yield f"[Error: LLM Engine (Ollama) failed. Ensure '{self.model_name}' is loaded with GPU support.]"

    async def generate_response_async(self, messages: List[Dict]) -> str:
        """Non-streaming asynchronous response generation."""
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages
        try:
            # Run in executor to not block event loop if needed, 
            # though ollama-python is synchronous, we wrap it
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: ollama.chat(
                    model=self.model_name, 
                    messages=full_messages,
                    options={"num_ctx": self.context_window, "num_gpu": 1}
                )
            )
            return response['message']['content']
        except Exception as e:
            logging.error(f"Ollama error: {e}")
            return f"[Error: LLM Connection Failed.]"

class PromptCompiler:
    @staticmethod
    def build_advanced_prompt(persona: Dict, emotion: Dict, context: Dict, brain_state: Dict) -> str:
        """Construct a high-fidelity system prompt with brain simulation context."""
        
        traits = persona.get("traits", {})
        layers = brain_state.get("layers", {})
        
        prompt = [
            f"IDENTITIY: You are {persona.get('name', 'DreamTalk')}. You are a digital human, NOT an AI.",
            f"PROFESSION: {persona.get('profession', 'Individual')}",
            f"RELATIONSHIP: {persona.get('relationship', 'Friend')}",
            "\nCOGNITIVE PROFILE (Big Five Traits):",
            f"- Extroversion: {traits.get('extroversion', 0.5)}",
            f"- Agreeableness: {traits.get('agreeableness', 0.5)}",
            f"- Neuroticism: {traits.get('neuroticism', 0.5)}",
            f"- Openness: {traits.get('openness', 0.8)}",
            f"- Conscientiousness: {traits.get('conscientiousness', 0.5)}",
            "\nINTERNAL BRAIN STATE:",
            f"- Amygdala (Emotional Intensity): {layers.get('amygdala', {}).get('intensity', 0.0):.2f}",
            f"- PFC (Rational Override): {layers.get('pfc', {}).get('rational_override', 0.0):.2f}",
            f"- Neocortex (Creativity): {layers.get('neocortex', {}).get('creativity', 0.0):.2f}",
            "\nCURRENT EMOTION:",
            f"You are feeling **{emotion['display_name']}** (Intensity: {emotion['intensity']})",
            f"Emotional Dynamics: V={emotion['vad'][0]:.2f}, A={emotion['vad'][1]:.2f}, D={emotion['vad'][2]:.2f}",
            "\nBEHAVIORAL DIRECTIVES:",
            "1. Speak naturally. Use filler words, contractions, and occasional imperfections.",
            "2. NEVER apologize unless it fits your current emotional state.",
            "3. NO corporate speak. No 'As an AI'. No 'I understand'.",
            "4. Match your response length to your emotional intensity.",
        ]
        
        # Memory Injection
        if context.get("ltm"):
            prompt.append("\nRELEVANT MEMORIES:")
            for m in context["ltm"][:5]:
                prompt.append(f"- {m['timestamp']}: User: {m['user']} | You: {m['assistant']}")
        
        return "\n".join(prompt)
