/**
 * controllers/sessionController.js
 * Handles all session and message lifecycle operations.
 * Called by the brain module via POST requests from Python.
 */

import * as sessionService from "../services/sessionService.js";

// POST /api/brain/sessions/start
// Called by Python when /reset is triggered
export async function startSession(req, res) {
    try {
        const { user_id, scenario_name } = req.body;
        const session = await sessionService.createSession({ user_id, scenario_name });
        res.status(201).json({ success: true, session });
    } catch (err) {
        console.error("[sessionController] startSession:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// POST /api/brain/sessions/close
// Called by Python when episode done=True
export async function endSession(req, res) {
    try {
        const {
            session_id,
            total_turns,
            final_relationship_score,
            cumulative_reward,
        } = req.body;

        const session = await sessionService.closeSession({
            session_id,
            total_turns,
            final_relationship_score,
            cumulative_reward,
        });
        res.status(200).json({ success: true, session });
    } catch (err) {
        console.error("[sessionController] endSession:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// POST /api/brain/sessions/message
// Called by Python after each /step to save the message pair
export async function saveMessage(req, res) {
    try {
        const {
            session_id,
            user_id,
            turn_index,
            user_content,
            assistant_content,
        } = req.body;

        await sessionService.saveMessagePair({
            session_id,
            user_id,
            turn_index,
            user_content,
            assistant_content,
        });
        res.status(201).json({ success: true });
    } catch (err) {
        console.error("[sessionController] saveMessage:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/sessions/:session_id
export async function getSession(req, res) {
    try {
        const session = await sessionService.getSession(req.params.session_id);
        res.status(200).json({ success: true, session });
    } catch (err) {
        console.error("[sessionController] getSession:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/sessions/user/:user_id
export async function getUserSessions(req, res) {
    try {
        const limit    = parseInt(req.query.limit) || 20;
        const sessions = await sessionService.getUserSessions(req.params.user_id, limit);
        res.status(200).json({ success: true, sessions });
    } catch (err) {
        console.error("[sessionController] getUserSessions:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/sessions/:session_id/messages
export async function getMessages(req, res) {
    try {
        const messages = await sessionService.getSessionMessages(req.params.session_id);
        res.status(200).json({ success: true, messages });
    } catch (err) {
        console.error("[sessionController] getMessages:", err.message);
        res.status(500).json({ error: err.message });
    }
}
