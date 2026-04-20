# Architecture Overview: DreamTalk Brain Module v3.5

DreamTalk is a high-performance, modular AI personality engine designed to simulate human-like interaction. This module represents the standalone **Brain Module**, which focuses exclusively on the cognitive and emotional layers of a digital human, stripped of visual and audio overhead.

## Core Philosophy: Biological Mimicry
The architecture is built on the principle of **Biological Mimicry**. Each component is meticulously designed to represent a specific part of the human cognitive process:
- **Limbic System (Amygdala)**: Raw emotional reaction and survival instincts.
- **Prefrontal Cortex (PFC)**: Rational decision-making, filtering, and executive control.
- **Hippocampus**: Short-term and long-term memory integration and recall.
- **Neocortex**: Complex language generation and creative personality styling.

## System Components

### 1. Backend: The Central Nervous System (FastAPI)
The backend is a high-performance, asynchronous FastAPI application that orchestrates the entire cognitive flow.
- **LLM Service ([service.py](../backend/llm/service.py))**: Manages communication with local high-performance models like LLaMA 3. It handles persona-conditioned prompting and long-context management (up to 32K tokens).
- **Emotion Engine ([engine.py](../backend/emotion/engine.py))**: A sophisticated PAD (Pleasure, Arousal, Dominance) model that tracks the internal emotional state in a continuous 3D space.
- **Memory System ([system.py](../backend/memory/system.py))**: A 3-layer architecture for immediate context (STM), semantic recall (LTM via FAISS), and emotional relationship history.
- **Brain Simulation ([brain.py](../backend/models/brain.py))**: A multi-layer model that weights signals from the Amygdala, Hippocampus, and PFC to determine the final behavioral output.

### 2. Frontend: The Interaction Interface (React)
The frontend provides a modern, responsive chat interface designed for high-fidelity digital human interaction.
- **Personality Configuration**: Allows users to define the persona's identity (Name, Profession, Relationship) and core Big Five personality traits.
- **Live State Monitoring**: Real-time visualization of the brain's internal emotional state (Active Mood and Intensity).
- **Asynchronous Chat**: A WhatsApp-style interface with support for streaming responses and neural processing indicators.

## Detailed Information Flow
1. **Input Reception**: The user sends a message via the React frontend.
2. **Cognitive Triggering**: The backend receives the message and immediately triggers the emotional and memory layers.
3. **Emotional Resonance**: The Emotion Engine calculates a PAD stimulus from the input and updates the current mood, applying **Emotional Inertia** to ensure realistic persistence.
4. **Semantic Retrieval**: The Memory System performs a semantic search against the FAISS vector database to recall relevant past interactions.
5. **Neural Decision weighting**: The Brain Simulation weights the current emotion against rational traits (PFC) and memory resonance (Hippocampus).
6. **Prompt Synthesis**: A high-fidelity, persona-conditioned prompt is compiled, injecting the current emotion, brain state, and recalled memories.
7. **LLM Inference**: The prompt is sent to the local LLM (e.g., LLaMA 3) with GPU acceleration for high-speed generation.
8. **Memory Consolidation**: The new interaction is stored in STM, and if necessary, consolidated into LTM for permanent storage.
9. **Stateful Delivery**: The final response, along with updated emotional metadata and brain state, is returned to the user.

---
[Next: Emotion Engine (PAD Model)](emotion_engine.md)
