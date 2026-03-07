# DreamTalk: Emotion Engine

This is the foundational "Emotion Engine Model" for the DreamTalk digital personality recreation system.
It is a local, API-free system that uses a local Llama model to converse with the user while maintaining a dynamic emotional state based on the sentiment of the user's inputs.

## Architecture

- **Affective Analysis:** Uses `vaderSentiment` for lightweight, offline sentiment analysis.
- **State Tracker:** Computes an exponential moving average (EMA) of user sentiment to transition between various "moods".
- **Local LLM:** Uses the `ollama` Python package to query a local Llama 3.1 8B parameter model, injecting the avatar's mood and recent history into the prompt.

## Setup Instructions

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama:**
   - Download and install Ollama from [https://ollama.com/](https://ollama.com/)
   - Open a terminal and pull the Llama 3.1 model:
     ```bash
     ollama run llama3.1
     ```

3. **Run the Emotion Engine:**
   ```bash
   python src/dreamtalk_terminal.py
   ```
