# Dev 3 Merge Notes

Merged `origin/main` (Dev 1 + Dev 2) into `dev3-feature`.

## Port

- **Backend**: `8000` (unchanged, `backend/run.py`)

## Changes Made

### 1. Backend (`backend/app/main.py`)

- Added repo root to `sys.path` so backend can import `scoutr` (Dev 3)
- Included Dev 3 export router: `POST /export` for PDF scouting reports
- Extended `GET /comparables` to accept `player_id` for Dev 3 PDF export

### 2. Orchestrator (`backend/app/agents/orchestrator.py`)

- Wired in Dev 3 Tactical Fit Agent
- `assemble_node` calls `evaluate_tactical_fit()` for each candidate
- Fills `tactical_fit_score`, `fit_explanation`, `heatmap_zones`, `formation_compatibility` in dossiers

### 3. Dependencies (`backend/requirements.txt`)

- Added `weasyprint` (PDF export)
- Added `anthropic` (optional Tactical Fit LLM fallback)

## Running

```bash
# Install backend deps (includes Dev 1/2/3)
cd backend && pip install -r requirements.txt

# Run backend (port 8000)
cd backend && python run.py
```

Dev 3 agents use `http://localhost:8000` for `/player/{id}` and `/comparables`.

## Tests

Dev 3 unit tests (70 passed):

```bash
python -m pytest tests/ -v
```
