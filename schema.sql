-- ============================================================
-- DreamTalk Brain Module — Supabase Schema
-- Run this in Supabase → SQL Editor
-- Owner: Brain Module / RL Environment team
-- ============================================================

-- ── 1. users ─────────────────────────────────────────────────
-- Core user table. Other modules (auth, appointments) reference this.
-- If auth module already created this, skip and only add missing columns.
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    display_name    TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── 2. chat_sessions ─────────────────────────────────────────
-- One row per conversation session between a user and the persona.
-- Tracks the overall arc of the session.
CREATE TABLE IF NOT EXISTS chat_sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scenario_name       TEXT,                          -- e.g. grief_support, factual_neutral
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    ended_at            TIMESTAMPTZ,
    total_turns         INT DEFAULT 0,
    final_relationship_score  FLOAT DEFAULT 0.5,      -- 0.0 – 1.0
    cumulative_reward   FLOAT DEFAULT 0.0,            -- RL reward for this session
    status              TEXT DEFAULT 'active'         -- active | completed | abandoned
        CHECK (status IN ('active', 'completed', 'abandoned'))
);

-- ── 3. chat_messages ─────────────────────────────────────────
-- Individual turn-level messages within a session.
CREATE TABLE IF NOT EXISTS chat_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    turn_index      INT NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── 4. emotion_logs ──────────────────────────────────────────
-- One row per agent decision per turn.
-- Records what PAD state the brain chose and what reward it got.
CREATE TABLE IF NOT EXISTS emotion_logs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    turn_index          INT NOT NULL,

    -- User message sentiment (from VADER)
    user_pleasure       FLOAT,           -- -1.0 to 1.0
    user_arousal        FLOAT,           -- -1.0 to 1.0

    -- Agent's PAD decision
    pad_pleasure        FLOAT NOT NULL,  -- -1.0 to 1.0
    pad_arousal         FLOAT NOT NULL,  -- -1.0 to 1.0
    pad_dominance       FLOAT NOT NULL,  -- -1.0 to 1.0
    emotion_label       TEXT NOT NULL,   -- e.g. compassion, warm_curiosity
    memory_action       TEXT,            -- RETRIEVE_LTM | USE_STM | SKIP
    response_style      TEXT,            -- empathetic | analytical | ...
    inertia_strength    FLOAT,

    -- Outcome
    reward              FLOAT NOT NULL,
    verdict             TEXT,            -- PERFECT_READ | CORRECT | EMOTIONAL_DEAF | ...
    relationship_delta  FLOAT,

    logged_at           TIMESTAMPTZ DEFAULT NOW()
);

-- ── 5. relationship_scores ────────────────────────────────────
-- Running relationship score between a user and the persona.
-- Updated at the end of each session (or per turn for real-time tracking).
CREATE TABLE IF NOT EXISTS relationship_scores (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score               FLOAT NOT NULL DEFAULT 0.5,   -- 0.0 – 1.0
    total_sessions      INT DEFAULT 0,
    total_turns         INT DEFAULT 0,
    miss_count          INT DEFAULT 0,                -- EMOTIONAL_DEAF events
    overreact_count     INT DEFAULT 0,                -- EMOTIONAL_OVERREACTION events
    avg_reward          FLOAT DEFAULT 0.0,
    last_updated        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id)    -- one row per user, upserted each session
);

-- ── 6. memory_entries ────────────────────────────────────────
-- Long-term memory (LTM) entries persisted from FAISS → Supabase.
-- Each row is one semantic memory chunk for a user.
CREATE TABLE IF NOT EXISTS memory_entries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id      UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    content         TEXT NOT NULL,              -- the memory text
    embedding       VECTOR(384),               -- sentence-transformers embedding (pgvector)
    importance      FLOAT DEFAULT 1.0,         -- higher = retrieved first
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    last_accessed   TIMESTAMPTZ DEFAULT NOW()
);

-- ── 7. pad_state_snapshots ───────────────────────────────────
-- Optional: snapshot of the persona's PAD state at each turn.
-- Useful for visualising emotional arc in the dashboard.
CREATE TABLE IF NOT EXISTS pad_state_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    turn_index      INT NOT NULL,
    pleasure        FLOAT NOT NULL,
    arousal         FLOAT NOT NULL,
    dominance       FLOAT NOT NULL,
    snapped_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Indexes — for query performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id     ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_status      ON chat_sessions(status);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id  ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_emotion_logs_session_id   ON emotion_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_emotion_logs_user_id      ON emotion_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_emotion_logs_verdict      ON emotion_logs(verdict);
CREATE INDEX IF NOT EXISTS idx_memory_entries_user_id    ON memory_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_pad_snapshots_session_id  ON pad_state_snapshots(session_id);

-- ============================================================
-- Enable pgvector extension (for memory embeddings)
-- Run this FIRST if not already enabled:
-- CREATE EXTENSION IF NOT EXISTS vector;
-- ============================================================

-- ============================================================
-- Row Level Security (RLS)
-- Users can only read/write their own data.
-- Service role key bypasses RLS (used by Node.js backend).
-- ============================================================
ALTER TABLE chat_sessions        ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages        ENABLE ROW LEVEL SECURITY;
ALTER TABLE emotion_logs         ENABLE ROW LEVEL SECURITY;
ALTER TABLE relationship_scores  ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_entries       ENABLE ROW LEVEL SECURITY;
ALTER TABLE pad_state_snapshots  ENABLE ROW LEVEL SECURITY;

-- Users read their own sessions
CREATE POLICY "users_own_sessions"
    ON chat_sessions FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "users_own_messages"
    ON chat_messages FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "users_own_emotion_logs"
    ON emotion_logs FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "users_own_relationship_scores"
    ON relationship_scores FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "users_own_memory_entries"
    ON memory_entries FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "users_own_pad_snapshots"
    ON pad_state_snapshots FOR ALL
    USING (auth.uid() = user_id);
