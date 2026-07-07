/**
 * controllers/memoryController.js
 * Handles LTM memory persistence between Python brain and Supabase.
 */

import * as memoryService from "../services/memoryService.js";

// POST /api/brain/memory
// Called by Python to persist a new LTM memory entry
export async function saveMemory(req, res) {
    try {
        const memory = await memoryService.saveMemory(req.body);
        res.status(201).json({ success: true, memory });
    } catch (err) {
        console.error("[memoryController] saveMemory:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// GET /api/brain/memory/:user_id
// Called by Python on session start to warm up FAISS from persisted memories
export async function getUserMemories(req, res) {
    try {
        const limit    = parseInt(req.query.limit) || 100;
        const memories = await memoryService.getUserMemories(req.params.user_id, limit);
        res.status(200).json({ success: true, memories });
    } catch (err) {
        console.error("[memoryController] getUserMemories:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// PATCH /api/brain/memory/:memory_id/touch
// Called when Python retrieves a memory — updates last_accessed
export async function touchMemory(req, res) {
    try {
        await memoryService.touchMemory(req.params.memory_id);
        res.status(200).json({ success: true });
    } catch (err) {
        console.error("[memoryController] touchMemory:", err.message);
        res.status(500).json({ error: err.message });
    }
}

// DELETE /api/brain/memory/:user_id/prune
// Called periodically to keep memory table lean
export async function pruneMemories(req, res) {
    try {
        const keepTop = parseInt(req.query.keep) || 200;
        const result  = await memoryService.pruneMemories(req.params.user_id, keepTop);
        res.status(200).json({ success: true, ...result });
    } catch (err) {
        console.error("[memoryController] pruneMemories:", err.message);
        res.status(500).json({ error: err.message });
    }
}
