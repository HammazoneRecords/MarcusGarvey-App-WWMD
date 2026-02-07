# Plan: Link User Profile Data and Saved Content to Supabase

## Goal

Persist per-user data in Supabase so it syncs across devices and survives logout/login:

- **Saved facts** (Knowledge Base bookmarks)
- **Saved lens results** (Garvey Lens responses + checked action steps)
- **Toolkit edits** (custom template markdown)
- **Recent lens activity** (optional; can stay local or be a simple count/timestamps)

Current state: all of this lives in Zustand + localStorage only (no user binding).

---

## Best-Practice Approach

1. **Supabase tables** — one table per domain (saved_facts, lens_results, toolkit_edits), keyed by `user_id` (auth.uid()).
2. **Row Level Security (RLS)** — users can only read/write their own rows.
3. **Write-through when signed in** — every local mutation (toggle save, save lens result, etc.) also writes to Supabase when `user` is present.
4. **Hydrate on login** — when the user signs in, fetch their rows and merge into (or replace) the Zustand store so the UI shows server state.
5. **Anonymous / logout** — keep using the same store and localStorage for guests; when the user logs out, optionally clear only the “user” slice or leave local data as anonymous. Next login loads server data and overwrites those slices.

---

## 1. Supabase Schema

Run in Supabase SQL editor (or migrations).

### 1.1 Optional: `profiles`

If you want display name, avatar, etc. (beyond `auth.users`):

```sql
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  avatar_url text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table public.profiles enable row level security;

create policy "Users can read own profile"
  on public.profiles for select using (auth.uid() = id);
create policy "Users can update own profile"
  on public.profiles for update using (auth.uid() = id);
create policy "Users can insert own profile"
  on public.profiles for insert with check (auth.uid() = id);
```

Trigger to create a profile row on signup (optional):

```sql
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1)));
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
```

### 1.2 `user_saved_facts`

```sql
create table if not exists public.user_saved_facts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  fact_id text not null,
  created_at timestamptz default now(),
  unique(user_id, fact_id)
);

alter table public.user_saved_facts enable row level security;

create policy "Users can manage own saved facts"
  on public.user_saved_facts for all using (auth.uid() = user_id);
```

### 1.3 `user_lens_results`

Store full lens result as JSONB so we don’t have to change the schema when the app’s `WWMDResponse` shape evolves. Include a stable `result_id` (same as app’s `result.id`) and optionally store checked action step IDs in the payload or in a separate column.

```sql
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

create policy "Users can manage own lens results"
  on public.user_lens_results for all using (auth.uid() = user_id);
```

- **payload**: full `WWMDResponse` (query, principle, historicalAnalogy, receipts, actionSteps, mirrorQuestions, etc.).
- **checked_action_step_ids**: array of action step IDs the user checked (maps to current `savedActionSteps[resultId]`).

### 1.4 `user_toolkit_edits`

```sql
create table if not exists public.user_toolkit_edits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  template_id text not null,
  markdown text not null,
  updated_at timestamptz default now(),
  unique(user_id, template_id)
);

alter table public.user_toolkit_edits enable row level security;

create policy "Users can manage own toolkit edits"
  on public.user_toolkit_edits for all using (auth.uid() = user_id);
```

### 1.5 Optional: `user_recent_lens_activity`

If you want to sync “Recent Lens Activity” (e.g. last N session timestamps):

```sql
create table if not exists public.user_recent_lens_activity (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  session_at timestamptz not null default now()
);

alter table public.user_recent_lens_activity enable row level security;

create policy "Users can manage own lens activity"
  on public.user_recent_lens_activity for all using (auth.uid() = user_id);
```

You can limit to last N rows per user in the app (e.g. fetch and keep last 10).

---

## 2. Sync Strategy

### 2.1 When user signs in

1. Fetch from Supabase:
   - `user_saved_facts` → list of `fact_id`
   - `user_lens_results` → list of `{ result_id, payload, checked_action_step_ids }`
   - `user_toolkit_edits` → list of `{ template_id, markdown }`
   - (optional) `user_recent_lens_activity` → timestamps
