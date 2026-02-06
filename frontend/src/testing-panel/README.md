# Testing Feature Panel (reusable)

Right-sidebar QA panel: page-aware checklist of features/CTAs. Check off items as you test; progress is saved in `localStorage` and shown per-page and overall. A **Notes** section at the bottom lets you add bullet points (one per line) for follow-ups, e.g. “Info on /facts/fact-bsl to adjust”; notes are persisted under the same `storageKey`.

## Use in this project

The panel is wired in `Layout.tsx` with `testingPanelConfig`. Toggle with the chevron to collapse to a narrow strip.

## Attach to another site

1. **Copy these files** into the other project:
   - `types.ts`
   - `TestingPanel.tsx`
   - `testingPanelConfig.ts` (then replace with your own config)

2. **Define your config** in `testingPanelConfig.ts`:
   - `siteName`: display name
   - `storageKey`: unique key for `localStorage` (e.g. `myapp-testing-panel`) so it doesn’t clash with this site
   - `pages`: array of `{ path, label, items: [{ id, label }] }`
   - Use exact `path` (e.g. `"/"`, `"/dashboard"`) or a path prefix (e.g. `"/facts"` for `/facts/123`). The panel matches the current route to show the right list.

3. **Render the panel** in your root layout (or a wrapper):
   ```tsx
   import { TestingPanel } from './testing-panel';
   import { testingPanelConfig } from './testing-panel/testingPanelConfig';

   <TestingPanel config={testingPanelConfig} visible={true} />
   ```

4. **Optional:** Show only in dev or when `?testing=1`:
   ```tsx
   visible={import.meta.env.DEV || new URLSearchParams(location.search).has('testing')}
   ```

## Config path matching

- Exact: `path === pathname` (e.g. `"/"`, `"/library"`).
- Prefix: for paths like `/facts/42`, use `path: "/facts"` (with trailing slash in config for “Template Detail” style: `"/toolkit/"`). The panel matches when `pathname.startsWith(path)` after exact match fails.
