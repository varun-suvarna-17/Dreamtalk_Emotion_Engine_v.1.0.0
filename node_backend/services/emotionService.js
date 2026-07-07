/**
 * services/emotionService.js
 * Supabase DB operations for emotion_logs, relationship_scores,
 * and pad_state_snapshots.
 */

import supabase from "../config/supabase.js";

// ── Emotion Logs ──────────────────────────────────────────────────────────────

/**
 * Log one agent decision per turn.
 * Called after every /step in the brain module.
 */
export async function logEmotion({
    session_id,
    user_id,
    turn_index,
    user_pleasure,
    user_arousal,
    pad_pleasure,
    pad_arousal,
    pad_dominance,
    emotion_label,
    memory_action,
    response_style,
    inertia_strength,
    reward,
    verdict,
    relationship_delta,
}) {
    const { data, error } = await supabase
        .from("emotion_logs")
        .insert({
            session_id,
            user_id,
            turn_index,
            user_pleasure,
            user_arousal,
            pad_pleasure,
            pad_arousal,
            pad_dominance,
            emotion_label,
            memory_action,
            response_style,
            inertia_strength,
            reward,
            verdict,
            relationship_delta,
        })
        .select()
        .single();

    if (error) throw error;
    return data;
}

/**
 * Get emotion history for a user across all sessions.
 * Used by the dashboard and by the brain's QUERY_EMOTIONAL_HISTORY meta-action.
 */
export async function getUserEmotionHistory(user_id, limit = 50) {
    const { data, error } = await supabase
        .from("emotion_logs")
        .select("*")
        .eq("user_id", user_id)
        .order("logged_at", { ascending: false })
        .limit(limit);

    if (error) throw error;
    return data;
}

/**
 * Get emotion logs for a specific session.
 */
export async function getSessionEmotionLogs(session_id) {
    const { data, error } = await supabase
        .from("emotion_logs")
        .select("*")
        .eq("session_id", session_id)
        .order("turn_index", { ascending: true });

    if (error) throw error;
    return data;
}

/**
 * Aggregate verdict counts for a user — used for pattern detection.
 */
export async function getVerdictSummary(user_id) {
    const { data, error } = await supabase
        .from("emotion_logs")
        .select("verdict, reward")
        .eq("user_id", user_id);

    if (error) throw error;

    // Compute counts client-side (simpler than raw SQL for now)
    const summary = {};
    let totalReward = 0;
    for (const row of data) {
        const key = row.verdict?.split(" ")[0] || "UNKNOWN";
        summary[key] = (summary[key] || 0) + 1;
        totalReward += row.reward || 0;
    }

    return {
        total_turns:    data.length,
        avg_reward:     data.length ? totalReward / data.length : 0,
        verdict_counts: summary,
    };
}

// ── Relationship Scores ───────────────────────────────────────────────────────

/**
 * Upsert the running relationship score for a user.
 * Called at the end of every session.
 */
export async function upsertRelationshipScore({
    user_id,
    score,
    total_sessions,
    total_turns,
    miss_count,
    overreact_count,
    avg_reward,
}) {
    const { data, error } = await supabase
        .from("relationship_scores")
        .upsert(
            {
                user_id,
                score,
                total_sessions,
                total_turns,
                miss_count,
                overreact_count,
                avg_reward,
                last_updated: new Date().toISOString(),
            },
            { onConflict: "user_id" }
        )
        .select()
        .single();

    if (error) throw error;
    return data;
}

/**
 * Get the current relationship score for a user.
 */
export async function getRelationshipScore(user_id) {
    const { data, error } = await supabase
        .from("relationship_scores")
        .select("*")
        .eq("user_id", user_id)
        .single();

    // If no record yet, return a fresh default
    if (error && error.code === "PGRST116") {
        return {
            user_id,
            score:           0.5,
            total_sessions:  0,
            total_turns:     0,
            miss_count:      0,
            overreact_count: 0,
            avg_reward:      0,
        };
    }
    if (error) throw error;
    return data;
}

// ── PAD State Snapshots ───────────────────────────────────────────────────────

/**
 * Save a PAD snapshot for one turn. Used to render the emotional arc chart.
 */
export async function savePadSnapshot({
    session_id,
    user_id,
    turn_index,
    pleasure,
    arousal,
    dominance,
}) {
    const { error } = await supabase.from("pad_state_snapshots").insert({
        session_id,
        user_id,
        turn_index,
        pleasure,
        arousal,
        dominance,
    });

    if (error) throw error;
}

/**
 * Get full PAD arc for a session — for visualisation.
 */
export async function getSessionPadArc(session_id) {
    const { data, error } = await supabase
        .from("pad_state_snapshots")
        .select("turn_index, pleasure, arousal, dominance, snapped_at")
        .eq("session_id", session_id)
        .order("turn_index", { ascending: true });

    if (error) throw error;
    return data;
}
