"""
Memory System for DreamTalk.
3-layer: STM (conversation buffer), LTM (Vector DB), Emotional Memory.
"""

import os
import json
import faiss
import numpy as np
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

class MemorySystem:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Layer 1: Short-Term Memory (Session Buffer)
        self.stm: List[Dict] = []
        self.stm_limit = 20
        
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

    def add_interaction(self, user_input: str, response: str, emotion: Dict):
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
            self._add_to_ltm(oldest)
            
        # Update Emotional Memory
        self.emotional_history.append({
            "emotion": emotion["name"],
            "vad": emotion["vad"],
            "timestamp": interaction["timestamp"]
        })

    def _add_to_ltm(self, interaction: Dict):
        """Push interaction to the vector database."""
        text = f"User said: {interaction['user']}\nDreamTalk responded: {interaction['assistant']}"
        embedding = self.ltm_model.encode([text])[0]
        embedding = np.array(embedding, dtype="float32")
        faiss.normalize_L2(embedding.reshape(1, -1))
        
        self.ltm_index.add(embedding.reshape(1, -1))
        self.ltm_corpus.append(interaction)

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

    def save(self):
        """Persist LTM and emotional memory to disk."""
        # Save LTM Index
        faiss.write_index(self.ltm_index, os.path.join(self.base_path, "ltm_index.faiss"))
        # Save LTM Corpus
        with open(os.path.join(self.base_path, "ltm_corpus.json"), "w") as f:
            json.dump(self.ltm_corpus, f)
        # Save Emotional History
        with open(os.path.join(self.base_path, "emotional_history.json"), "w") as f:
            json.dump(self.emotional_history, f)

    def load(self):
        """Load memory from disk."""
        idx_path = os.path.join(self.base_path, "ltm_index.faiss")
        if os.path.exists(idx_path):
            self.ltm_index = faiss.read_index(idx_path)
        
        corpus_path = os.path.join(self.base_path, "ltm_corpus.json")
        if os.path.exists(corpus_path):
            with open(corpus_path, "r") as f:
                self.ltm_corpus = json.load(f)
        
        eh_path = os.path.join(self.base_path, "emotional_history.json")
        if os.path.exists(eh_path):
            with open(eh_path, "r") as f:
                self.emotional_history = json.load(f)
