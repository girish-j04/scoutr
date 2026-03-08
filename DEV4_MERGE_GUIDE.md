# Dev 4 Merge Guide

Use this doc to merge Dev 4 work into ScoutR. Assumes Dev 4 has built the **Sporting Director Copilot UI** (frontend).

---

## 1. Current Structure

```
scoutr/
├── backend/                    # Single deployable API (port 8000)
│   ├── app/
│   │   ├── main.py             # FastAPI app, routes, CORS
│   │   ├── agents/             # Query parser, Scout, Valuation, Orchestrator
│   │   ├── services/           # ChromaDB, SQLite, CSV
│   │   └── schemas.py
│   ├── scoutr/                 # Dev 3 domain logic (agents, export, scoring)
│   │   ├── agents/             # Tactical Fit, Monitoring
│   │   ├── api/                # export_router
│   │   ├── export/             # PDF service
│   │   └── scoring/
│   ├── data_pipeline/
│   ├── run.py
│   └── requirements.txt
├── tests/                      # Unit + integration
└── docs (ScoutR.md, MERGE_NOTES, etc.)
```

- `backend/` is the single deployable tree. All backend code lives here.
- `backend/` is added to `sys.path` so `scoutr` and `app` are importable.
- No `scoutr-backend/` (removed). No top-level `scoutr/` package.

---

## 2. API Endpoints (Dev 1–3)

| Method | Path | Purpose |
|--------|------|---------|
| GET | /health | Health check |
| GET | / | Root |
| POST | /search | ChromaDB player search |
| GET | /player/{id} | Single player profile |
| GET | /comparables | Comparable transfers (target_fee or player_id) |
| POST | /query | Full AI dossier (batch) |
| POST | /query/stream | SSE stream of reasoning + result |
| POST | /export | PDF scouting report (Dev 3) |

All served at `http://localhost:8000`.

---

## 3. How to Merge Dev 4

### Option A: Frontend as sibling to backend

```
scoutr/
├── backend/
├── frontend/          # Dev 4 UI (e.g. React, Next.js, Vite)
└── tests/
```

- Add `frontend/` at repo root.
- Document how to run both (e.g. `backend` on 8000, `frontend` on 3000).
- Frontend calls `http://localhost:8000` for API.

### Option B: Frontend inside backend (monolith)

```
backend/
├── app/
├── scoutr/
├── static/            # Serve built frontend
└── templates/
```

- Build frontend and serve from FastAPI static/templates.
- Add static mount in `backend/app/main.py`.

### Option C: Separate deploy (frontend elsewhere)

- Frontend is its own repo or Vercel/Netlify app.
- Point it at `https://your-scoutr-api.com`.
- No structural changes in this repo.

---

## 4. Files to Touch

| If Dev 4 needs… | Edit |
|-----------------|------|
| New API route | `backend/app/main.py` |
| CORS for new origin | `backend/app/main.py` (CORSMiddleware) |
| New agent in orchestration | `backend/app/agents/orchestrator.py` |
| New schema/request model | `backend/app/schemas.py` |
| New dependency | `backend/requirements.txt` |

---

## 5. Path & Imports

- `backend/` is on `sys.path` (set in `main.py` and `tests/conftest.py`).
- Use `from app.xyz` for backend app code.
- Use `from scoutr.xyz` for Dev 3 logic (agents, export, scoring).

---

## 6. Run & Test

```bash
# Backend
cd backend && pip install -r requirements.txt
cd backend && python run.py

# Tests (from repo root)
python -m pytest tests/ -v
```

Tests expect `backend/` on path; `tests/conftest.py` handles that.

---

## 7. Contracts (Dev 4 → Backend)

See `INTEGRATION_CONTRACTS.md` for:

- `POST /export` request/response
- Player schema expected by Tactical Fit
- Monitoring alerts schema
- Golden path player IDs (1001, 1002, 1003)

---

## 8. Environment

- Copy `backend/.env.example` to `backend/.env`.
- Set `GEMINI_API_KEY` for full AI flow.
- Dev 4 frontend may need its own env (e.g. `VITE_API_URL`).

---

## 9. Checklist for Dev 4 Merge

- [ ] Merge `dev4-feature` into `main` (or open PR)
- [ ] Add `frontend/` (or chosen layout) to repo
- [ ] Add run instructions to `README.md` or this guide
- [ ] CORS: allow frontend origin in `backend/app/main.py` if needed
- [ ] Run `pytest tests/` — all pass
- [ ] Smoke test: backend on 8000, frontend calls `/query` and `/export`
