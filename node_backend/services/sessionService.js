/**
 * services/sessionService.js
 * Supabase DB operations for chat_sessions and chat_messages.
 * Called by sessionController. Never called directly from routes.
 */

import supabase from "../config/supabase.js";

// ── Sessions ──────────────────────────────────────────────────────────────────

/**
 * Create a new chat session when the brain calls /reset.
 */
export async function createSession({ user_id, scenario_name }) {
    const { data, error } = await supabase
        .from("chat_sessions")
        .insert({
            user_id,
            scenario_name,
            status: "active",
        })
        .select()
        .single();

    if (error) throw error;
    return data;
}

/**
 * Mark a session as completed and write final stats.
 */
export async function closeSession({
    session_id,
    total_turns,
    final_relationship_score,
    cumulative_reward,
}) {
    const { data, error } = await supabase
        .from("chat_sessions")
        .update({
            status:                   "completed",
            ended_at:                 new Date().toISOString(),
            total_turns,
            final_relationship_score,
            cumulative_reward,
        })
        .eq("id", session_id)
        .select()
        .single();

    if (error) throw error;
    return data;
}

/**
 * Fetch a single session by ID.
 */
export async function getSession(session_id) {
    const { data, error } = await supabase
        .from("chat_sessions")
        .select("*")
        .eq("id", session_id)
        .single();

    if (error) throw error;
    return data;
}

/**
 * Get all sessions for a user, most recent first.
 */
export async function getUserSessions(user_id, limit = 20) {
    const { data, error } = await supabase
        .from("chat_sessions")
        .select("*")
        .eq("user_id", user_id)
        .order("started_at", { ascending: false })
        .limit(limit);

    if (error) throw error;
    return data;
}

// ── Messages ──────────────────────────────────────────────────────────────────

/**
 * Save a user + assistant message pair for one turn.
 */
export async function saveMessagePair({
    session_id,
    user_id,
    turn_index,
    user_content,
    assistant_content,
}) {
    const { error } = await supabase.from("chat_messages").insert([
        {
            session_id,
            user_id,
            turn_index,
            role:    "user",
            content: user_content,
        },
        {
            session_id,
            user_id,
            turn_index,
            role:    "assistant",
            content: assistant_content,
        },
    ]);

    if (error) throw error;
}

/**
 * Get all messages for a session, ordered by turn.
 */
export async function getSessionMessages(session_id) {
    const { data, error } = await supabase
        .from("chat_messages")
        .select("*")
        .eq("session_id", session_id)
        .order("turn_index", { ascending: true })
        .order("role",       { ascending: true });

    if (error) throw error;
    return data;
}
