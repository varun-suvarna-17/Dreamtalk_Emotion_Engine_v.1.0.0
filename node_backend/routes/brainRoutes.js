/**
 * routes/brainRoutes.js
 *
 * All routes for the brain module integration.
 * Mounted at /api/brain in your main Express app.
 *
 * Every route is protected by validateBrainKey — only the Python
 * FastAPI service (with BRAIN_API_KEY) can call these endpoints.
 *
 * Read routes (GET) are also accessible to the frontend team
 * for dashboard and history features — remove validateBrainKey
 * from those routes if you want frontend-direct access.
 */

import { Router } from "express";
import { validateBrainKey, validateBody } from "../middleware/validateBrain.js";

import * as sessionCtrl  from "../controllers/sessionController.js";
import * as emotionCtrl  from "../controllers/emotionController.js";
import * as memoryCtrl   from "../controllers/memoryController.js";

const router = Router();

// All brain routes require the shared API key
router.use(validateBrainKey);

// ── Sessions ──────────────────────────────────────────────────────────────────
router.post(
    "/sessions/start",
    validateBody(["user_id"]),
    sessionCtrl.startSession
);

router.post(
    "/sessions/close",
    validateBody(["session_id", "total_turns", "final_relationship_score", "cumulative_reward"]),
    sessionCtrl.endSession
);

router.post(
    "/sessions/message",
    validateBody(["session_id", "user_id", "turn_index", "user_content", "assistant_content"]),
    sessionCtrl.saveMessage
);

router.get("/sessions/user/:user_id",    sessionCtrl.getUserSessions);
router.get("/sessions/:session_id",      sessionCtrl.getSession);
router.get("/sessions/:session_id/messages", sessionCtrl.getMessages);

// ── Emotion Logs ──────────────────────────────────────────────────────────────
router.post(
    "/emotion/log",
    validateBody(["session_id", "user_id", "turn_index",
                  "pad_pleasure", "pad_arousal", "pad_dominance",
                  "emotion_label", "reward", "verdict"]),
    emotionCtrl.logEmotion
);

router.get("/emotion/history/:user_id",       emotionCtrl.getEmotionHistory);
router.get("/emotion/session/:session_id",    emotionCtrl.getSessionLogs);
router.get("/emotion/summary/:user_id",       emotionCtrl.getVerdictSummary);

// ── Relationship Scores ───────────────────────────────────────────────────────
router.post(
    "/emotion/relationship",
    validateBody(["user_id", "score"]),
    emotionCtrl.upsertRelationship
);

router.get("/emotion/relationship/:user_id",  emotionCtrl.getRelationshipScore);

// ── PAD Snapshots ─────────────────────────────────────────────────────────────
router.post(
    "/emotion/pad-snapshot",
    validateBody(["session_id", "user_id", "turn_index",
                  "pleasure", "arousal", "dominance"]),
    emotionCtrl.savePadSnapshot
);

router.get("/emotion/pad-arc/:session_id",    emotionCtrl.getPadArc);

// ── Memory ────────────────────────────────────────────────────────────────────
router.post(
    "/memory",
    validateBody(["user_id", "content"]),
    memoryCtrl.saveMemory
);

router.get("/memory/:user_id",                memoryCtrl.getUserMemories);
router.patch("/memory/:memory_id/touch",      memoryCtrl.touchMemory);
router.delete("/memory/:user_id/prune",       memoryCtrl.pruneMemories);

export default router;
