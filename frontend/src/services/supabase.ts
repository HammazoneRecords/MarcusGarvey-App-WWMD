import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const url = import.meta.env.VITE_SUPABASE_URL;
const anonKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY;

/** Supabase client for auth and data. Only created when env vars are set. */
let supabase: SupabaseClient | null = null;

if (url && anonKey) {
    supabase = createClient(url, anonKey);
}

export { supabase };

/** Use for conditional features: if (isSupabaseConfigured()) { ... } */
export function isSupabaseConfigured(): boolean {
    return supabase !== null;
}
