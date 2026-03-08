# ScoutR

### Agentic AI Transfer Intelligence for Football Clubs

**Built at 24-Hour Hackathon | Team of 4 | Claude Code + Cursor**

---

# Part 1: The Product

## What Is ScoutR?

ScoutR is an **agentic AI platform** that acts as an always-on **transfer intelligence engine** for football clubs.

It watches player data across **50+ leagues**, surfaces candidates that match a club's **tactical and financial profile**, and delivers **ready-to-act scouting dossiers automatically**.

The core insight is simple:

Elite clubs like **Manchester City** and **Bayern Munich** have **20-person analytics departments** doing this work manually.

But the **300+ clubs in leagues like the Championship, Bundesliga 2, Serie B, and MLS** are making multi-million euro transfer decisions using **Transfermarkt and spreadsheets**.

ScoutR changes that.

---

# The Problem It Solves

The transfer market is driven by **information asymmetry**.

A sporting director at a mid-tier club might spend:

* Weeks manually filtering players
* Jumping across **3–4 different tools**
* Still not knowing:

  * whether a player actually fits their system
  * whether competitors are already pursuing them

ScoutR runs this **entire process autonomously 24/7** and surfaces the results in **one interface**.

---

# How It Works

ScoutR runs **four AI agents** orchestrated inside **LangGraph**.

### 1. Scout Agent

* Converts natural language queries into structured search criteria
* Searches player databases
* Returns ranked candidates
* Shows reasoning live

### 2. Valuation Agent

* Uses:

  * comparable transfers
  * contract expiry timelines
  * club finances
* Produces a **negotiation-ready fee range**

### 3. Tactical Fit Agent

Evaluates whether a player fits the buying club.

Analyzes:

* positional heatmaps
* pressing metrics
* formation compatibility

Then produces a **plain-English explanation**.

### 4. Monitoring Agent

Runs continuously watching a **target watchlist**.

Alerts when:

* contract situations change
* competitor scouts appear
* clubs face financial trouble

---

## Sporting Director Copilot Interface

The UI provides a **conversational interface** where a sporting director can:

1. Type a query in natural language
2. Watch agents reason in real time
3. Receive **player dossier cards**
4. Export reports with **one-click PDF**

---

# Tech Stack

| Layer               | Technology                          | Why                        |
| ------------------- | ----------------------------------- | -------------------------- |
| Agent Orchestration | LangGraph (Python)                  | Multi-agent state machines |
| LLM                 | Claude Sonnet 4 via Anthropic API   | Reasoning + narratives     |
| Vector Store        | Chroma (local) or Pinecone          | Player data retrieval      |
| Data Sources        | StatsBomb Open Data + FBref scraper | Real player stats          |
| Backend             | FastAPI                             | REST endpoints             |
| Frontend            | Next.js 14 + Tailwind CSS           | Chat + scouting UI         |
| Streaming           | Server-Sent Events                  | Live agent reasoning       |
| PDF Export          | pdfkit                              | Scouting report generation |
| Deployment          | Vercel + Railway                    | Fast hackathon deploy      |

---

# Data Sources

### StatsBomb Open Data

Provides:

* pressing metrics
* progressive carries
* expected goals
* positional event data

### FBref

Scraped for:

* contract expiry
* market values
* player metadata

### Transfermarkt

Used for:

* comparable transfer fees
* valuation agent benchmarks

---

# Part 2: Individual Team Tasks

Each team member owns a **clear vertical slice of the system**.

All four tracks run **in parallel from hour zero**.

---

# Dev 1 — Data & Backend

**Owns**

* Data ingestion
* Vector store
* FBref scraper
* REST API

---

## Hours 0–3

* Clone StatsBomb open data
* Load **3 seasons** of event JSON
* Store embeddings in **Chroma vector store**

Define player schema:

```
player_id
name
club
league
age
position
contract_expiry
market_value
press_metrics
progressive_carries
xA
xG
```

Build FastAPI endpoint:

```
/search
```

Returns matching players.

---

## Hours 3–8

Build **FBref scraper** using:

* BeautifulSoup or
* Playwright

Store contract + market data in **SQLite**.

Add endpoint:

```
/player/{id}
```

Add comparable transfer endpoint:

```
/comparables
```

Using a static Transfermarkt CSV.

---

## Hours 8–13

Complete REST API.

Endpoints must return **clean JSON**.

Create integration test script.

Publish API documentation for Dev 2 and Dev 3.

Seed **Golden Path Dataset**:

Leeds United left-back query.

---

## Hours 13–18

Data QA checks.

Ensure:

* no null values
* all demo players complete

Dev 1 becomes **data support for team**.

---

# Dev 2 — Scout + Valuation Agents

**Owns**

* LangGraph orchestration
* Scout Agent
* Valuation Agent

---

## Hours 0–3

Create LangGraph state schema.

