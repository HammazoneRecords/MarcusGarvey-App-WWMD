# Whirlwind KB / MarcusGarvey-App-WWMD — Big Picture

One doc to read to understand the whole app: what it is, how it's laid out, how the main flows work, and what's currently broken vs. working. For deep architecture/file-level detail see `PROJECT_STRUCTURE.md`. For raw screenshots from the audit behind this doc, see `UI_SCREEN_OBSERVATIONS_2026-06.md` and `UI_FLOW_OBSERVATIONS_2026-06-10.md`.

## What this app is

**Whirlwind KB** ("Marcus Garvey ARK") is a source-grounded research/companion app built around Marcus Garvey's writings, speeches, and the history of the U.N.I.A. It's a React (Vite + TS + Tailwind, PWA) frontend talking to a Python Flask + RAG backend. Two AI-driven features sit at the center:

- **"What Would Marcus Do?" (WWMD / Garvey Lens)** — user describes a real situation, Marcus answers in first person with a principle, a historical analogy from his own life, concrete action steps, grounded citations ("receipts"), and reflective questions back to the user.
- **"Ask Marcus" (Chat)** — open-ended Q&A with Marcus, tuned to be conversational for small talk and to give fuller archive-grounded answers for real questions.

Everything else (Knowledge Base / Library, Toolkit templates, Profile, Daily Reflection on Home) supports those two core features with research material, organizational templates, and saved-state.

## Screen map

| Route | Nav label (sidebar/bottom) | Purpose |
|---|---|---|
| `/home` | Home | Daily Reflection quote, Quick Actions (Ask WWMD, Browse Knowledge Base, Open Toolkit, Community*), Research Highlight article, archival image gallery |
| `/wwmd` | "Garvey Lens (WWMD)" (sidebar) / "Lens" (bottom nav) | The WWMD form + response view |
| `/chat` | "Ask Marcus" (sidebar) / "Chat" (bottom nav) | Free-form chat with Marcus |
| `/library` | Knowledge Base | Searchable/filterable archive of articles, claims, and saved Lens results |
| `/toolkit` | Toolkit | Organizational templates (study circle curriculum, budget templates, bylaws, etc.) |
| `/profile` | Profile | Saved facts/templates count, display mode toggle, offline pack (coming soon), DevOps link, email sign-in |
| `/browse`, `/workflow`, `/log`, `/devops` | none — not in any nav | Render fine but aren't linked from anywhere visible; likely admin/dev scaffolding — confirm if intentional |
| `/privacy`, `/terms` | footer links | Legal pages |
| `/auth/verify` | — | Magic-link sign-in completion |
| `/facts/:id`, `/toolkit/:id` | — | Detail views for a library fact / toolkit template |

\* "Community" quick action is visibly disabled/greyed — coming soon.

## First-run experience

Every fresh session shows a "Hail, freedom fighter" modal asking what Marcus should call the user (name → personalizes responses) before anything else, with a "Skip for now" escape hatch. This modal currently appears over **every** route including `/privacy` and `/terms`.

## Core user flows

**WWMD flow (primary feature):**
1. Land on `/wwmd` → textarea is pre-filled with "Marcus, what would you do if " and focused.
2. User completes the sentence, picks Lens Mode (Personal / Community).
3. Submit → "Searching archives... Ns" loading state with elapsed timer.
4. Response renders: principle ("What Marcus Would Do"), historical analogy, **TTS early-access signup banner** (new), action steps ("What He'd Have You Do") with checkboxes, grounded receipts/citations, and mirror questions ("Marcus Asks You"). Copy/Share/Start Over controls at top.
- Verified end-to-end working with no console errors.

**Chat flow:**
1. `/chat` shows an empty state ("Ask Marcus anything...") with input bar pinned at bottom.
2. Backend prompt now branches by message type: short reply for greetings/banter, principle→modern-equivalent bridge when user pushes back ("that's 2026, history can't help"), full multi-paragraph answer for real questions.
- Chat send/response interaction itself wasn't re-tested visually this pass (only empty state).

**Browse/research flow:**
- Home → Quick Actions → Knowledge Base or Toolkit. Both pages render correct content on a full page load, but currently get stuck on a "SEARCHING..." skeleton state when navigated to via in-app links (see Known Issues).

## Known issues (as of 2026-06-10)

**Fixed this session:**
1. ~~**WWMD textarea pre-fill garbling**~~ — FIXED. Cursor/selection is now clamped to never land inside the "Marcus, what would you do if " prefix, so clicking anywhere in the textarea and typing can no longer split the prefix apart.
2. ~~**Char counter shows "0/4000"**~~ — FIXED. `useWatch` now reflects the form's actual default value, so the counter correctly shows `29/4000` on load.

**Confirmed false positives (no fix needed):**
- ~~Knowledge Base & Toolkit stuck on "SEARCHING..."~~ — re-tested with a longer wait (5s); content loads correctly via client-side nav too. The original test just didn't wait long enough for the `/api/library` fetch.

**Copy/naming inconsistencies (low priority):**
4. Leftover **"Garvey Lens"** references in `/profile` copy (Data Disclaimer, Architectural Boundary) — the rest of the WWMD feature was renamed to "What Would Marcus Do" / "WWMD" this session, but profile copy wasn't updated.
5. Page header above `/wwmd` content still reads "Garvey Lens" while the `<h1>` below it reads "What Would Marcus Do?" — and the sidebar label is "Garvey Lens (WWMD)". Three slightly different names for the same feature.
6. Bottom-nav icons: "Chat" tab uses a kiosk/robot icon, "Lens" tab uses a speech-bubble icon — arguably backwards (speech bubble reads as "chat").

**Confirmed NOT bugs:**
- Dark mode is an in-app toggle (moon icon, top-right / Profile → Display Mode), not OS `prefers-color-scheme` — working as designed.
- Bottom nav does **not** actually overlap content on mobile — earlier appearance of overlap was a Playwright full-page-screenshot artifact with `position: fixed` elements; verified clean via real viewport scroll.

**To confirm with Deego:**
- Are `/browse`, `/workflow`, `/log`, `/devops` intentional (admin tools) or leftover scaffolding to remove from routing?
- Marcus's speech-phrase vocabulary for the prompt — pending Deego pulling examples from YouTube (logged as FW-2026-06-09-004).

## Pending feature work
- TTS ("hear Marcus speak") — early-access banner + lead capture is live on the WWMD response screen (`/api/leads/tts`, `tts_leads` table). Actual TTS playback not yet built.
