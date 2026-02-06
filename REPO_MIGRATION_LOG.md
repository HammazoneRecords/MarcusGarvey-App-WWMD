# Repository Migration Log

This document tracks the restructuring of the Marcus Garvey App WWMD repository into a clean monorepo architecture.

**Goal**: Separate Frontend (`React`) from Backend (`Python/ARK`) for better organization.

## Migration Table

| File / Folder Name | Purpose | Location BEFORE | Location AFTER |
| :--- | :--- | :--- | :--- |
| `src/` | Frontend Source Code (React/Vite) | `/src/` | `/frontend/src/` |
| `public/` | Static Assets (Icons, Manifests) | `/public/` | `/frontend/public/` |
| `package.json` | Node Dependencies Configuration | `/package.json` | `/frontend/package.json` |
| `package-lock.json` | Frozen Node Dependencies | `/package-lock.json` | `/frontend/package-lock.json` |
| `vite.config.ts` | Vite Build Configuration | `/vite.config.ts` | `/frontend/vite.config.ts` |
| `tsconfig.json` | TypeScript Configuration | `/tsconfig.json` | `/frontend/tsconfig.json` |
| `tsconfig.node.json` | TypeScript Node Config | `/tsconfig.node.json` | `/frontend/tsconfig.node.json` |
| `postcss.config.js` | CSS Processing Config | `/postcss.config.js` | `/frontend/postcss.config.js` |
| `tailwind.config.js` | Tailwind Config | `/tailwind.config.js` | `/frontend/tailwind.config.js` |
| `index.html` | App Entry Point | `/index.html` | `/frontend/index.html` |
| `node_modules/` | Installed Dependencies | `/node_modules/` | `/frontend/node_modules/` |
| `backend/` | Python ARK Engine & Scripts | `/backend/` | `/backend/` (Unchanged) |
| `.env` | Environment Variables (API Keys) | `/.env` | `/.env` (Root shared) |
| `README.md` | Project Documentation | `/README.md` | `/README.md` (Root) |
| `CHANGELOG.md` | Project History | `/CHANGELOG.md` | `/CHANGELOG.md` (Root) |
| `ask_marcus.bat` | Convenience Script | `/ask_marcus.bat` | `/ask_marcus.bat` (Updated path) |
| `sessions/` | JSON Vault (Shared Data) | `/sessions/` | `/sessions/` (Shared root) |
| `ContextCapsuleBOX/` | AI Memory Storage | `/ContextCapsuleBOX/` | `/ContextCapsuleBOX/` (Root) |

## Implementation Steps

1.  **Create Directory**: `mkdir frontend`
2.  **Move Files**: Move all frontend-specific files into `frontend/`.
3.  **Update Batch File**: Modify `ask_marcus.bat` if it relies on root paths (mostly backend focused, so safe).
4.  **Verify Build**: Run `npm run dev` inside `frontend/`.

## Impact Analysis

-   **Backend**: Unaffected. `backend/` path stays at root.
-   **Frontend**: Requires `cd frontend` before running `npm` commands.
-   **VS Code**: Workspace settings may need to point to `frontend/` root for ESLint/Prettier.