```
query
parsed_criteria
candidate_list
selected_player
dossier
valuation
tactical_fit
monitoring_alerts
```

Build query parser using Claude.

Example output:

```
{
 position: "left-back",
 max_age: 24,
 max_fee: 7000000,
 min_press_score: 0.75,
 contract_expiry_within_months: 12
}
```

Stub Scout Agent.

---

## Hours 3–8

Scout Agent:

1. Calls `/search`
2. Re-ranks results

Scoring weights:

```
tactical_fit: 40%
fee_fit: 30%
contract_urgency: 30%
```

Stream reasoning via **Server Sent Events**.

Example event:

```
{
 step: "Filtering candidates",
 detail: "Applying pressing score threshold"
}
```

---

## Hours 8–13

Build **Valuation Agent**.

Calls:

```
/comparables
```

Calculates:

```
low_fee
mid_fee
high_fee
```

Contract urgency:

* green
* amber
* red

Create Orchestrator chain:

```
Query Parser
 → Scout Agent
 → Valuation Agent
 → Output Assembly
```

---

## Hours 13–18

Integrate **Tactical Fit Agent** from Dev 3.

Confirm output JSON shape.

Run **Golden Path Query end-to-end**.

---

# Dev 3 — Tactical Fit + Monitoring Agents

**Owns**

* Tactical Fit Agent
* Monitoring Agent
* PDF export

---

## Hours 0–3

Define tactical scoring inputs:

* PPDA
* pressure success rate
* defensive actions per 90
* positional heatmap centroid
* formation style

Output:

```
score: 0-100
explanation: text
```

Define formation profiles:

```
4-3-3
4-2-3-1
3-5-2
4-4-2
3-4-3
```

---

## Hours 3–8

Tactical Fit Agent:

1. Fetch player stats via `/player/{id}`
2. Compute score
3. Generate explanation via Claude

Output schema:

```
{
 tactical_fit_score,
 fit_explanation,
 heatmap_zones,
 formation_compatibility
}
```

---

## Hours 8–13

Monitoring Agent.

Input:

```
watchlist: [player_ids]
```

Alerts triggered when:

* contract < 6 months
* competitor scout detected
* club financial trouble

Start **PDF export module** using `pdfkit`.

---

## Hours 13–18

Complete PDF template.

Export endpoint:

```
POST /export
```

Fallback logic:

If data fails → return **golden path dataset**.

---

# Dev 4 — Frontend + Demo Lead

**Owns**

* Full Next.js UI
* Demo narrative

---

## Hours 0–3

Create Next.js 14 + Tailwind project.

Layout:

```
Sidebar: Club Command Center
Main: Chat + Results
```

Club panel includes:

* Leeds United branding
* Squad summary
* Transfer need indicator

---

## Hours 3–8

Build components:

* Agent Reasoning Stream
* Player Dossier Card

Card fields:

* name
* club
* age
* tactical score
* contract risk
* fee range
* key stats chart

---

## Hours 8–13

Build **Tactical Fit Deep Dive panel**.

Includes:

* pitch diagram
* heatmap zones
* pressing comparison

Add **Monitoring Feed** component.

---

## Hours 13–18

Add **PDF export button**.

Preload **Golden Path Demo**.

Polish UI to look like **production SaaS**.

---

# Merge Protocol

1. Dev 1 validates API responses.
2. Dev 2 connects Scout + Valuation agents.
3. Dev 3 integrates Tactical Fit.
4. Dev 4 connects SSE reasoning stream.
5. Run Golden Path demo.
6. Bugs fixed by owning developer.
7. UI locked at hour 18.
8. Final rehearsal at hour 22.

---

# Golden Path Query

```
Find me a left-back under 24, comfortable in a high press,
contract expiring within 12 months, available for under €7M,
preferably from a league with similar intensity to the Championship.
```

Expected output:

* **3 ranked players**
* full dossiers
* fee estimates

---

# 24-Hour Development Timeline

| Time  | Dev 1               | Dev 2              | Dev 3                  | Dev 4            |
| ----- | ------------------- | ------------------ | ---------------------- | ---------------- |
| 0-3   | StatsBomb ingestion | LangGraph skeleton | Tactical scoring model | Next.js scaffold |
| 3-8   | FBref scraper       | Scout Agent        | Tactical Fit Agent     | Dossier UI       |
| 8-13  | Comparables DB      | Valuation Agent    | Monitoring Agent       | Reasoning UI     |
| 13-18 | Data QA             | Orchestrator       | PDF Export             | UI polish        |
| 18-21 | Data support        | Golden path test   | Edge cases             | Design pass      |
| 21-24 | Code freeze         | Code freeze        | Code freeze            | Slides + demo    |

---

# The One Rule

At **hour 18**, Dev 4 **locks the UI**.

No new features.

The goal becomes:

**A flawless 10-minute golden path demo.**

Not a bigger product.
