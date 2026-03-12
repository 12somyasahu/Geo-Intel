# GEO·INTEL — Geopolitical Market Intelligence Dashboard

> Every BUY/SELL signal is fully explainable — drillable from signal back to exact source article, keyword scorer breakdown, and LLM step-by-step reasoning.

![GEO·INTEL Dashboard](https://img.shields.io/badge/status-live-brightgreen) ![Python](https://img.shields.io/badge/python-3.12-blue) ![React](https://img.shields.io/badge/react-18-61dafb) ![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3%2070B-orange)

---

## What It Does

GEO·INTEL ingests real-time geopolitical news, scores countries by conflict risk, and generates explainable market signals — showing not just *what* to trade but *why*, with a full chain of thought from raw headline to BUY/SELL recommendation.

**Key differentiator:** Full explainability chain  
`Raw article → Keyword scorer → GTI score → Narrative cluster → LLM reasoning → Market signal`

---

## Features

- **Live GTI Map** — Geopolitical Tension Index choropleth for 40+ countries, updated every 6 hours via Tavily search
- **3D Globe Toggle** — react-globe.gl with tension spikes, pulsing rings, and animated conflict arcs
- **Explainable Signals** — BUY/SELL signals with expandable Chain-of-Thought reasoning (Groq Llama 3.3 70B)
- **Live Prices + Sparklines** — Real-time prices for WTI, Gold, USD/CNH, MSCI EM via yfinance
- **Country Click Panel** — Click any country for live Tavily + Groq analysis on demand
- **What-If Scenario Engine** — Adjust Oil Shock / Escalation / Cyber sliders and see GTI delta + new signal
- **Narrative Clusters** — Groq-derived macro story arcs linking signals across regions
- **Live Ticker** — Breaking geopolitical headlines with severity badges, refreshed hourly
- **Region + Asset Filters** — Filter signals by region and asset class

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite, Leaflet.js, react-globe.gl, D3.js, Zustand, TailwindCSS |
| Backend | FastAPI + Uvicorn, Python 3.12 |
| LLM | Groq API — Llama 3.3 70B Versatile |
| News/Intel | Tavily Search API |
| Market Data | yfinance (WTI, Gold, Forex, Equities) |
| Scoring | Custom keyword scorer with 5 category weights |
| Caching | File-based JSON cache with TTL (GTI: 6hr, Signals: 24hr, Ticker: 1hr) |

---

## Project Structure

```
Geo-Intel/
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Map/
│       │   │   ├── GeoMap.jsx          # Leaflet choropleth + country click
│       │   │   ├── GlobeView.jsx       # react-globe.gl 3D globe
│       │   │   └── CountryPanel.jsx    # Country analysis panel
│       │   ├── Layout/
│       │   │   ├── Navbar.jsx
│       │   │   ├── Sidebar.jsx         # Signals / Narratives / What-If tabs
│       │   │   └── Ticker.jsx          # Breaking news ticker
│       │   └── Signals/
│       │       └── SignalCard.jsx      # Signal card with live price + CoT
│       ├── services/api.js             # API client
│       └── store/useStore.js           # Zustand global state
└── backend/
    ├── main.py                         # FastAPI app
    ├── models.py                       # Pydantic schemas
    ├── routes/
    │   ├── gti.py                      # GET /api/gti, /api/gti/{iso}
    │   ├── signals.py                  # GET /api/signals
    │   ├── narratives.py               # GET /api/narratives
    │   ├── ticker.py                   # GET /api/ticker
    │   ├── analyze.py                  # GET /api/analyze/{iso}
    │   └── prices.py                   # GET /api/prices/{ticker}
    └── services/
        ├── gti_cache.py                # Live GTI scoring via Tavily
        ├── signal_cache.py             # Signal generation via Tavily + Groq
        ├── narrative_cache.py          # Narrative clustering via Groq
        ├── ticker_cache.py             # Breaking news via Tavily
        ├── scorer.py                   # Keyword scorer (5 categories)
        ├── groq_llm.py                 # Groq signal generator
        ├── price_service.py            # Live prices via yfinance
        └── tavily_search.py            # Tavily search client
```

---

## Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Groq API key — [console.groq.com](https://console.groq.com)
- Tavily API key — [app.tavily.com](https://app.tavily.com)

### Backend

```bash
cd Geo-Intel
python -m venv backend/venv
backend/venv/Scripts/activate  # Windows
pip install -r backend/requirements.txt
```

Create `backend/.env`:
```
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

```bash
uvicorn backend.main:app --reload --port 8000
```

First boot generates all caches (~45 seconds). Subsequent starts are instant.

### Frontend

```bash
cd frontend
npm install
# Download world.geojson to frontend/public/world.geojson
npm run dev
```

> **world.geojson** is not included in the repo (14MB). Download from [naturalearth.com](https://www.naturalearthdata.com/) or any GeoJSON world boundaries source.

---

## API Endpoints

| Method | Endpoint | Description | Cache TTL |
|--------|----------|-------------|-----------|
| GET | `/api/gti` | All country GTI scores | 6 hours |
| GET | `/api/gti/{iso}` | Single country GTI | 6 hours |
| GET | `/api/signals` | Active market signals | 24 hours |
| GET | `/api/narratives` | Macro narrative clusters | 24 hours |
| GET | `/api/ticker` | Breaking news events | 1 hour |
| GET | `/api/prices/{ticker}` | Live price + sparkline | 5 minutes |
| GET | `/api/analyze/{iso}` | On-demand country analysis | — |
| POST | `/api/analyze/{iso}/scenario` | What-If scenario scoring | — |
| POST | `/api/*/refresh` | Force cache refresh | — |

---

## How The GTI Score Works

1. **Tavily** searches for recent conflict/security news for each country
2. **Keyword scorer** categorizes headlines into 5 buckets: `conflict`, `energy`, `trade`, `cyber`, `monetary`
3. Each bucket has weighted keywords — matches accumulate into a raw score
4. Score is normalized to 0-100 and mapped to `LOW / MEDIUM / HIGH / CRITICAL`
5. Active war zones (RU, UA, IR, IL, PS) have a minimum floor score

---

## What-If Engine

Adjust scenario multipliers per category:
- **Oil Shock** — amplifies energy keyword weights → WTI, XLE signals
- **Escalation** — amplifies conflict weights → Gold, CHF safe-haven signals  
- **Supply Chain** — amplifies trade weights → shipping ETF signals
- **Cyber Threat** — amplifies cyber weights → HACK, BUG ETF signals
- **Rate Change** — amplifies monetary weights → bond, USD signals

Delta = Scenario GTI − Baseline GTI. Groq generates a new signal for the scenario context.

---

## Portfolio Context

Built as a demonstration of:
- Real-time data pipeline architecture (Tavily → scorer → LLM → cache)
- Explainable AI for financial signals
- Full-stack deployment (FastAPI + React)
- Geospatial visualization (Leaflet + react-globe.gl)

**Author:** Somya Sahu | [LinkedIn](https://www.linkedin.com/in/12somyasahu/) | [GitHub](https://github.com/12somyasahu)