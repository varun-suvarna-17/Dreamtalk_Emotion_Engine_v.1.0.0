"""
Brain Module Backend for DreamTalk. 
Multi-tenant system focused on Thinking, Emotion, Personality, and Memory.
"""

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import logging
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import uvicorn

# Ensure all modules are in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)

from emotion.engine import PADEmotionEngine
from memory.system import MemorySystem
from models.brain import BigFiveTraits, NeuralBrainSimulation
from llm.service import LLMService, PromptCompiler

try:
    from supabase import create_client
except Exception:
    create_client = None

logger = logging.getLogger(__name__)

DEFAULT_USER_ID = "default_user"
DEFAULT_AVATAR_ID = "default_avatar"

DEFAULT_PERSONA = {
    "name": "Alex",
    "profession": "Software Architect",
    "relationship": "Friend",
    "tone": "casual",
    "traits": {
        "extroversion": 0.6,
        "agreeableness": 0.7,
        "neuroticism": 0.3,
        "openness": 0.9,
        "conscientiousness": 0.8,
    },
}

app = FastAPI(title="DreamTalk Brain Module API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class AvatarRuntime:
    emotion_engine: PADEmotionEngine
    memory_system: MemorySystem
    brain_sim: NeuralBrainSimulation
    llm_service: LLMService


class ChatRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = DEFAULT_USER_ID
    avatar_id: Optional[str] = DEFAULT_AVATAR_ID


class PersonaUpdate(BaseModel):
    user_id: Optional[str] = DEFAULT_USER_ID
    avatar_id: Optional[str] = DEFAULT_AVATAR_ID
    name: Optional[str] = None
    profession: Optional[str] = None
    relationship: Optional[str] = None
    tone: Optional[str] = None
    traits: Optional[Dict[str, float]] = None


avatar_runtime_cache: Dict[Tuple[str, str], AvatarRuntime] = {}
sentiment_analyzer = SentimentIntensityAnalyzer()


def create_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SECRET_KEY")

    if not supabase_url or not supabase_key:
        logger.warning("Supabase disabled: SUPABASE_URL or SUPABASE_KEY is missing.")
        return None

    if create_client is None:
        logger.warning("Supabase disabled: supabase-py is not installed.")
        return None

    try:
        return create_client(supabase_url, supabase_key)
    except Exception as exc:
        logger.warning("Supabase client initialization failed: %s", exc)
        return None


supabase = create_supabase_client()


def tenant_key(user_id: Optional[str], avatar_id: Optional[str]) -> Tuple[str, str]:
    return user_id or DEFAULT_USER_ID, avatar_id or DEFAULT_AVATAR_ID


def scoped_session_id(avatar_id: str, session_id: Optional[str]) -> str:
    return f"{avatar_id}:{session_id or 'default'}"


def get_avatar_runtime(user_id: str, avatar_id: str) -> AvatarRuntime:
    key = (user_id, avatar_id)
    if key not in avatar_runtime_cache:
        memory_system = MemorySystem()
        memory_system.default_user_id = user_id
        avatar_runtime_cache[key] = AvatarRuntime(
            emotion_engine=PADEmotionEngine(inertia=0.85),
            memory_system=memory_system,
            brain_sim=NeuralBrainSimulation(),
            llm_service=LLMService(),
        )
    return avatar_runtime_cache[key]


def fetch_avatar_persona(user_id: str, avatar_id: str) -> Dict:
    persona = deepcopy(DEFAULT_PERSONA)
    if supabase is None:
        return persona

    try:
        result = (
            supabase.table("avatar_config")
            .select("*")
            .eq("user_id", user_id)
            .eq("avatar_id", avatar_id)
            .limit(1)
            .execute()
        )
        rows = result.data or []
        if not rows:
            return persona

        row = rows[0]
        persona["name"] = row.get("name") or persona["name"]
        persona["profession"] = row.get("profession") or persona["profession"]
        persona["relationship"] = row.get("relationship") or persona["relationship"]
        persona["tone"] = row.get("tone") or persona["tone"]
        if isinstance(row.get("traits"), dict):
            persona["traits"].update(row["traits"])
    except Exception as exc:
        logger.warning("Failed to fetch avatar config from Supabase: %s", exc)

    return persona


def save_avatar_persona(user_id: str, avatar_id: str, persona: Dict) -> None:
    if supabase is None:
        return

    try:
        supabase.table("avatar_config").upsert(
            {
                "user_id": user_id,
                "avatar_id": avatar_id,
                "name": persona.get("name"),
                "profession": persona.get("profession"),
                "relationship": persona.get("relationship"),
                "tone": persona.get("tone"),
                "traits": persona.get("traits", {}),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            on_conflict="user_id,avatar_id",
        ).execute()
    except Exception as exc:
        logger.warning("Failed to save avatar config to Supabase: %s", exc)


def save_brain_output(
    user_id: str,
    avatar_id: str,
    session_id: str,
    turn_id: int,
    response_text: str,
    current_emotion: Dict,
) -> None:
    if supabase is None:
        return

    try:
        supabase.table("brain_output").insert(
            {
                "user_id": user_id,
                "avatar_id": avatar_id,
                "session_id": session_id,
                "turn_id": turn_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "response_text": response_text,
                "sentiment_emotion": current_emotion,
            }
        ).execute()
    except Exception as exc:
        logger.warning("Failed to save brain output to Supabase: %s", exc)


def apply_traits_to_brain(runtime: AvatarRuntime, persona: Dict) -> None:
    try:
        runtime.brain_sim.update_traits(BigFiveTraits(**persona["traits"]))
    except Exception as exc:
        logger.warning("Failed to apply avatar traits: %s", exc)


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_id, avatar_id = tenant_key(request.user_id, request.avatar_id)
        runtime = get_avatar_runtime(user_id, avatar_id)
        persona = fetch_avatar_persona(user_id, avatar_id)
        apply_traits_to_brain(runtime, persona)

        sentiment_score = sentiment_analyzer.polarity_scores(request.user_input)["compound"]
        stimulus = runtime.emotion_engine.stimulus_from_sentiment(sentiment_score)
        current_emotion = runtime.emotion_engine.update(stimulus)

        context = runtime.memory_system.retrieve_context(request.user_input)
        decision = runtime.brain_sim.process_decision(
            request.user_input,
            current_emotion,
            context,
        )

        system_prompt = PromptCompiler.build_advanced_prompt(
            persona,
            current_emotion,
            context,
            decision,
        )
        runtime.llm_service.set_system_prompt(system_prompt)

        stm_messages: List[Dict] = []
        for turn in context.get("stm", []):
            if turn.get("user"):
                stm_messages.append({"role": "user", "content": turn["user"]})
            if turn.get("assistant"):
                stm_messages.append({"role": "assistant", "content": turn["assistant"]})

        messages = stm_messages + [{"role": "user", "content": request.user_input}]
        response = await runtime.llm_service.generate_response_async(messages)

        scoped_id = scoped_session_id(avatar_id, request.session_id)
        turn_id = runtime.memory_system.next_turn(scoped_id)
        runtime.memory_system.add_interaction(
            request.user_input,
            response,
            current_emotion,
            user_id=user_id,
            avatar_id=avatar_id,
            session_id=scoped_id,
        )

        save_brain_output(
            user_id=user_id,
            avatar_id=avatar_id,
            session_id=request.session_id or "default",
            turn_id=turn_id,
            response_text=response,
            current_emotion=current_emotion,
        )

        return {
            "user_id": user_id,
            "avatar_id": avatar_id,
            "session_id": request.session_id or "default",
            "turn_id": turn_id,
            "response": response,
            "emotion": current_emotion,
            "brain_state": decision["layers"],
            "delay_ms": decision["delay_ms"],
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/configure")
async def configure(update: PersonaUpdate):
    user_id, avatar_id = tenant_key(update.user_id, update.avatar_id)
    runtime = get_avatar_runtime(user_id, avatar_id)
    persona = fetch_avatar_persona(user_id, avatar_id)

    if update.name is not None:
        persona["name"] = update.name
    if update.profession is not None:
        persona["profession"] = update.profession
    if update.relationship is not None:
        persona["relationship"] = update.relationship
    if update.tone is not None:
        persona["tone"] = update.tone
    if update.traits:
        persona["traits"].update(update.traits)

    apply_traits_to_brain(runtime, persona)
    save_avatar_persona(user_id, avatar_id, persona)

    return {
        "status": "success",
        "user_id": user_id,
        "avatar_id": avatar_id,
        "persona": persona,
    }


@app.get("/memory")
async def get_memory(
    user_id: str = Query(DEFAULT_USER_ID),
    avatar_id: str = Query(DEFAULT_AVATAR_ID),
):
    user_id, avatar_id = tenant_key(user_id, avatar_id)
    runtime = get_avatar_runtime(user_id, avatar_id)
    return {
        "user_id": user_id,
        "avatar_id": avatar_id,
        "stm": runtime.memory_system.stm[-10:],
        "ltm_count": runtime.memory_system.ltm_index.ntotal,
        "emotional_history": [
            e["emotion"] for e in runtime.memory_system.emotional_history[-20:]
        ],
    }


@app.get("/emotion")
async def get_emotion(
    user_id: str = Query(DEFAULT_USER_ID),
    avatar_id: str = Query(DEFAULT_AVATAR_ID),
):
    user_id, avatar_id = tenant_key(user_id, avatar_id)
    runtime = get_avatar_runtime(user_id, avatar_id)
    return {
        "user_id": user_id,
        "avatar_id": avatar_id,
        "emotion": runtime.emotion_engine.get_current_emotion(),
    }


@app.get("/health")
async def health():
    return {
        "status": "online",
        "module": "brain_module",
        "multi_tenant": True,
        "supabase_enabled": supabase is not None,
        "active_avatar_runtimes": len(avatar_runtime_cache),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
