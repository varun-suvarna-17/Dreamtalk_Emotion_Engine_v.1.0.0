/**
 * services/memoryService.js
 * Supabase DB operations for memory_entries (LTM persistence).
 *
 * The Python brain uses FAISS for fast in-session vector search.
 * This service persists those memories to Supabase so they survive
 * server restarts and are shared across sessions.
 */

import supabase from "../config/supabase.js";

/**
 * Save a new memory entry (text + optional embedding).
 */
export async function saveMemory({
    user_id,
    session_id,
    content,
    embedding = null,   // float[] from sentence-transformers, optional
    importance = 1.0,
}) {
    const { data, error } = await supabase
        .from("memory_entries")
        .insert({
            user_id,
            session_id,
            content,
            embedding,
            importance,
        })
        .select()
        .single();

    if (error) throw error;
    return data;
}

/**
 * Get all memories for a user, most important first.
 * The Python brain uses this to warm-up FAISS on session start.
 */
export async function getUserMemories(user_id, limit = 100) {
    const { data, error } = await supabase
        .from("memory_entries")
        .select("id, content, importance, created_at")
        .eq("user_id", user_id)
        .order("importance",  { ascending: false })
        .order("created_at",  { ascending: false })
        .limit(limit);

    if (error) throw error;
    return data;
}

/**
 * Update last_accessed timestamp when a memory is retrieved.
 * Keeps the memory fresh and prevents it from aging out.
 */
export async function touchMemory(memory_id) {
    const { error } = await supabase
        .from("memory_entries")
        .update({ last_accessed: new Date().toISOString() })
        .eq("id", memory_id);

    if (error) throw error;
}

/**
 * Delete old or low-importance memories for a user.
 * Run periodically to keep the memory table lean.
 */
export async function pruneMemories(user_id, keepTop = 200) {
    // Get all memories sorted by importance desc
    const { data, error } = await supabase
        .from("memory_entries")
        .select("id")
        .eq("user_id", user_id)
        .order("importance",    { ascending: false })
        .order("last_accessed", { ascending: false });

    if (error) throw error;

    const toDelete = data.slice(keepTop).map((r) => r.id);
    if (toDelete.length === 0) return { pruned: 0 };

    const { error: delErr } = await supabase
        .from("memory_entries")
        .delete()
        .in("id", toDelete);

    if (delErr) throw delErr;
    return { pruned: toDelete.length };
}
