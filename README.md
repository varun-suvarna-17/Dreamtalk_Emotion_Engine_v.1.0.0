# DreamTalk: Standalone Brain Module

The **DreamTalk Brain Module** is a high-performance, independent AI system designed to simulate human-like cognition, emotion, and personality. It is stripped of all voice and avatar dependencies, focusing purely on the "thinking" and "feeling" layers of a digital human.

## 🎯 Key Capabilities
- **Neural Personality Simulation**: Dynamically adapts behavior based on Big Five traits (Openness, Conscientiousness, Extroversion, Agreeableness, Neuroticism).
- **Advanced Emotion Engine**: Uses the **PAD (Pleasure, Arousal, Dominance)** model with 50+ emotional states and emotional inertia for realistic mood persistence.
- **3-Layer Memory System**:
  - **STM**: Recent conversation buffer.
  - **LTM**: FAISS-powered vector database for long-term semantic recall.
  - **Emotional Memory**: Tracks relationship history and emotional trends per user.
- **Natural Response Engine**: Simulates human-like imperfections, decision weighting (Emotion vs Logic), and tone adaptation.

## 🏗️ Project Structure
```text
brain_module/
├── backend/            # FastAPI Standalone Backend
│   ├── brain/          # Cognitive Simulation Layers
│   ├── emotion/        # PAD Emotion Engine (50+ states)
│   ├── memory/         # 3-Layer Memory System (STM/LTM/Emotional)
│   ├── llm/            # Local LLM Service (Ollama/LLaMA 3)
│   ├── models/         # Pydantic & Data Models
│   └── main.py         # Module Entry Point
├── frontend/           # React Chat & Configuration UI
│   ├── pages/          # ChatApp & Configuration Panel
│   └── components/     # UI Components
├── data/               # Persistent Vector DB & Emotional Logs
└── configs/            # Personality & System Presets
```

## 🚀 Getting Started

### 1. Backend Setup
1. **Ollama**: Ensure Ollama is installed and the LLaMA 3 model is pulled:
   ```bash
   ollama pull llama3:8b
   ```
2. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn ollama faiss-cpu sentence-transformers numpy pydantic
   ```
3. **Run**:
   ```bash
   python backend/main.py
   ```

### 2. Frontend Setup
1. **Dependencies**: `npm install axios react`
2. **Run**: Use your standard React development server command.

## 🛠️ Usage
1. **Configure**: Open the UI and define the persona's name, profession, and personality traits using the sliders.
2. **Initialize**: Click "Start Chat" to boot the brain module with the defined configuration.
3. **Interact**: Chat naturally with a digital human that remembers you and reacts with genuine emotional complexity.

---
*This module is designed for developers who want to integrate a sophisticated "Brain" into their own applications without the overhead of voice or visual rendering.*
