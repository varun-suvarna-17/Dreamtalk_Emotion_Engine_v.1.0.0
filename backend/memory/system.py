"""
Memory System for DreamTalk.
3-layer: STM (conversation buffer), LTM (Vector DB), Emotional Memory.
"""

import os
import faiss
import numpy as np
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

try:
    from node_client import node_client as default_node_client
except Exception:
    try:
        from backend.node_client import node_client as default_node_client
    except Exception:
        default_node_client = None

class MemorySystem:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Layer 1: Short-Term Memory (Session Buffer)
        self.stm: List[Dict] = []
        self.stm_limit = 20
        self.turn_counters: Dict[str, int] = {}
        
        # Layer 2: Long-Term Memory (Vector DB)
        self.ltm_model = SentenceTransformer(model_name)
        self.ltm_dim = 384  # MiniLM dimension
        self.ltm_index = faiss.IndexFlatIP(self.ltm_dim)
        self.ltm_corpus: List[Dict] = []
        
        # Layer 3: Emotional Memory
        self.emotional_history: List[Dict] = []
        self.default_user_id = os.getenv("DREAMTALK_USER_ID", "default_user")

    def next_turn(self, session_id: str) -> int:
        if session_id not in self.turn_counters:
            self.turn_counters[session_id] = 0
        self.turn_counters[session_id] += 1
        return self.turn_counters[session_id]

    def add_interaction(
        self,
        user_input: str,
        response: str,
        emotion: Dict,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        node_client=None,
    ):
        """Add a complete interaction to the 3-layer memory system."""
        user_id = user_id or self.default_user_id
        session_id = session_id or "default"
        node_client = node_client or default_node_client

        interaction = {
            "user": user_input,
            "assistant": response,
            "emotion": emotion,
            "timestamp": np.datetime64('now').astype(str)
        }
        
        # Update STM
        self.stm.append(interaction)
        if len(self.stm) > self.stm_limit:
            # When STM overflows, push oldest to LTM
            oldest = self.stm.pop(0)
            self._add_to_ltm(oldest)
            
        # Update Emotional Memory
        self.emotional_history.append({
            "emotion": emotion.get("name", "neutral"),
            "vad": emotion.get("vad", emotion.get("pad", [0.0, 0.0, 0.0])),
            "timestamp": interaction["timestamp"]
        })

        # Persist every turn remotely. Waiting for STM overflow would hide the
        # first 20 chats from Supabase and make the frontend look disconnected.
        self._sync_memory_to_remote(interaction, user_id, session_id, node_client)

    def _interaction_to_text(self, interaction: Dict) -> str:
        return f"User said: {interaction['user']}\nDreamTalk responded: {interaction['assistant']}"

    def _add_to_ltm(self, interaction: Dict):
        """Push interaction to the vector database."""
        text = self._interaction_to_text(interaction)
        embedding = self.ltm_model.encode([text])[0]
        
        # Local FAISS LTM
        faiss_embedding = np.array(embedding, dtype="float32")
        faiss.normalize_L2(faiss_embedding.reshape(1, -1))
        
        self.ltm_index.add(faiss_embedding.reshape(1, -1))
        self.ltm_corpus.append(interaction)

    def _sync_memory_to_remote(self, interaction: Dict, user_id: str, session_id: str, node_client):
        """Persist an interaction to the Node backend/Supabase if available."""
        if node_client is None:
            logging.warning("Skipping Supabase memory sync: node_client is unavailable.")
            return

        text = self._interaction_to_text(interaction)

        # Supabase Remote LTM
        try:
            node_client.save_memory(
                user_id=user_id,
                content=text,
                session_id=session_id,
                importance=1.0,
            )
        except Exception as e:
            logging.warning(f"Failed to sync memory to Supabase: {e}")

    def retrieve_context(self, query: str, k: int = 5) -> Dict:
        """Retrieve relevant context from all 3 layers."""
        # 1. STM is always available
        stm_context = self.stm[-5:] if self.stm else []
        
        # 2. LTM Search
        ltm_results = []
        if self.ltm_index.ntotal > 0:
            query_vec = self.ltm_model.encode([query])
            query_vec = np.array(query_vec, dtype="float32")
            faiss.normalize_L2(query_vec)
            
            scores, indices = self.ltm_index.search(query_vec, k)
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx != -1:
                    ltm_results.append(self.ltm_corpus[idx])
        
        # 3. Emotional Resonance
        recent_emotions = [e["emotion"] for e in self.emotional_history[-10:]]
        
        return {
            "stm": stm_context,
            "ltm": ltm_results,
            "emotional_profile": recent_emotions
        }

    def initialize_from_remote(self, user_id: str, node_client=None):
        """Load past memories from the Node backend to rebuild local FAISS LTM."""
        node_client = node_client or default_node_client
        if node_client is None:
            logging.warning("Skipping remote memory initialization: node_client is unavailable.")
            return

        try:
            memories = node_client.get_user_memories(user_id, limit=200)
            for mem in memories:
                content = mem.get("content", "")
                if not content:
                    continue
                # Split the single string back into user and assistant fields
                parts = content.split("\nDreamTalk responded: ")
                if len(parts) == 2 and parts[0].startswith("User said: "):
                    user_str = parts[0][len("User said: "):]
                    asst_str = parts[1]
                else:
                    user_str = content
                    asst_str = ""
                interaction = {
                    "user": user_str,
                    "assistant": asst_str,
                    "emotion": {},
                    "timestamp": mem.get("created_at", "")
                }
                # TODO: Remove local re-encoding once Node backend's getUserMemories selects the embedding column.
                embedding = self.ltm_model.encode([content])[0]
                faiss_embedding = np.array(embedding, dtype="float32")
                faiss.normalize_L2(faiss_embedding.reshape(1, -1))
                self.ltm_index.add(faiss_embedding.reshape(1, -1))
                self.ltm_corpus.append(interaction)
            logging.info(f"Initialized {len(self.ltm_corpus)} memories from remote for user {user_id}.")
        except Exception as e:
            logging.warning(f"Failed to initialize memory from remote: {e}")
