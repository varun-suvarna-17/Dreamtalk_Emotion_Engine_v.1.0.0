"""
Memory System for DreamTalk.
3-layer: STM (conversation buffer), LTM (Vector DB), Emotional Memory.
"""

import os
import json
import faiss
import numpy as np
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

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
        
        # Persistent storage paths
        self.base_path = "data/memory"
        os.makedirs(self.base_path, exist_ok=True)

    def next_turn(self, session_id: str) -> int:
        if session_id not in self.turn_counters:
            self.turn_counters[session_id] = 0
        self.turn_counters[session_id] += 1
        return self.turn_counters[session_id]

    def add_interaction(self, user_input: str, response: str, emotion: Dict, user_id: str, session_id: str, node_client):
        """Add a complete interaction to the 3-layer memory system."""
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
            self._add_to_ltm(oldest, user_id, session_id, node_client)
            
        # Update Emotional Memory
        self.emotional_history.append({
            "emotion": emotion["name"],
            "vad": emotion["vad"],
            "timestamp": interaction["timestamp"]
        })

    def _add_to_ltm(self, interaction: Dict, user_id: str, session_id: str, node_client):
        """Push interaction to the vector database."""
        text = f"User said: {interaction['user']}\nDreamTalk responded: {interaction['assistant']}"
        embedding = self.ltm_model.encode([text])[0]
        
        # Local FAISS LTM
        faiss_embedding = np.array(embedding, dtype="float32")
        faiss.normalize_L2(faiss_embedding.reshape(1, -1))
        
        self.ltm_index.add(faiss_embedding.reshape(1, -1))
        self.ltm_corpus.append(interaction)
        
        # Supabase Remote LTM
        try:
            
            node_client.save_memory(
                user_id=user_id,
                content=text,
                session_id=session_id,
                importance=1.0,
                embedding=[float(x) for x in embedding] 
            )
            # If we were to pass embedding, we'd do: embedding=[float(x) for x in embedding]
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

    def initialize_from_remote(self, user_id: str, node_client):
        """Load past memories from the Node backend to rebuild local FAISS LTM."""
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
