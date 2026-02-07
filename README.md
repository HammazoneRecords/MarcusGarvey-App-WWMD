# Whirlwind KB

> **"A people without the knowledge of their past history, origin and culture is like a tree without roots."** — Marcus Garvey

A full-stack, source-grounded knowledge base inspired by the legacy of Marcus Garvey. Whirlwind KB combines a modern React frontend with a Python-powered RAG (Retrieval-Augmented Generation) backend to deliver historically accurate, citation-backed wisdom.

---

## ✨ Features

### 🏠 Daily Reflection
Curated quotes and historical context from verified sources, delivered fresh each day to inspire and educate.

### 📚 Knowledge Base
A searchable, filterable database of historical claims—each backed by **Receipts** (primary source citations) to ensure integrity. When the backend is running, facts load from the nodes DB; otherwise from bundled mock data.

### 🧭 WWMD (Garvey Lens)
**"What Would Marcus Do?"** — An AI-powered decision assistant providing principle-based counsel with historical analogies. All responses are **source-grounded**, never fabricated.

### 🛠️ Toolkit
Organization-building templates with an interactive local editor. Save and customize templates for community work.

### 👤 Profile
Personalized dashboard: saved facts, theme, **AI/API configuration** (Ollama, Open Router, OpenAI-compatible, Google Gemini), and recent Lens activity.

---

## 🏗️ Architecture

This is a **Monorepo** with three main components that communicate via a **Session Vault** (JSON file exchange):

```
MarcusGarvey App WWMD/
├── frontend/          # React Application (Vite + TypeScript + Tailwind)
├── backend/           # Python ARK Engine (RAG + Vector DB + Logic)
├── sessions/          # The Bridge: JSON data exchange folder
├── docs/              # Project Documentation
├── ask_marcus.bat     # CLI Entry Point for queries
└── .env               # Global Configuration (API Keys)
```

### Frontend (`/frontend`)
| Technology | Purpose |
|:-----------|:--------|
| React 18 + Vite | Fast, modern UI framework |
| TypeScript | Type-safe development |
| TailwindCSS | Utility-first styling |
| Framer Motion | Smooth animations |
| Zustand | State management with persistence |
| React Hook Form + Zod | Form validation |
| Lucide React | Premium icon library |

### Backend (`/backend`)
| Component | Purpose |
|:----------|:--------|
| `api/server.py` | Flask API (Chat, WWMD Lens, library, source viewer, testing panel, sessions, health) |
| `api/nodes_db.py` | Nodes DB: init, seed from db.json, serve library payload |
| `data/memory.db` | RAG SQLite (anchors, chunks) |
| `data/nodes.db` | Nodes SQLite (nodes, sources, claims); created on first `/api/library` use |
| `data/testing_panel.db` | Testing panel SQLite (checklist + notes per storage_key) |
| `migrations/` | Node spec (001) + anchor/chunk links (002); SQLite variants in `*_sqlite.sql` |
| `ragbox/scripts/wwmd_ask_hybrid.py` | Core RAG engine with citation injection |
| `ragbox/`, `ingestion/`, `tools/` | RAG modules, document pipeline, validators |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+
- API key for AI provider (configured in `.env`)

### Set up frontend and backend (from project root)

**1. Install dependencies**
```bash
# Frontend
npm run install:frontend

# Backend (Python)
npm run install:backend
# Or: pip install -r backend/requirements.txt
```

**2. Configure environment**  
Create or edit `.env` in the project root:
```env
GEMINI_API_KEY=your_api_key_here
# or OLLAMA_HOST for local models

# Optional overrides (defaults shown)
ARK_API_HOST=0.0.0.0
ARK_API_PORT=5050

# Development proxy + browser fetch base
VITE_DEV_API=http://localhost:5050
VITE_API_BASE_URL=http://localhost:5050
```

**3. Run both (use two terminals)**

| Terminal 1 — Backend | Terminal 2 — Frontend |
|----------------------|------------------------|
| `npm run dev:backend` | `npm run dev:frontend` |

- Backend: Flask API at **http://localhost:5050** (health: `GET /api/health`, library: `GET /api/library`, fact: `GET /api/library/facts/:id`). On first use it creates `backend/data/nodes.db` from the node schema and seeds it from `frontend/src/mock/db.json` so nodes/sources/claims point to RAG anchors.
- Frontend: Vite dev server at **http://127.0.0.1:5173** (proxies `/api` to backend). When `VITE_API_BASE_URL` is set, the Knowledge Base loads facts from the backend; otherwise it uses mock `db.json`.

---

### Alternative: run from subfolders

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Backend**
```bash
pip install -r backend/requirements.txt
python backend/api/server.py
```

**Option B: CLI Only**
```bash
# Query Marcus directly via terminal
ask_marcus "What would Marcus Garvey say about self-reliance?"
```

