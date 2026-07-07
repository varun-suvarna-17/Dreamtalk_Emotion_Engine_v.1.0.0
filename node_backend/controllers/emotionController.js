/**
 * controllers/emotionController.js
 * Handles emotion log writes, relationship score updates, and PAD snapshots.
 */

import * as emotionService from "../services/emotionService.js";

// POST /api/brain/emotion/log
// Called by Python after every /step
export async function logEmotion(req, res) {
    try {
        const log = await emotionService.logEmotion(req.body);
        res.status(201).json({ success: true, log });
    } catch (err) {
        console.error("[emotionController] logEmotion:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/emotion/history/:user_id
// Used by dashboard + brain's QUERY_EMOTIONAL_HISTORY meta-action
export async function getEmotionHistory(req, res) {
    try {
        const limit   = parseInt(req.query.limit) || 50;
        const history = await emotionService.getUserEmotionHistory(
            req.params.user_id,
            limit
        );
        res.status(200).json({ success: true, history });
    } catch (err) {
        console.error("[emotionController] getEmotionHistory:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/emotion/session/:session_id
export async function getSessionLogs(req, res) {
    try {
        const logs = await emotionService.getSessionEmotionLogs(req.params.session_id);
        res.status(200).json({ success: true, logs });
    } catch (err) {
        console.error("[emotionController] getSessionLogs:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/emotion/summary/:user_id
// Returns verdict counts + avg reward — for dashboard stats cards
export async function getVerdictSummary(req, res) {
    try {
        const summary = await emotionService.getVerdictSummary(req.params.user_id);
        res.status(200).json({ success: true, summary });
    } catch (err) {
        console.error("[emotionController] getVerdictSummary:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// POST /api/brain/emotion/relationship
// Called by Python at end of session to upsert relationship score
export async function upsertRelationship(req, res) {
    try {
        const record = await emotionService.upsertRelationshipScore(req.body);
        res.status(200).json({ success: true, record });
    } catch (err) {
        console.error("[emotionController] upsertRelationship:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/emotion/relationship/:user_id
// Used by dashboard + brain's CHECK_RELATIONSHIP_SCORE meta-action
export async function getRelationshipScore(req, res) {
    try {
        const score = await emotionService.getRelationshipScore(req.params.user_id);
        res.status(200).json({ success: true, score });
    } catch (err) {
        console.error("[emotionController] getRelationshipScore:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// POST /api/brain/emotion/pad-snapshot
// Called by Python each turn to record PAD arc
export async function savePadSnapshot(req, res) {
    try {
        await emotionService.savePadSnapshot(req.body);
        res.status(201).json({ success: true });
    } catch (err) {
        console.error("[emotionController] savePadSnapshot:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/emotion/pad-arc/:session_id
// Returns full PAD arc for a session — used by emotional arc chart
export async function getPadArc(req, res) {
    try {
        const arc = await emotionService.getSessionPadArc(req.params.session_id);
        res.status(200).json({ success: true, arc });
    } catch (err) {
        console.error("[emotionController] getPadArc:", err.message);
        res.status(500).json({ error: err.message });
    }
}