2. Hydrate the store:
   - Set `savedFactIds` to the fetched fact IDs.
   - Set `savedLensResults` to the payloads (in a consistent order, e.g. by `created_at` desc).
   - Set `savedActionSteps` to a map `result_id -> checked_action_step_ids`.
   - Set `toolkitEdits` to the map of template_id -> markdown.
   - Set `recentWWMDIds` from activity rows if you synced them.
3. Keep using the same Zustand store; no need to change component APIs.

### 2.2 When user is signed in (write-through)

On each mutation that currently only updates the store:

| Action | Store update (existing) | Supabase write |
|--------|-------------------------|----------------|
| Toggle saved fact | `toggleSavedFact(id)` | Insert or delete row in `user_saved_facts` |
| Save lens result | `saveLensResult(result)` | Upsert `user_lens_results` (result_id, payload, checked_action_step_ids from current store for that result) |
| Toggle action step | `toggleSavedActionStep(resultId, stepId)` | Update `user_lens_results.checked_action_step_ids` for that result_id |
| Save toolkit edit | `saveToolkitEdit(id, markdown)` | Upsert `user_toolkit_edits` |
| Add WWMD session | `addWWMDSession()` | Optional: insert into `user_recent_lens_activity` |

Prefer **optimistic UI**: update the store immediately, then call Supabase; on failure, revert or show a toast and retry.

### 2.3 When user signs out

- **Option A (simplest):** Do not clear the store. Local state stays as “anonymous” data. Next time they sign in, overwrite with server data (so they see their account data, not the previous anonymous session).
- **Option B:** On sign-out, clear only the “user-backed” slices (savedFactIds, savedLensResults, savedActionSteps, toolkitEdits) so the next session starts clean. Optional: offer “Import from this device” on next login to push local data to server once.

Recommendation: **Option A** for now; overwrite on login with server data.

### 2.4 First-time login (optional: migrate local to server)

If the user had been using the app anonymously and then signs in, you can offer “Sync this device’s saved items to your account?” and one-time insert local store data into Supabase (only for rows the server doesn’t already have). Then reload from server so the store is the union or server-wins.

---

## 3. Frontend Implementation Outline

### 3.1 Supabase client

Already have `supabase` and `useAuth()`. No change needed for auth.

### 3.2 Sync layer (single place for “user data” I/O)

- **Option A — Hook:** e.g. `useUserDataSync()` that:
  - Subscribes to `user` from `useAuth()`.
  - On `user` set: fetches all four (or three) tables and hydrates the store.
  - Exposes “persist” helpers that the store or components can call when the user is signed in (e.g. `persistSavedFact(factId)`, `persistLensResult(result)`, etc.).
- **Option B — Store middleware / wrapper:** Keep store actions; inside each action, if `user` is present, also call Supabase. That requires the store to know `user` (e.g. pass it in, or read from a small auth context/store).

Recommendation: **Option B** with a small “auth context” or reading `user` from `useAuth()` inside a custom hook that wraps the store’s actions and adds Supabase calls. Alternatively, a single `useUserDataSync()` that:
1. On login: fetches and hydrates.
2. Provides no new API: instead, **intercept or patch** the existing store actions so that when the user is signed in, after the store update they also run the Supabase write. Easiest: a `useEffect` that subscribes to store changes and, when `user` is present, syncs to Supabase (debounced or on specific keys). That can get messy; cleaner is to add a thin layer that each “save” action calls (e.g. `syncToSupabase('savedFactIds', ...)`) or to call Supabase directly inside the existing actions by getting `user` from a module-level or React context.

Simplest structure:

- **`services/supabaseUserData.ts`** (or `api/userData.ts`):  
  - `fetchUserSavedFacts(userId)`, `fetchUserLensResults(userId)`, `fetchUserToolkitEdits(userId)`  
  - `upsertSavedFact(userId, factId)`, `removeSavedFact(userId, factId)`  
  - `upsertLensResult(userId, resultId, payload, checkedStepIds)`, `updateLensResultCheckedSteps(userId, resultId, checkedStepIds)`  
  - `upsertToolkitEdit(userId, templateId, markdown)`  
  All use `supabase.from('...').select/insert/upsert/delete` with RLS (so only own rows).

