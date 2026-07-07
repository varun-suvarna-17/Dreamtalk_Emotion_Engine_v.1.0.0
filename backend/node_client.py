"""
python/node_client.py
HTTP client for the DreamTalk brain module to communicate with
the Node.js/Express backend, which writes to Supabase.

Usage: instantiate NodeClient once at brain startup, then call
       its methods from server/app.py after each /reset and /step.

All methods raise NodeClientError on failure so the brain can
decide whether to continue the episode or abort.

Environment variables:
    NODE_BACKEND_URL  — default: http://localhost:3000
    BRAIN_API_KEY     — shared secret, must match Node.js .env
"""

import os
import requests
from typing import Optional

NODE_BACKEND_URL = os.getenv("NODE_BACKEND_URL", "http://localhost:3000")
BRAIN_API_KEY    = os.getenv("BRAIN_API_KEY", "")
TIMEOUT          = 10   # seconds


class NodeClientError(Exception):
    pass


class NodeClient:
    """
    Thin wrapper around the Node.js /api/brain/* endpoints.
    One instance lives for the lifetime of the FastAPI process.
    """

    def __init__(self):
        self._base = NODE_BACKEND_URL.rstrip("/") + "/api/brain"
        self._headers = {
            "Content-Type":    "application/json",
            "X-Brain-Api-Key": BRAIN_API_KEY,
        }

    def _post(self, path: str, body: dict) -> dict:
        url = f"{self._base}{path}"
        try:
            r = requests.post(url, json=body, headers=self._headers, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            raise NodeClientError(f"POST {path} failed: {e}")

    def _get(self, path: str, params: dict = None) -> dict:
        url = f"{self._base}{path}"
        try:
            r = requests.get(url, params=params, headers=self._headers, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            raise NodeClientError(f"GET {path} failed: {e}")

    def _patch(self, path: str) -> dict:
        url = f"{self._base}{path}"
        try:
            r = requests.patch(url, headers=self._headers, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.RequestException as e:
            raise NodeClientError(f"PATCH {path} failed: {e}")

    # ── Sessions ──────────────────────────────────────────────────────────────

    def start_session(self, user_id: str, scenario_name: str = None) -> dict:
        """
        Call after /reset. Returns the new session row including session_id.
        """
        data = self._post("/sessions/start", {
            "user_id":       user_id,
            "scenario_name": scenario_name,
        })
        return data["session"]

    def close_session(
        self,
        session_id:               str,
        total_turns:              int,
        final_relationship_score: float,
        cumulative_reward:        float,
    ) -> dict:
        """
        Call when episode done=True.
        """
        data = self._post("/sessions/close", {
            "session_id":               session_id,
            "total_turns":              total_turns,
            "final_relationship_score": final_relationship_score,
            "cumulative_reward":        cumulative_reward,
        })
        return data["session"]

    def save_message(
        self,
        session_id:        str,
        user_id:           str,
        turn_index:        int,
        user_content:      str,
        assistant_content: str,
    ) -> None:
        """
        Call after each /step to persist the message pair.
        """
        self._post("/sessions/message", {
            "session_id":        session_id,
            "user_id":           user_id,
            "turn_index":        turn_index,
            "user_content":      user_content,
            "assistant_content": assistant_content,
        })

    def get_user_sessions(self, user_id: str, limit: int = 20) -> list:
        data = self._get(f"/sessions/user/{user_id}", {"limit": limit})
        return data["sessions"]

    # ── Emotion Logs ──────────────────────────────────────────────────────────

    def log_emotion(
        self,
        session_id:        str,
        user_id:           str,
        turn_index:        int,
        user_pleasure:     float,
        user_arousal:      float,
        pad_pleasure:      float,
        pad_arousal:       float,
        pad_dominance:     float,
        emotion_label:     str,
        memory_action:     str,
        response_style:    str,
        inertia_strength:  float,
        reward:            float,
        verdict:           str,
        relationship_delta: float,
    ) -> dict:
        """
        Call after every /step alongside save_message.
        """
        data = self._post("/emotion/log", {
            "session_id":        session_id,
            "user_id":           user_id,
            "turn_index":        turn_index,
            "user_pleasure":     user_pleasure,
            "user_arousal":      user_arousal,
            "pad_pleasure":      pad_pleasure,
            "pad_arousal":       pad_arousal,
            "pad_dominance":     pad_dominance,
            "emotion_label":     emotion_label,
            "memory_action":     memory_action,
            "response_style":    response_style,
            "inertia_strength":  inertia_strength,
            "reward":            reward,
            "verdict":           verdict,
            "relationship_delta": relationship_delta,
        })
        return data["log"]

    def get_emotion_history(self, user_id: str, limit: int = 50) -> list:
        """Used by QUERY_EMOTIONAL_HISTORY meta-action."""
        data = self._get(f"/emotion/history/{user_id}", {"limit": limit})
        return data["history"]

    def get_verdict_summary(self, user_id: str) -> dict:
        data = self._get(f"/emotion/summary/{user_id}")
        return data["summary"]

    # ── Relationship Scores ───────────────────────────────────────────────────

    def upsert_relationship_score(
        self,
        user_id:         str,
        score:           float,
        total_sessions:  int   = 0,
        total_turns:     int   = 0,
        miss_count:      int   = 0,
        overreact_count: int   = 0,
        avg_reward:      float = 0.0,
    ) -> dict:
        """Call at the end of each session."""
        data = self._post("/emotion/relationship", {
            "user_id":         user_id,
            "score":           score,
            "total_sessions":  total_sessions,
            "total_turns":     total_turns,
            "miss_count":      miss_count,
            "overreact_count": overreact_count,
            "avg_reward":      avg_reward,
        })
        return data["record"]

    def get_relationship_score(self, user_id: str) -> dict:
        """Used by CHECK_RELATIONSHIP_SCORE meta-action."""
        data = self._get(f"/emotion/relationship/{user_id}")
        return data["score"]

    # ── PAD Snapshots ─────────────────────────────────────────────────────────

    def save_pad_snapshot(
        self,
        session_id:  str,
        user_id:     str,
        turn_index:  int,
        pleasure:    float,
        arousal:     float,
        dominance:   float,
    ) -> None:
        self._post("/emotion/pad-snapshot", {
            "session_id": session_id,
            "user_id":    user_id,
            "turn_index": turn_index,
            "pleasure":   pleasure,
            "arousal":    arousal,
            "dominance":  dominance,
        })

    def get_pad_arc(self, session_id: str) -> list:
        data = self._get(f"/emotion/pad-arc/{session_id}")
        return data["arc"]

    # ── Memory ────────────────────────────────────────────────────────────────

    def save_memory(
        self,
        user_id:    str,
        content:    str,
        session_id: Optional[str] = None,
        importance: float         = 1.0,
    ) -> dict:
        data = self._post("/memory", {
            "user_id":    user_id,
            "content":    content,
            "session_id": session_id,
            "importance": importance,
        })
        return data["memory"]

    def get_user_memories(self, user_id: str, limit: int = 100) -> list:
        """
        Call on session start to warm up FAISS with persisted memories.
        Returns list of {id, content, importance} dicts.
        """
        data = self._get(f"/memory/{user_id}", {"limit": limit})
        return data["memories"]

    def touch_memory(self, memory_id: str) -> None:
        self._patch(f"/memory/{memory_id}/touch")


# ── Singleton ─────────────────────────────────────────────────────────────────
# Import this instance in your Python brain code:
#   from backend.node_client import node_client
node_client = NodeClient()
