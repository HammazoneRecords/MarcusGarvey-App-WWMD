# Supabase

## Running the user-data migration

1. Open your project in [Supabase Dashboard](https://supabase.com/dashboard) → **SQL Editor**.
2. Copy the contents of `migrations/001_user_data_tables.sql`.
3. Paste and run. This creates:
   - `user_saved_facts` (user_id, fact_id)
   - `user_lens_results` (user_id, result_id, payload jsonb, checked_action_step_ids)
   - `user_toolkit_edits` (user_id, template_id, markdown)
   - RLS policies so users can only access their own rows.

If you use the Supabase CLI: from the repo root, `supabase db push` (or link the project and run migrations as per Supabase docs).
