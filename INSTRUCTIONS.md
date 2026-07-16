# DreamTalk Brain Module - Instructions

## 🧠 Overview
The **Brain Module** is the cognitive, emotional, and memory backend for **DreamTalk**. It manages:
- **Emotion Engine**: Calculates emotional states (using PAD: Pleasure, Arousal, Dominance) and sentiment analysis.
- **Memory System**: Implements a three-layer memory system (Short-Term Memory, Long-Term Memory, and Emotional History).
- **Personality Simulator**: Drives LLM-based agent responses tailored to specific avatar personas and Big Five personality traits.

### 🏗️ How It Fits in the DreamTalk Ecosystem
DreamTalk consists of several repository/modules:
1. **Frontend (Next.js)**: Standard UI for users to interact with the avatars.
2. **Node.js Express Backend (Node Bridge)**: Acts as the main API and DB gateway for writing/reading configuration records.
3. **Voice Module**: Handles speech-to-text (STT) and text-to-speech (TTS) interfaces.
4. **Avatar Engine**: Drives visual/facial behavior based on emotional cues.
5. **Brain Module (This repo)**: Core FastAPI service that integrates all cognitive features, memory indexing, and LLM processing.

```
+--------------------+
|  Next.js Frontend  |
+---------+----------+
          |
          | REST API
          v
+---------+----------+      REST (node_client)     +----------------------+
| Node.js Express    |<----------------------------+ FastAPI Brain Module |
| (Node Bridge)      |                             | (This Repository)    |
+---------+----------+                             +----------+-----------+
          |                                                   |
          | Read/Write                                        | Direct reads/writes
          v                                                   v
+---------+---------------------------------------------------+-----------+
|                            Supabase Database                            |
+-------------------------------------------------------------------------+
```

---

## 🛠️ Prerequisites
- **Python Version**: Python 3.9+ (Python 3.10 or 3.11 is recommended).
- **Package Manager**: `pip` (standard Python package installer).

---

## 🚀 Setup & Installation

### 1. Install Dependencies
Run the following command in the project root to install the required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
1. Copy the `.env.example` file to create your own local `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the required values:
   - **`SUPABASE_URL`**: Your Supabase project URL (e.g., `https://your-project.supabase.co`).
   - **`SUPABASE_KEY` / `SUPABASE_SECRET_KEY`**: Use the **`service_role`** key specifically.
     > [!IMPORTANT]
     > The Brain Module must use the `service_role` secret key because Row Level Security (RLS) is enabled on key tables (like `avatar_config` and `brain_output`). As a trusted background backend service, the Brain Module needs to bypass RLS policies to perform writes/updates without a user authentication token context.
   - **`LLM_PROVIDER`**: Set to `groq` (cloud, fast) or `ollama` (local offline fallback).
   - **`GROQ_API_KEY`**: Your Groq Cloud API key if using Groq.
   - **`NODE_BACKEND_URL`**: URL of your running Node.js Bridge backend (typically `http://localhost:3000` or `http://localhost:3001`).
   - **`BRAIN_API_KEY`**: Secret key used to authorize calls to/from the Node.js backend.

---

## 🏃 Running the Service

Start the FastAPI backend server:
```bash
python backend/main.py
```

### Confirming it runs
To verify the service is running and configured correctly, query the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected JSON response:
```json
{
  "status": "online",
  "module": "brain_module",
  "multi_tenant": true,
  "supabase_enabled": true,
  "active_avatar_runtimes": 0
}
```

---

## 👥 Multi-Tenancy Architecture
The Brain Module supports multi-tenancy. Every avatar and user combination is handled in a sandboxed runtime instance.
The main endpoints:
- `POST /chat`
- `POST /configure`
- `GET /memory`
- `GET /emotion`

All accept `user_id` and `avatar_id` in their request bodies or query parameters. If not provided, default placeholder values (`default_user` and `default_avatar`) are utilized so the system can be easily tested in a standalone environment.

---

## 🗄️ Database Management & Schema Sharing
- The `avatar_config` and `brain_output` Supabase tables are shared directly with the frontend and Node.js bridge repositories.
- **IMPORTANT**: Any schema changes to these tables must be coordinated across all repos. The `documentation/supabase_multi_tenant.sql` file in this repository serves as the official source of truth.

### Switching to a Different/Shared Supabase Org
If you need to migrate or switch the project to a new Supabase organization/project:
1. Update your `.env` file with the new `SUPABASE_URL` and `SUPABASE_SECRET_KEY` (service_role).
2. Execute the schema definitions inside [supabase_multi_tenant.sql](file:///d:/Major%20project/Dreamtalk_Emotion_Engine_v.1.0.0/documentation/supabase_multi_tenant.sql) in the new Supabase SQL Editor to initialize all tables, schemas, indexes, and pgvector settings.
