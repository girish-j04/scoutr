# ScoutR

**Agentic AI Transfer Intelligence for Football Clubs**

---

## What Is ScoutR?

ScoutR is an agentic AI platform that acts as an always-on transfer intelligence engine for football clubs. It watches player data across 50+ leagues, surfaces candidates that match a club's tactical and financial profile, and delivers ready-to-act scouting dossiers automatically.

The core insight is simple: elite clubs like Manchester City and Bayern Munich have 20-person analytics departments doing this work manually. The 300+ clubs in the Championship, Bundesliga 2, Serie B, and MLS are making multi-million euro transfer decisions with Transfermarkt and a spreadsheet. ScoutR changes that.

---

## The Problem It Solves

The transfer market is driven by information asymmetry. A sporting director at a mid-tier club might spend weeks manually filtering players, chasing data across three different tools, and still not know whether a target actually fits their formation or if a competitor is already circling. ScoutR runs that entire process autonomously, 24 hours a day, and surfaces the output in a single interface.

---

## How It Works

ScoutR is built around four AI agents that work together inside a LangGraph orchestration layer:

- **Scout Agent** — Takes a natural language query from the sporting director and translates it into structured search criteria. It runs that search across real player data and returns ranked candidates with full reasoning shown live.
- **Valuation Agent** — Cross-references comparable transfers, contract expiry timelines, and club financial situations to produce a negotiation-ready fee range for each candidate.
- **Tactical Fit Agent** — Scores how well a target player would integrate into the buying club's system. It analyses positional heatmaps, pressing metrics, and formation compatibility, then generates a plain-English explanation.
- **Monitoring Agent** — Sits in the background watching a pre-set list of targets. It sends delta alerts when something changes: a contract situation, a competitor scout spotted, a club entering financial trouble.

A conversational Sporting Director Co-Pilot interface ties all four agents together. The sporting director types a query in plain English, watches the agents reason in real time, and gets back a set of player dossier cards with a one-click PDF export.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Agent Orchestration | LangGraph (Python) | Multi-agent state machines, controllable agent loops |
| LLM | Claude Sonnet 4 via Anthropic API | Reasoning, dossier generation, tactical narrative |
| Vector Store | Chroma (local) or Pinecone (cloud) | RAG over player stats and transfer history |
| Data Sources | StatsBomb Open Data + FBref scraper | Real player names, press metrics, event data |
| Backend | FastAPI (Python) | REST endpoints connecting agents to frontend |
| Frontend | Next.js 14 + Tailwind CSS | Chat interface, dossier cards, pitch diagram |
| Streaming | Server-Sent Events (SSE) | Live agent reasoning shown step by step in UI |
| PDF Export | pdfkit (Python) | Auto-generated scouting report, one-click export |
| Deployment | Vercel (frontend) + Railway (backend) | Fast deploy, no DevOps overhead during hackathon |

---

## Data Sources

- **StatsBomb Open Data** — free, high-quality event data covering pressing metrics, progressive carries, expected goals, and positional data across major leagues
- **FBref** — scraped for contract expiry dates, transfer values, and player biographical data
- **Transfermarkt public data** — comparable transfer fee history used by the Valuation Agent for fee range estimation
