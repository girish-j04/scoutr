# ScoutR Backend (Dev 1 Data & API Layer)

This directory contains the data pipeline and the FastAPI REST layer for the ScoutR platform. It is designed to act as the source of truth for the LangGraph agents built by Dev 2 and Dev 3.

## Setup Instructions

To run this backend locally so your agents can hit `http://127.0.0.1:8000`:

1. **Install Dependencies**
   ```bash
   cd scoutr-backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the Data Ingestion Pipelines**
   Ensure you have cloned StatsBomb open data to `data_pipeline/data/statsbomb/` first.
   ```bash
   # 1. Loads real player stats into local ChromaDB
   python3 data_pipeline/ingest_statsbomb.py
   
   # 2. Mocks FBref scraping to avoid IP bans during hackathon, stores in SQLite
   python3 data_pipeline/scrape_fbref.py
   
   # 3. Seeds the 'Golden Path' demo fallback
   python3 data_pipeline/seed_golden_path.py
   ```

3. **Start the API Server**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, the interactive interactive Swagger UI is available at:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Key Details for Dev 2 & 3:
- Send `POST /search` your Claude-parsed query object. It utilizes a "Smart Mapping" system, so you can send natural language positions like "Right-Back" or "Attacking Midfielder" and the API will dynamically translate it to match the rigorous StatsBomb labels.
- Call `GET /player/{id}` to fetch a single massive dictionary combining on-pitch performance stats (`xG`, `pressures`) with financial context (`contract_expiry`, `market_value`).
- If at any point the live queries fail or take too long during the 10-minute demo crunch, passing `"left-back"` and `"Championship"` into the `/search` endpoint will instantly return the pre-cached **Golden Path** object to keep the demo flawless.
