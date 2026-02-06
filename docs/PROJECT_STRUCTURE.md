# Marcus Garvey App (WWMD) - Project Architecture

**Version**: 2.0 (Monorepo)
**Date**: 2025-12-30

## Overview
This repository uses a Monorepo structure to separate the React Frontend from the Python Intelligence Engine. They communicate via the "Session Vault" (JSON file exchange).

## Directory Structure

### 📂 Root Level
| File/Folder | Purpose |
| :--- | :--- |
| `frontend/` | The React Application (Vite + TS + Tailwind) |
| `backend/` | The Python ARK Engine (RAG + Logic) |
| `sessions/` | **The Bridge**: JSON data exchange folder |
| `docs/` | Project Documentation & Logs |
| `ask_marcus.bat` | **Main Entry**: Run queries via terminal |
| `.env` | Global Configuration (API Keys) |

### 📂 Frontend (`/frontend`)
| Path | Purpose |
| :--- | :--- |
| `src/pages/ArkPage.tsx` | The WWMD Interface |
| `src/services/ArkService.ts` | Polls the Vault API |
| `src/components/layout/` | Global Layout & Navigation |
| `package.json` | Frontend Dependencies |

### 📂 Backend (`/backend`)
| Path | Purpose |
| :--- | :--- |
| `scripts/wwmd_ask_hybrid.py` | **Core Engine**: RAG + Citation Injection |
| `scripts/serve_vault.py` | **API Bridge**: Serves `sessions/` content |
| `data/memory.db` | SQLite + Vector Database |

## Workflows

### 1. The "Gliding" Loop (Development)
1.  **Run Backend**: `ask_marcus "Query"` -> Generates JSON in `sessions/`.
2.  **Serve Bridge**: `python backend/scripts/serve_vault.py` -> Exposes JSON.
3.  **Run Frontend**: `cd frontend && npm run dev` -> React App polls Bridge.

### 2. Deployment (Vision)
-   **Frontend**: Build to static HTML/JS (`npm run build`).
-   **Backend**: Wrap `wwmd_ask_hybrid.py` in a FastAPI container.
