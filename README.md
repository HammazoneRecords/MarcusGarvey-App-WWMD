# Garvey Compass

> **"A people without the knowledge of their past history, origin and culture is like a tree without roots."** — Marcus Garvey

A full-stack, source-grounded intelligence platform rooted in the philosophy of Marcus Garvey. This application combines a modern React frontend with a Python-powered RAG (Retrieval-Augmented Generation) backend to deliver historically accurate, citation-backed wisdom.

---

## ✨ Features

### 🏠 Daily Reflection
Curated quotes and historical context from verified sources, delivered fresh each day to inspire and educate.

### 📚 Library
A searchable, filterable database of historical claims—each backed by **Receipts** (primary source citations) to ensure integrity.

### 🧭 WWMD (Garvey Lens)
**"What Would Marcus Do?"** — An AI-powered decision assistant providing principle-based counsel with historical analogies. All responses are **source-grounded**, never fabricated.

### 🛠️ Toolkit
Organization-building templates with an interactive local editor. Save and customize templates for community work.

### 👤 Profile
Personalized dashboard to manage saved facts, preferences, and your learning journey.

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
| `api/server.py` | Flask API Server (Chat, WWMD Lens, sessions, health) |
| `requirements.txt` | Flask, flask-cors, pymupdf (install from `backend/`) |
| `migrations/` | PostgreSQL Node Specification schema (optional) |
| `ragbox/scripts/wwmd_ask_hybrid.py` | Core RAG Engine with citation injection |
| `data/memory.db` | SQLite + Vector database |
| `ragbox/` | RAG system modules |
| `ingestion/` | Document processing pipeline |
| `tools/` | Utility scripts and validators |

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
- Frontend: Vite dev server at **http://127.0.0.1:5173** (proxies `/api` to backend). When `VITE_API_BASE_URL` is set, Library loads facts from the backend; otherwise it uses mock `db.json`.

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

---

## 📖 Workflow

### The "Gliding" Loop (Development)
1. **Run Backend**: `ask_marcus "Query"` → Generates JSON in `sessions/`
2. **Serve Bridge**: `python backend/scripts/serve_vault.py` → Exposes JSON via API
3. **Run Frontend**: `cd frontend && npm run dev` → React polls the bridge

### Deployment Vision
- **Frontend**: Build to static HTML/JS, deploy to CDN
- **Backend**: Wrap `wwmd_ask_hybrid.py` in FastAPI container

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

## 🔌 API Endpoints (Future/Backend Integration)

| Endpoint | Description |
|:---------|:------------|
| Endpoint | Description |
|:---------|:------------|
| `POST /api/chat` | Main RAG chat endpoint (Prosecutor's Standard) |
| `POST /api/wwmd` | Garvey Lens analysis (Principle + Action Steps) |
| `GET /api/history` | List past sessions |
| `GET /api/session/<filename>` | Retrieve specific session |

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

*Garvey Lens is source-grounded counsel, not impersonation.*
