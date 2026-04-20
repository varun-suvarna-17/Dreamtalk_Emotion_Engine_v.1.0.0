# API Reference & Frontend Guide

DreamTalk Brain Module v3.5 uses a high-performance **FastAPI** backend and a reactive **Next.js** frontend. This document provides a detailed guide for developers to interact with the system.

## Backend API Reference (FastAPI)

The backend is located in the `backend/` directory and is designed to be fully asynchronous.

### 1. Chat Interaction
- **Endpoint**: `POST /chat`
- **Description**: The primary entry point for interaction. Processes the message through all cognitive layers.
- **Request Body**:
  ```json
  {
    "user_input": "Hey Alex, do you remember our talk about AI?",
    "session_id": "optional_string"
  }
  ```
- **Key Response Fields**:
  - `response`: The generated text from the LLM.
  - `emotion`: The current primary emotional state (name, display name, PAD values).
  - `brain_state`: The internal activation levels of the Amygdala, PFC, Hippocampus, and Neocortex.
  - `delay_ms`: The simulated neural processing time.

### 2. Personality Configuration
- **Endpoint**: `POST /configure`
- **Description**: Initializes or updates the digital human's identity and Big Five traits.
- **Request Body**:
  ```json
  {
    "name": "Alex",
    "profession": "Software Architect",
    "relationship": "Friend",
    "tone": "casual",
    "traits": {
      "extroversion": 0.8,
      "agreeableness": 0.6,
      "neuroticism": 0.3,
      "openness": 0.9,
      "conscientiousness": 0.5
    }
  }
  ```

### 3. Memory & Emotion Diagnostics
- **Endpoints**: `GET /memory`, `GET /emotion`
- **Description**: Debugging endpoints to retrieve the current state of all memory layers and the active PAD state.

---

## Frontend Guide (React / Next.js)

The frontend is designed as a sleek, dark-themed "Digital Human Control Center."

### 1. Configuration Panel
The initial screen of the application allows you to define the **Cognitive Profile** of your digital human.
- **Identity Fields**: Define the Name, Profession, and Relationship.
- **Big Five Sliders**: Use interactive range inputs to set the OCEAN personality traits.
- **Initialization**: Clicking "Start Chat" sends the configuration to the backend and boots the brain module.

### 2. Chat Interface
A WhatsApp-style interface focused on authentic communication.
- **Neural Indicators**: Displays the assistant's active mood (e.g., "JOYFUL") and intensity (e.g., "high") for every message.
- **Thinking State**: Shows a "Processing neural signals..." pulse while the backend calculates the response and simulated delay.
- **History Management**: Automatically scrolls to the newest message and maintains session history.

### 3. Technical Implementation
- **Axios**: Used for all asynchronous communication with the FastAPI backend.
- **Tailwind CSS**: Used for the premium, high-contrast UI design.
- **React Hooks**: Extensively uses `useState`, `useEffect`, and `useRef` for managing state and side effects.

## Local Setup Requirements
- **Ollama**: Must be running with the `llama3:8b` (or 70B) model pulled.
- **CORS**: The backend has CORS enabled to allow communication from the frontend (typically running on `localhost:3000`).

---
[Return to Architecture Overview](architecture.md)
