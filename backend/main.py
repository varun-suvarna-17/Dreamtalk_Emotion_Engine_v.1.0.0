"""
Brain Module Backend for DreamTalk.
Standalone system focused on Thinking, Emotion, Personality, and Memory.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import uvicorn
import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

# Sentiment analyser (shared instance — lightweight, thread-safe)
_vader = SentimentIntensityAnalyzer()

# Ensure all modules are in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from emotion.engine import PADEmotionEngine
from memory.system import MemorySystem
from models.brain import NeuralBrainSimulation, BigFiveTraits
from llm.service import LLMService, PromptCompiler
from node_client import node_client

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"  # TODO: replace with real auth

# ---------------------------------------------------------------------------
# Fix 3 — FastAPI lifespan (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load memory on startup; persist it incrementally."""
    try:
        memory_system.initialize_from_remote(DEFAULT_USER_ID, node_client)
    except Exception as e:
        logging.warning(f"Failed to initialize memory from remote on startup: {e}")
    yield
    # Removed memory_system.save() as persistence happens incrementally now

app = FastAPI(title="DreamTalk Brain Module API", lifespan=lifespan)

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
        session_id = request.session_id
        if not session_id or session_id == "default":
            try:
                session_data = node_client.start_session(user_id=DEFAULT_USER_ID, scenario_name="general_chat")
                session_id = session_data["id"]
            except Exception as e:
                logging.warning(f"Failed to start session via node_client: {e}")
                session_id = "default"
                
        turn_index = memory_system.next_turn(session_id)

        # 1. Fix 1 — Dynamic VADER sentiment → PAD Stimulus
        scores = _vader.polarity_scores(request.user_input)
        sentiment_score = scores["compound"]  # Range: -1.0 (very negative) to +1.0 (very positive)
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
        memory_system.add_interaction(
            request.user_input, 
            response, 
            current_emotion,
            DEFAULT_USER_ID,
            session_id,
            node_client
        )
        
        # 8. Background Tasks for Supabase syncing
        def sync_to_supabase():
            try:
                node_client.save_message(
                    session_id=session_id,
                    user_id=DEFAULT_USER_ID,
                    turn_index=turn_index,
                    user_content=request.user_input,
                    assistant_content=response
                )
            except Exception as e:
                logging.warning(f"Failed to save message: {e}")
                
            try:
                node_client.save_pad_snapshot(
                    session_id=session_id,
                    user_id=DEFAULT_USER_ID,
                    turn_index=turn_index,
                    pleasure=current_emotion["pad"][0],
                    arousal=current_emotion["pad"][1],
                    dominance=current_emotion["pad"][2]
                )
            except Exception as e:
                logging.warning(f"Failed to save PAD snapshot: {e}")
                
            try:
                node_client.log_emotion(
                    session_id=session_id,
                    user_id=DEFAULT_USER_ID,
                    turn_index=turn_index,
                    user_pleasure=sentiment_score,
                    user_arousal=abs(sentiment_score),
                    pad_pleasure=current_emotion["pad"][0],
                    pad_arousal=current_emotion["pad"][1],
                    pad_dominance=current_emotion["pad"][2],
                    emotion_label=current_emotion["name"],
                    memory_action="USE_STM",
                    response_style="default",
                    inertia_strength=emotion_engine.inertia,
                    reward=0.0,
                    verdict="N/A",
                    relationship_delta=0.0
                )
            except Exception as e:
                logging.warning(f"Failed to log emotion: {e}")

        background_tasks.add_task(sync_to_supabase)

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
