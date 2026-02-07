-- User data tables for Whirlwind KB: saved facts, lens results, toolkit edits.
-- Run in Supabase SQL Editor (or via Supabase CLI: supabase db push).
-- RLS: users can only read/write their own rows.

-- 1. Saved facts (Knowledge Base bookmarks)
create table if not exists public.user_saved_facts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  fact_id text not null,
  created_at timestamptz default now(),
  unique(user_id, fact_id)
);

alter table public.user_saved_facts enable row level security;

drop policy if exists "Users can manage own saved facts" on public.user_saved_facts;
create policy "Users can manage own saved facts"
  on public.user_saved_facts for all using (auth.uid() = user_id);

-- 2. Lens results (Garvey Lens responses + checked action steps)
create table if not exists public.user_lens_results (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  result_id text not null,
  payload jsonb not null,
  checked_action_step_ids text[] default '{}',
  created_at timestamptz default now(),
  unique(user_id, result_id)
);

alter table public.user_lens_results enable row level security;

drop policy if exists "Users can manage own lens results" on public.user_lens_results;
create policy "Users can manage own lens results"
  on public.user_lens_results for all using (auth.uid() = user_id);

-- 3. Toolkit edits (custom template markdown)
create table if not exists public.user_toolkit_edits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  template_id text not null,
  markdown text not null,
  updated_at timestamptz default now(),
  unique(user_id, template_id)
);

alter table public.user_toolkit_edits enable row level security;

drop policy if exists "Users can manage own toolkit edits" on public.user_toolkit_edits;
create policy "Users can manage own toolkit edits"
  on public.user_toolkit_edits for all using (auth.uid() = user_id);
