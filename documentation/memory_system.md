# Memory System (3-layer)

DreamTalk's Memory System is designed to ensure that digital human interactions are consistent, contextually aware, and emotionally grounded over long periods. It implements a sophisticated 3-layer architecture for memory management.

## The Memory Layers

### 1. Short-Term Memory (STM): Immediate Context
- **Role**: The session-level buffer that stores the most recent interactions.
- **Goal**: Provides immediate context for the current conversation thread.
- **Implementation**: A sliding window buffer in [system.py](../backend/memory/system.py) that stores the last 20 messages.
- **Behavior**: This is the "working memory" used to maintain coherence within a single conversation session.

### 2. Long-Term Memory (LTM): Semantic Recall
- **Role**: A persistent, searchable database of every interaction the digital human has ever had.
- **Goal**: Allows DreamTalk to "remember" topics, facts, and events from days, weeks, or months ago.
- **Implementation**:
  - **Vector Database (FAISS)**: Stores interaction embeddings as dense vectors for high-speed semantic search.
  - **Embedding Model**: Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to encode interactions into 384-dimensional vectors.
- **Mechanism**: When STM reaches its limit, the oldest interactions are "consolidated" into LTM. Before generating a response, the system performs a semantic search against LTM to find the top-K most relevant past interactions.

### 3. Emotional Memory: Relationship Trajectory
- **Role**: A specialized store that tracks the evolution of the persona's emotional state over time.
- **Goal**: Enables DreamTalk to develop a unique "relationship profile" with each user.
- **Implementation**: Stores a sequence of named emotions and their raw PAD values, along with timestamps.
- **Utility**: This allows the Brain Simulation to determine if a user has been historically friendly, hostile, or neutral, which influences the digital human's baseline traits and reactivity.

## Advanced Memory Features

### Semantic Search & Recall
DreamTalk doesn't just "remember" things in chronological order. It uses **Semantic Recall** to find memories that are conceptually similar to the current conversation. If you mention "hiking" today, DreamTalk can recall a conversation about "mountains" from three weeks ago, even if it wasn't in the recent history.

### Contextual Injection
Recalled memories are not just stored; they are actively injected into the LLM's system prompt. This gives the digital human a "shared history" with the user, making the interaction feel deeply personal and authentic.

### Persistent Storage & Portability
The system is designed for total persistence:
- **FAISS Index**: The vector search index is saved to `data/memory/ltm_index.faiss`.
- **Memory Corpus**: The actual text of interactions is stored in `data/memory/ltm_corpus.json`.
- **Emotional Logs**: Historical emotional data is persisted in `data/memory/emotional_history.json`.

This ensures that the digital human's "brain" and its relationship with you are maintained even after the system is restarted.

---
[Next: API Reference & Frontend Guide](api_reference.md)
