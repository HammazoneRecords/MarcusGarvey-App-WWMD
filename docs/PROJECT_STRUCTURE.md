# Whirlwind KB — Project Architecture

**Version**: 2.1  
**Date**: 2026-02

## Overview

Whirlwind KB is a monorepo: a React frontend (Vite + TypeScript + Tailwind) and a Python backend (Flask API + RAG engine). They communicate via REST API; session JSON in `sessions/` is used for chat history and optional vault-style exchange.

## Directory Structure

### Root
| File/Folder | Purpose |
|:------------|:--------|
| `frontend/` | React app (Vite, TS, Tailwind, PWA) |
| `backend/` | Python API, RAG, nodes DB, testing panel DB |
| `sessions/` | Session JSON; testing panel state JSON in `sessions/testing_panel/` |
| `docs/` | Project documentation |
| `ask_marcus.bat` | CLI entry for RAG queries |
| `.env` | API keys and optional overrides |

### Frontend (`/frontend`)
| Path | Purpose |
|:-----|:--------|
| `src/pages/` | Home, Library (Knowledge Base), WWMD, Toolkit, Profile, FactDetail, TemplateDetail |
| `src/services/api.ts` | API client (library, facts, WWMD, source section, testing panel) |
| `src/store/useStore.ts` | Zustand store (theme, saved facts, toolkit edits, apiConfig, Lens history) |
| `src/components/layout/` | Layout, GlobalSidebar, BottomNav |
| `src/testing-panel/` | Testing panel (checklist + notes), config and types |
| `src/mock/db.json` | Seed data for sources/facts/daily/templates when backend not used |
| `vite.config.ts` | Vite + PWA manifest (Whirlwind KB) |

### Backend (`/backend`)
| Path | Purpose |
|:-----|:--------|
| `api/server.py` | Flask app: /api/chat, /api/wwmd, /api/library, /api/library/facts/:id, /api/source/:anchor_id, /api/testing-panel, /api/health, sessions |
| `api/nodes_db.py` | Nodes DB init, seed from db.json, get_library() |
| `data/memory.db` | RAG SQLite (anchors, chunks) |
| `data/nodes.db` | Nodes SQLite (nodes, sources, claims, claim_sources); created on first library use |
| `data/testing_panel.db` | Testing panel state (storage_key, checked_json, notes_json) |
| `data/testing_panel_schema.sql` | Testing panel table schema |
| `migrations/` | 001 node spec (Postgres + SQLite), 002 anchor/chunk links |
| `ragbox/scripts/wwmd_ask_hybrid.py` | RAG + citation injection for chat and WWMD |
| `ingestion/`, `tools/` | Document pipeline and utilities |

## Workflows

### Development
1. **Backend**: `npm run dev:backend` (or `python backend/api/server.py`) → http://localhost:5050  
2. **Frontend**: `npm run dev:frontend` → http://127.0.0.1:5173 (proxies /api to backend)  
3. With `VITE_API_BASE_URL` set, Knowledge Base and testing panel use backend; otherwise mock/localStorage.

### Build & Preview
- `npm run build` → builds frontend to `frontend/dist/`  
- `npm run preview` → serves dist at http://127.0.0.1:4173  

### Deployment (vision)
- Frontend: static build to CDN  
- Backend: containerize Flask + RAG (e.g. FastAPI wrapper)
