"""
Brain Module Backend for DreamTalk.
Standalone system focused on Thinking, Emotion, Personality, and Memory.
"""

from fastapi import BackgroundTasks
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import uvicorn
import sys
import os
import asyncio
from dotenv import load_dotenv

# Ensure all modules are in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from emotion.engine import PADEmotionEngine
from memory.system import MemorySystem
from models.brain import NeuralBrainSimulation, BigFiveTraits
from llm.service import LLMService, PromptCompiler

app = FastAPI(title="DreamTalk Brain Module API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Cognitive Modules
emotion_engine = PADEmotionEngine(inertia=0.85)
memory_system = MemorySystem()
brain_sim = NeuralBrainSimulation()
llm_service = LLMService()  # Provider & model read from .env (auto-failover: Groq → Ollama)

# Persistent Global Persona
persona = {
    "name": "Alex",
    "profession": "Software Architect",
    "relationship": "Friend",
    "tone": "casual",
    "traits": {
        "extroversion": 0.6,
        "agreeableness": 0.7,
        "neuroticism": 0.3,
        "openness": 0.9,
        "conscientiousness": 0.8
    }
}

class ChatRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = "default"

class PersonaUpdate(BaseModel):
    name: Optional[str]
    profession: Optional[str]
    relationship: Optional[str]
    tone: Optional[str]
    traits: Optional[Dict[str, float]]

@app.post("/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    try:
        # 1. Analyze input -> PAD Stimulus
        # Simulating sentiment analysis for the stimulus
        sentiment_score = 0.0 # This would be replaced by a real sentiment model
        stimulus = emotion_engine.stimulus_from_sentiment(sentiment_score)

        # 2. Update Emotional State
        current_emotion = emotion_engine.update(stimulus)

        # 3. Retrieve Context from 3-layer Memory
        context = memory_system.retrieve_context(request.user_input)

        # 4. Neural Brain Decision
        decision = brain_sim.process_decision(request.user_input, current_emotion, context)

        # 5. Compile Advanced Personality-Driven Prompt
        system_prompt = PromptCompiler.build_advanced_prompt(
            persona, current_emotion, context, decision
        )
        llm_service.set_system_prompt(system_prompt)

        # 6. Fix 2 — Inject STM history so the LLM remembers the conversation
        # Format: [system] + [stm turns as user/assistant pairs] + [current user turn]
        stm_messages: List[Dict] = []
        for turn in context.get("stm", []):
            if turn.get("user"):
                stm_messages.append({"role": "user",      "content": turn["user"]})
            if turn.get("assistant"):
                stm_messages.append({"role": "assistant", "content": turn["assistant"]})

        messages = stm_messages + [{"role": "user", "content": request.user_input}]
        response = await llm_service.generate_response_async(messages)

        # 7. Update Memory with the new interaction
        memory_system.add_interaction(request.user_input, response, current_emotion)
        
        return {
            "response": response,
            "emotion": current_emotion,
            "brain_state": decision["layers"],
            "delay_ms": decision["delay_ms"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/configure")
async def configure(update: PersonaUpdate):
    global persona
    if update.name: persona["name"] = update.name
    if update.profession: persona["profession"] = update.profession
    if update.relationship: persona["relationship"] = update.relationship
    if update.tone: persona["tone"] = update.tone
    if update.traits:
        persona["traits"].update(update.traits)
        new_traits = BigFiveTraits(**persona["traits"])
        brain_sim.update_traits(new_traits)
    return {"status": "success", "persona": persona}

@app.get("/memory")
async def get_memory():
    return {
        "stm": memory_system.stm[-10:],
        "ltm_count": memory_system.ltm_index.ntotal,
        "emotional_history": [e["emotion"] for e in memory_system.emotional_history[-20:]]
    }

@app.get("/emotion")
async def get_emotion():
    return emotion_engine.get_current_emotion()

@app.get("/health")
async def health():
    return {"status": "online", "module": "brain_module"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
