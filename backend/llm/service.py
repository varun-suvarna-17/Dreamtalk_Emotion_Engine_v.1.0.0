"""
High-Performance LLM Service for DreamTalk v3.5.
Supports Groq Cloud (LLaMA-3, Mixtral) and Ollama (local LLaMA-3).
Provider is selected via LLM_PROVIDER env variable: 'groq' | 'ollama'
Automatic failover: if Groq is unavailable, falls back to Ollama seamlessly.
"""

import os
import logging
import asyncio
from typing import List, Dict, AsyncGenerator

from groq import AsyncGroq
import ollama as _ollama  # official ollama python client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """
    Dual-provider LLM service with automatic failover.

    Set LLM_PROVIDER=groq  in .env  →  primary: Groq Cloud, fallback: Ollama
    Set LLM_PROVIDER=ollama in .env →  Ollama only (no failover)

    If the primary provider (Groq) fails at runtime, the service automatically
    retries the same request through Ollama and stays on Ollama for subsequent
    calls until you explicitly reset via switch_provider().
    """

    def __init__(self, model_name: str = None):
        self.preferred_provider = os.environ.get("LLM_PROVIDER", "groq").strip().lower()
        self.active_provider = self.preferred_provider  # can change at runtime
        self.system_prompt = ""

        # --- Always prepare the Groq client (if key exists) ---
        groq_key = os.environ.get("GROQ_API_KEY") or os.environ.get("API_KEY")
        self.groq_model = model_name or os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        self.groq_client = AsyncGroq(api_key=groq_key) if groq_key else None

        # --- Always prepare the Ollama model name ---
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3")

        if self.preferred_provider not in ("groq", "ollama"):
            raise ValueError(
                f"Unknown LLM_PROVIDER='{self.preferred_provider}'. Must be 'groq' or 'ollama'."
            )

        logger.info(
            f"[LLMService] Primary: {self.preferred_provider} | "
            f"Groq model: {self.groq_model} | Ollama model: {self.ollama_model}"
        )

    # ------------------------------------------------------------------
    # Provider management
    # ------------------------------------------------------------------
    def set_system_prompt(self, prompt: str):
        self.system_prompt = prompt

    def switch_provider(self, provider: str):
        """Manually switch the active provider at runtime."""
        provider = provider.strip().lower()
        if provider not in ("groq", "ollama"):
            raise ValueError(f"Invalid provider '{provider}'. Use 'groq' or 'ollama'.")
        self.active_provider = provider
        logger.info(f"[LLMService] Active provider switched to: {self.active_provider}")

    def reset_provider(self):
        """Reset back to the preferred (env-configured) provider."""
        self.active_provider = self.preferred_provider
        logger.info(f"[LLMService] Provider reset to preferred: {self.active_provider}")

    # ------------------------------------------------------------------
    # Internal helpers per provider
    # ------------------------------------------------------------------
    async def _generate_groq(self, messages: List[Dict]) -> str:
        """Non-streaming call via Groq Cloud. Raises on failure."""
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages
        response = await self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=full_messages,
            temperature=0.8,
            top_p=0.9,
        )
        return response.choices[0].message.content

    async def _generate_ollama(self, messages: List[Dict]) -> str:
        """Non-streaming call via local Ollama daemon (runs sync client in thread)."""
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        def _sync_call():
            response = _ollama.chat(
                model=self.ollama_model,
                messages=full_messages,
            )
            return response["message"]["content"]

        return await asyncio.get_event_loop().run_in_executor(None, _sync_call)

    async def _stream_groq(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """Streaming call via Groq Cloud. Raises on failure."""
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages
        stream = await self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=full_messages,
            stream=True,
            temperature=0.8,
            top_p=0.9,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    # ------------------------------------------------------------------
    # Public API  (called by main.py)
    # ------------------------------------------------------------------
    async def generate_response_async(self, messages: List[Dict]) -> str:
        """
        Non-streaming response with automatic failover.
        Groq failure → logs warning → retries via Ollama → stays on Ollama.
        """
        if self.active_provider == "groq":
            try:
                return await self._generate_groq(messages)
            except Exception as e:
                logger.warning(
                    f"[LLMService] ⚠ Groq API unavailable ({e}). "
                    f"Switching to Ollama ({self.ollama_model})..."
                )
                self.active_provider = "ollama"
                # Fall through to Ollama below

        # --- Ollama path (primary or failover) ---
        try:
            return await self._generate_ollama(messages)
        except Exception as e:
            logger.error(f"[LLMService] ✘ Ollama also failed: {e}")
            return (
                "[Error: Both Groq and Ollama are unavailable. "
                "Check your API key / Ollama daemon and try again.]"
            )

    async def generate_streaming(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """
        Streaming response with automatic failover.
        Groq failure → falls back to a single-chunk Ollama response.
        """
        if self.active_provider == "groq":
            try:
                async for token in self._stream_groq(messages):
                    yield token
                return  # success — done
            except Exception as e:
                logger.warning(
                    f"[LLMService] ⚠ Groq streaming unavailable ({e}). "
                    f"Falling back to Ollama ({self.ollama_model})..."
                )
                self.active_provider = "ollama"

        # --- Ollama fallback (yield full response as one chunk) ---
        try:
            result = await self._generate_ollama(messages)
            yield result
        except Exception as e:
            logger.error(f"[LLMService] ✘ Ollama also failed: {e}")
            yield "[Error: Both Groq and Ollama are unavailable.]"
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
