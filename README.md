# ScoutR: Agentic AI Transfer Intelligence

ScoutR is an autonomous, agent-driven transfer intelligence platform for football clubs. Designed for sporting directors, it replaces manual spreadsheet scouting with a unified, natural-language interface. ScoutR continuously monitors 50+ leagues, finds tactical and financial fits, and delivers comprehensive, ready-to-act dossier reports in seconds.

---

## 🏗️ Architecture & Tech Stack

ScoutR is built with a modern, decoupled architecture featuring a Python/FastAPI backend and a React/Next.js frontend. The core intelligence is powered by **Google's Gemini 2.5 Flash** model, orchestrated via **LangGraph**.

### Backend (Transfer Intelligence Engine)
* **Framework Code:** `Python 3.10+`, `FastAPI`
* **Agent Orchestration:** `LangGraph`, `LangChain`
* **AI Model:** `Gemini 2.5 Flash` (via `langchain-google-genai`)
* **Vector Store:** `ChromaDB` (Local embedded for fast similarity search of player metrics)
* **Relational Data:** `SQLite` (Financials, contract expiries, structured player data)
* **Caching Layer:** `MongoDB` (Two-tier query caching for instant repeated query resolution)
* **Streaming:** `sse-starlette` to stream agent reasoning live to the client
* **Deployment:** Hosted on **Vultr** for high-performance, low-latency API execution

### Frontend (Sporting Director Co-Pilot)
* **Framework:** `Next.js 14` (App Router)
* **Styling:** `Tailwind CSS v4`, Custom Native CSS for landing page
* **UI Components:** `React`, `shadcn/ui`, `Framer Motion` (Micro-animations)
* **Data Fetching:** Real-time Server-Sent Events (SSE) parsing for live agent reasoning
* **Export:** One-click PDF Dossier generation via browser print APIs

---

## 🤖 The Four AI Agents

ScoutR operates through four specialized, autonomous agents orchestrated by LangGraph working in parallel:

1. **Scout Agent (Natural Language Search):** 
   Takes a plain-English query (e.g., *"Find me a left-back under 24, comfortable in a high press under €10M"*), parses it into structured criteria using Gemini, and executes a hybrid search against ChromaDB and SQLite.
2. **Valuation Agent (Market Fee Intelligence):** 
   Analyses contract expiry dates, comparable market values, and player age to calculate an estimated, realistic transfer fee range and assess selling club pressure.
3. **Tactical Fit Agent (Formation Compatibility):** 
   Evaluates progressive carries, pressure success rates, and positional data to score how well a player fits the buying club's tactical system (e.g., high-pressing 4-3-3), providing a plain-English tactical summary.
4. **Monitoring Agent (24/7 Target Watch):** 
   *(In Development)* Designed to watch shortlists and send alerts on contract changes, rival scouting activity, or club financial issues.

---

## 🚀 What We've Built So Far

### 1. Robust Data Pipeline & Retrieval
* Built ingestion scripts to process raw StatsBomb event data and Transfermarkt financials.
* Constructed a **ChromaDB vector store** mapping complex positional nuances (e.g. mapping "right-back" queries to "right wing back", "right center back", etc.).
* Implemented a solid fallback mechanism: if ChromaDB is empty, the system automatically falls back to curated mock data.

### 2. High-Performance Streaming Backend
* Implemented a `/query/stream` endpoint in FastAPI that yields Server-Sent Events (SSE).
* Optimized **LangGraph** orchestration to run multiple agent tasks concurrently using `asyncio.gather()`, drastically reducing latency.
* Added a **MongoDB Caching Layer** that hashes query criteria and caches the final dossier output, resulting in near-instantaneous responses for repeated queries.

### 3. Real-Time, Premium Frontend Interface
* Built a stunning, cinematic landing page (`/`) utilizing a scroll-driven canvas frame sequence (192 frames) and glassmorphism styling.
* Developed the `/app` dashboard featuring:
  * A live transfer budget gauge with animated number tickers.
  * A chat interface that streams the agent's "thought process" in real-time (e.g., *"[Agent] Analyzing tactical fit..."*).
  * Beautiful dossier cards displaying the final candidate results, complete with radar-style stats, scout summaries, and fee ranges.
* **Fixed critical frontend streaming bugs**, specifically a CRLF line-ending issue where the SSE parser failed to split `\r\n\r\n` chunks natively, ensuring smooth and reliable UI updates.

### 4. Interactive Feedback & Polishing
* Refined UI aesthetics by ensuring consistent accessibility (e.g., contrasting CTA buttons, bright white helper text).
* Implemented "Export to PDF" functionality directly within the dossier cards.

---

## 🛠️ Local Development Setup

### Backend
1. Navigate to the `backend/` directory: `cd backend`
2. Create and activate a virtual environment: `python -m venv venv` and `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with your API keys:
   ```env
   GEMINI_API_KEY=your_google_ai_key
   MONGO_URI=mongodb://localhost:27017
   ```
5. Run the server: `uvicorn app.main:app --reload --port 8000`

### Frontend
1. Navigate to the `frontend/` directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`
4. Open `http://localhost:3000` to view the landing page, or `http://localhost:3000/app` for the dashboard.

---

*Made for sporting directors who can't afford to be second.*