### 5. Build for Production
```bash
cd frontend
npm run build
npm run preview  # Test production build locally
```

### 6. Preview (production build locally)
From the **project root**:
```bash
npm run build
npm run preview
```
- Serves the built app from `frontend/dist/` at **http://127.0.0.1:4173** (Vite default).
- Use after frontend changes to verify the production bundle; refresh or clear cache if assets don’t update.

---

## 📖 Workflow

### The "Gliding" Loop (Development)
1. **Run Backend**: `ask_marcus "Query"` → Generates JSON in `sessions/`
2. **Serve Bridge**: `python backend/scripts/serve_vault.py` → Exposes JSON via API
3. **Run Frontend**: `cd frontend && npm run dev` → React polls the bridge

### Deployment (production)

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for full steps. Summary:

- **Environment**: Copy [.env.example](.env.example) to `.env` and set values. Never commit `.env`. For production backend set `CORS_ORIGINS` to your frontend origin(s). For production frontend build set `VITE_API_BASE_URL` to your API URL.
- **Frontend**: `cd frontend && npm run build`; deploy contents of `frontend/dist/` to your static host. Add PWA icons `pwa-192x192.png` and `pwa-512x512.png` to `frontend/public/` before building (see [frontend/public/PWA_ICONS_README.txt](frontend/public/PWA_ICONS_README.txt)).
- **Backend**: Run with a process manager (e.g. gunicorn) behind HTTPS. Use a reverse proxy for TLS.
- **Pre-launch**: Use [docs/PRE_PUBLICATION_CHECKLIST.md](docs/PRE_PUBLICATION_CHECKLIST.md).

---

## 🎨 Design Philosophy

| Principle | Implementation |
|:----------|:---------------|
| **Receipts-First** | Every claim backed by primary source citation |
| **Source-Grounded** | AI responses reference actual texts, never hallucinate |
| **Inclusive & Accessible** | Large tap targets, clear contrast, respectful design |
| **Premium Aesthetic** | Pan-African palette (Green, Gold, Red) in sophisticated tones |
| **Offline-Ready** | PWA support via `vite-plugin-pwa` |

---

## 📂 Data Contracts

Defined in `frontend/src/types/index.ts`:

| Type | Description |
|:-----|:------------|
| `SourceRef` | Citation details (id, title, author, year, type) |
| `Fact` | Verified claims with context and receipts |
| `DailyItem` | Content for daily reflection cards |
| `WWMDRequest/Response` | Schema for Garvey Lens assistant |
| `ToolkitTemplate` | Organization-building document blueprints |

---

## 🔌 API Endpoints

| Endpoint | Description |
|:---------|:------------|
| `POST /api/chat` | Main RAG chat endpoint |
| `POST /api/wwmd` | Garvey Lens analysis (Principle + Action Steps) |
| `GET /api/library` | Knowledge Base: sources + facts (optional filters: `?search=&category=&confidence=`) |
| `GET /api/library/facts/<id>` | Single fact by id |
| `GET /api/source/<anchor_id>` | RAG source section (optional `?locator=`) for citation viewer |
| `GET /api/testing-panel?storage_key=` | Testing panel state (checked, notes) |
| `POST /api/testing-panel` | Save testing panel state (body: `storage_key`, `checked?`, `notes?`) |
| `GET /api/health` | Health check |
| `GET /api/history` | List past sessions |
| `GET /api/session?file=` | Retrieve specific session |
| `GET /api/latest` | Most recent session |

---

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| [docs/PRE_PUBLICATION_CHECKLIST.md](docs/PRE_PUBLICATION_CHECKLIST.md) | Pre-launch checklist |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deployment and env vars |
| [docs/USER_MANUAL.md](docs/USER_MANUAL.md) | User guide |
| [docs/PRIVACY_POLICY.md](docs/PRIVACY_POLICY.md) | Privacy policy (fill contact before publish) |
| [docs/TERMS_OF_USE.md](docs/TERMS_OF_USE.md) | Terms of use (fill contact before publish) |
| [docs/POST_LAUNCH_RUNBOOK.md](docs/POST_LAUNCH_RUNBOOK.md) | Post-launch monitoring and rollback |

**Support**: Set contact details in the privacy policy and terms, and in the app (e.g. footer or Profile) if you offer user support.

---

## 🤝 Contributing

1. Follow the **Script State Protocol** for backend changes
2. Ensure all new facts include proper `SourceRef` citations
3. Run `npm run lint` before committing frontend changes
4. Document any new tools in `backend/docs/`

---

## 📜 License

This project is dedicated to preserving and sharing the wisdom of Marcus Garvey for educational purposes.

---

*Garvey Lens is source-grounded counsel, not impersonation. App name: **Whirlwind KB**.*
