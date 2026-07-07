/**
 * middleware/validateBrain.js
 *
 * Authenticates requests coming from the Python brain module (FastAPI).
 * The brain signs every request with a shared secret (BRAIN_API_KEY).
 * This prevents any random caller from writing emotion logs / sessions.
 */

export function validateBrainKey(req, res, next) {
    const apiKey = req.headers["x-brain-api-key"];

    if (!apiKey || apiKey !== process.env.BRAIN_API_KEY) {
        return res.status(401).json({
            error: "Unauthorized. Missing or invalid X-Brain-Api-Key header.",
        });
    }

    next();
}

/**
 * Validates that required body fields are present and correctly typed.
 * Usage: validateBody(["user_id", "session_id", "emotion_label"])
 */
export function validateBody(requiredFields) {
    return (req, res, next) => {
        const missing = requiredFields.filter(
            (f) => req.body[f] === undefined || req.body[f] === null
        );
        if (missing.length > 0) {
            return res.status(422).json({
                error: `Missing required fields: ${missing.join(", ")}`,
            });
        }
        next();
    };
}