- **Hydration on login:** In a `useEffect` that depends on `user`: if `user`, call the fetch functions and then update the store (e.g. `useStore.getState()` and set `savedFactIds`, `savedLensResults`, etc.). Do this in a single place (e.g. Layout or a `UserDataSync` component that uses `useAuth()` and the new service).

- **Write-through:** Wherever the store is updated (FactDetail toggle, WWMD save result, ResponseView toggle step, Toolkit save edit), after the store update, if `user` is present, call the corresponding Supabase function. You can do this by:
  - Adding a hook `usePersistUserData()` that returns wrapped versions of `toggleSavedFact`, `saveLensResult`, etc., that update the store and then call the Supabase service; or
  - Keeping the store as-is and in each component that mutates (FactDetail, WWMD, ResponseView, Toolkit), call the Supabase service after the store update when `useAuth().user` is set.

### 3.3 Store shape

Keep the current store shape. No need for “source of truth” flags; the source of truth when signed in is Supabase, and the store is a cache that we hydrate on login and update optimistically on write.

### 3.4 Loading and errors

- **On login:** Show a short “Syncing…” in Profile or a global bar until the first fetch completes. Then render as usual.
- **On write failure:** Toast “Could not sync; retry later” and optionally retry or leave the store as-is (user still sees their action; next login might overwrite if you don’t retry).

---

## 4. Implementation Order (Prerequisites First)

1. **Supabase:** Create tables and RLS (1.2–1.4; 1.1 and 1.5 optional).
2. **Frontend — service:** Add `supabaseUserData.ts` with fetch and write functions for saved facts, lens results, toolkit edits.
3. **Frontend — hydration:** On auth change (user set), fetch and hydrate store; run once on app load if already signed in (handled by `getSession` + `onAuthStateChange`).
4. **Frontend — write-through:** After each store mutation, if user is signed in, call the corresponding Supabase write. Prefer doing this in one place (e.g. wrapped store actions or a small hook used by the mutating components).
5. **Optional:** Profile table, recent lens activity table, “import from this device” on first login.

---

## 5. Files to Add/Touch

| Area | File | Change |
|------|------|--------|
| Supabase | Dashboard SQL | Create tables + RLS (and optional trigger). |
| Frontend | `src/services/supabaseUserData.ts` (new) | Fetch/upsert/delete for saved facts, lens results, toolkit edits. |
| Frontend | `src/hooks/useUserDataSync.ts` (new) or logic in Layout/App | On `user` set, fetch and hydrate store. |
| Frontend | `src/store/useStore.ts` | No change to shape; optionally call sync from a wrapper or leave writes to components. |
| Frontend | `src/pages/FactDetail.tsx` | After `toggleSavedFact`, if user, call supabaseUserData. |
| Frontend | `src/pages/WWMD.tsx` | After `saveLensResult`, if user, call supabaseUserData. |
| Frontend | `src/components/wwmd/ResponseView.tsx` | After `toggleSavedActionStep`, if user, call supabaseUserData. |
| Frontend | Toolkit edit save (wherever `saveToolkitEdit` is used) | After save, if user, call supabaseUserData. |

---

## 6. Summary

- **Tables:** `user_saved_facts`, `user_lens_results` (payload JSONB + checked_action_step_ids), `user_toolkit_edits`; optional `profiles`, `user_recent_lens_activity`.
- **RLS:** All tables `for all using (auth.uid() = user_id)`.
- **Sync:** Hydrate store on login; write-through to Supabase on every relevant mutation when signed in; anonymous data stays in localStorage until overwritten on next login.
- **UI:** Same store and components; add a small sync layer and optional “Syncing…” / error toasts.

This keeps the app’s existing mental model (single store, same UI) while adding Supabase as the persistent, per-user backend when the user is signed in.
