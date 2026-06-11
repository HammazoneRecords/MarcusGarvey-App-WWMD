# UI Layout & Flow Observations — 2026-06-10

Follow-up Playwright pass on the dev frontend (localhost:5175): dismissed the name-entry modal first, then walked through nav click-through flows (bottom tab bar on mobile, sidebar on desktop) and the full WWMD submit → response flow with a real query. Screenshots in `C:/tmp/marcus-shots/flow-*.png` (local scratch, not committed).

## Findings

1. ~~Bottom nav bar overlaps page content on mobile.~~ **False positive** — verified by scrolling to the real bottom of `/home` in-viewport (non-fullPage screenshot): `<main>` already has `pb-24` and the bottom nav sits cleanly below all content. The earlier "overlap" was a Playwright `fullPage: true` screenshot artifact with `position: fixed` elements (Chromium repeats fixed elements at their viewport position when stitching full-page screenshots). No fix needed.

2. **WWMD textarea pre-fill produces garbled text when a user clicks before typing.** The form pre-fills "Marcus, what would you do if " and an effect calls `setSelectionRange` to put the cursor at the end on mount. But if the user clicks anywhere inside the textarea first (very natural — most people click into a field before typing), the click repositions the cursor to wherever they clicked, and their typed text gets inserted there. In this test, clicking the textarea then typing "I want to start a small farming cooperative..." produced:
   > "Marcus, what would you**I want to start a small farming cooperative with my neighbors but we have no funding.** do if"
   The prefix got split apart ("you" / "do if") with the user's sentence jammed in the middle. This would go straight to the LLM as the situation text. Recommend either: (a) render the prefix as static, non-editable text outside/before the textarea and let the textarea only hold the user's continuation, or (b) on every focus/click, snap the cursor to end-of-text if it falls within the prefix range.

3. **Character counter doesn't count the pre-filled prefix.** On page load, the textarea contains "Marcus, what would you do if " (30 chars) but the counter reads "0/4000". It only starts counting once the user's `useWatch`-tracked value updates (and at that point includes the full, possibly-garbled string per #2). Minor but confusing — counter should reflect actual textarea content from the start.

4. ~~Knowledge Base and Toolkit pages get stuck in a skeleton-loading state on client-side (SPA) navigation.~~ **False positive** — re-tested with a 5s wait after clicking "Knowledge Base": content loads correctly (article cards render, "SEARCHING..." clears). The original 500ms wait in the first flow pass just wasn't long enough for the `/api/library` fetch to resolve. No fix needed; the loading skeleton works as intended.

5. **WWMD end-to-end flow works correctly.** Filled the form, submitted, watched the "Searching archives... Ns" loading state count up, and the response view rendered all expected sections in order: "What Marcus Would Do" (principle), historical analogy, the new TTS early-access banner, "What He'd Have You Do" (action steps with checkboxes), "Grounded Receipts" (citations), and "Marcus Asks You" (mirror questions). No console/page errors during the whole flow.

6. **Desktop sidebar label is actually "Garvey Lens (WWMD)"**, not plain "Garvey Lens" as it appeared in the lower-resolution screenshot from the previous pass — correcting that earlier note. The page header/breadcrumb above the `/wwmd` content still says "Garvey Lens" alone though (no "(WWMD)"), so there's still a small inconsistency between the sidebar label and the in-page header.

7. **"Ask Marcus" (Chat) empty state has a lot of unused vertical space on desktop** — the centered prompt ("Ask Marcus anything...") sits in a large mostly-empty panel with a big gap before the input bar at the bottom. Not broken, but worth a look if the page feels sparse compared to other screens.

## Not checked
- Chat send flow (typing a message and getting a reply) — only the empty state was captured this pass.
- Mobile WWMD response screen interactions (checking off action steps, copy/share buttons, TTS lead form submission).
- Tablet breakpoints.
