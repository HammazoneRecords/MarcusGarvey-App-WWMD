# UI Screen Observations — 2026-06-09

Playwright pass over every route on the dev frontend (localhost:5175), mobile (430x900, light + dark) and desktop (1440x900) for the key screens. Screenshots saved to `C:/tmp/marcus-shots/` (not committed — local scratch only). No console or page errors were thrown on any of the 12 routes in either color scheme.

Routes covered: `/home`, `/library`, `/wwmd`, `/chat`, `/toolkit`, `/profile`, `/browse`, `/workflow`, `/log`, `/devops`, `/privacy`, `/terms`.

## Findings

1. **"Hail, freedom fighter" name-entry modal blocks every screen, including legal pages.** On a fresh session (no name set), the modal appears centered over `/privacy` and `/terms` as well as the main app screens. Visitors can't read the Privacy Policy or Terms of Use without first dismissing a "what shall Marcus call you?" prompt. Worth considering whether `/privacy` and `/terms` should be exempt from this gate, since they're often checked by people who haven't engaged with the product yet.

2. **Dark mode appears visually identical to light mode across all screens.** Setting `colorScheme: 'dark'` in the browser context produced pixel-identical screenshots to light mode on every route (modal, home, wwmd, chat, etc.). This suggests the app's dark mode is driven by an explicit in-app toggle/class (not OS `prefers-color-scheme`), so this isn't necessarily a bug — but it means OS-level dark mode preference is not respected by default. Confirm this is the intended behavior.

3. **Leftover "Garvey Lens" naming in the Profile page copy.** The WWMD page itself now correctly shows "What Would Marcus Do?" (title, subtitle, section headers all updated per this session's changes). However, `/profile` still has two references to "Garvey Lens":
   - Data Disclaimer card: *"Garvey Lens is a source-grounded counsel assistant, not a personal impersonation..."*
   - Architectural Boundary section: *"The 'Garvey Lens' assistant provides analysis derived from documented historical principles..."*
   These should probably be updated to "What Would Marcus Do" (or "WWMD") for consistency with the renamed feature.

4. **Desktop sidebar nav still labels the feature "Garvey Lens" with an "(extended)" / "Premium feature"-style sub-label**, and the page header (top-left breadcrumb/title) on `/wwmd` still reads "Garvey Lens" even though the `<h1>` below it reads "What Would Marcus Do?". These are two more places using the old name — likely the `Layout` `title` prop and the sidebar nav config (`App.tsx` route title is `"Garvey Lens"` for `/wwmd`).

5. **Bottom nav icon mismatch (mobile).** The bottom tab bar shows: Home (house), Chat (TV/kiosk-style icon), Lens (speech-bubble icon), Library, Profile. Intuitively the speech-bubble icon reads as "Chat" and the TV/kiosk icon reads as "Ask Marcus"-as-oracle — but they're assigned the other way around. Worth a quick look at whether swapping the Chat and Lens icons would be more intuitive (Lens = magnifying glass / lightbulb type icon, Chat = speech bubble).

6. **`/browse`, `/workflow`, `/log`, `/devops` routes exist and render** (Browse, Workflow, Log, DevOps pages with headers like "Quick actions", "Configuration"), but none of these appear in the bottom nav or the desktop sidebar nav captured in this pass — they may be internal/dev-only routes left over from scaffolding. Confirm whether these should be hidden/removed from production routing or are intentionally admin-only.

7. **WWMD form pre-fill confirmed working.** The textarea on `/wwmd` correctly shows "Marcus, what would you do if " pre-filled with cursor positioned at the end (per this session's change), visible in both the mobile and desktop screenshots.

## Not checked
- Authenticated states (logged-in user, saved lens results, profile with API key configured) — all screenshots were taken as an anonymous/first-visit session.
- The actual WWMD response view / TTS early-access banner rendering (would require submitting a real query and waiting for the LLM response).
- Tablet breakpoints.
