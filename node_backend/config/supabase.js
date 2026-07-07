import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";

dotenv.config();

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SECRET_KEY) {
    throw new Error(
        "Missing Supabase credentials. " +
        "Ensure SUPABASE_URL and SUPABASE_SECRET_KEY are set in your .env file."
    );
}

// Service-role client — bypasses RLS, used server-side only.
// NEVER expose this key to the frontend.
const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SECRET_KEY,
    {
        auth: {
            autoRefreshToken: false,
            persistSession:   false,
        },
    }
);

export default supabase;
