# AI DecisionMate 🧠
### Explainable AI for Real-World Decisions

A full-stack, hackathon-ready **Explainable AI Decision Support System** that helps individuals and companies make better real-world decisions — from laptop selection to company bulk procurement — with full explanations, confidence levels, impact analysis, and what-if scenarios.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (3.14 supported)
- Node.js 18+
- npm 9+

### 1. Backend

```bash
cd backend
py -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The SQLite database (`decisionmate.db`) is created **automatically** on first startup. No migration commands needed.

### 2. Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 🌐 Ports

| Service  | Port |
|----------|------|
| Backend (FastAPI) | **8000** |
| Frontend (Vite/React) | **5173** |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (backend + database) |
| POST | `/analyze` | Free-text decision analysis |
| POST | `/guided-analyze` | Guided questionnaire analysis |
| POST | `/whatif` | What-if analysis with parameter changes |
| POST | `/products` | Product search (demo catalog) |
| POST | `/nearby` | Nearby business search (with fallback) |
| GET | `/history` | Get all decision history |
| GET | `/history/{id}` | Get single history record |
| DELETE | `/history/{id}` | Delete single history record |
| DELETE | `/history` | Delete all history |
| POST | `/counterfactual` | Counterfactual analysis |
| POST | `/impact` | Detailed impact analysis |

Interactive API docs: **http://localhost:8000/docs**

---

## 🏗️ Architecture

```
ai-decisionmate/
├── backend/
│   ├── main.py              # FastAPI app & all endpoints
│   ├── config.py            # Settings & environment variables
│   ├── database.py          # SQLAlchemy + SQLite setup (auto-creates tables)
│   ├── models.py            # ORM models (DecisionHistory)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── decision_engine.py   # Hybrid decision engine
│   ├── explainability.py    # Factor explanation generator
│   ├── impact.py            # Impact analysis engine
│   ├── whatif.py            # What-if analysis engine
│   ├── product_catalog.py   # Built-in demo product catalog
│   ├── business_search.py   # Nearby search (with fallback)
│   ├── history.py           # History CRUD operations
│   ├── requirements.txt     # Python dependencies (pinned)
│   └── .env.example         # Environment variable template
│
└── frontend/
    ├── src/
    │   ├── App.jsx          # Router + health check
    │   ├── main.jsx         # React entry point
    │   ├── api.js           # API client (axios)
    │   ├── components/
    │   │   ├── Navbar.jsx
    │   │   ├── BackendOffline.jsx
    │   │   ├── ConfidenceRing.jsx
    │   │   ├── FactorChart.jsx
    │   │   ├── ProductCard.jsx
    │   │   ├── WhatIfPanel.jsx
    │   │   ├── LoadingSpinner.jsx
    │   │   └── ErrorBanner.jsx
    │   ├── pages/
    │   │   ├── HomePage.jsx
    │   │   ├── GuidedDecisionPage.jsx
    │   │   ├── AskAIPage.jsx
    │   │   ├── ResultPage.jsx
    │   │   ├── HistoryPage.jsx
    │   │   └── HistoryDetailPage.jsx
    │   └── data/
    │       └── categoryQuestions.js
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    └── index.html
```

---

## 🎯 Features

### Two Decision Modes
- **Mode A — Guided Decision**: Select a category (Laptop, Smartphone, Fish/Aquarium, Company Bulk, etc.) and answer structured questions with radio buttons, checkboxes, and number inputs.
- **Mode B — Ask AI**: Type a free-text description and get an analyzed recommendation. Supports budget extraction, quantity detection, and requirement parsing.

### Decision Categories
Laptop · Smartphone · PC/Components · Pet · Fish/Aquarium · Education · Career · Travel · Home · Vehicle · Office Equipment · Product Purchase · Company/Bulk Purchase · General Decision

### Core Capabilities
| Feature | Description |
|---------|-------------|
| **Explainable AI** | Horizontal bar chart of top decision factors with percentage contributions |
| **Confidence Levels** | Ring chart: LOW (<60%) / MEDIUM (60-79%) / HIGH (≥80%) |
| **Impact Analysis** | Immediate, cost, long-term, trade-offs, risks, maintenance |
| **What-If Analysis** | Real-time sliders for budget/performance/quantity with 300ms debounce |
| **Counterfactual** | Finds minimum change to flip the recommendation |
| **Alternatives** | 3 options with trade-off comparison |
| **Demo Products** | 30+ built-in demo catalog items (labeled as demo data) |
| **Nearby Search** | Fallback to search suggestions when no API key |
| **Decision History** | SQLite-persisted, survives page refreshes |
| **History Deletion** | Individual and delete-all with confirmation dialog |
| **Company Bulk** | Multi-unit procurement with estimated cost breakdown |

---

## 🗄️ Database

- **Engine**: SQLite (file: `backend/decisionmate.db`)
- **ORM**: SQLAlchemy 2.0
- **Auto-initialized**: Tables created on first backend startup
- **No migrations needed** for basic demo

### Decision History Schema
```
id          INTEGER PRIMARY KEY
timestamp   DATETIME
category    VARCHAR(100)
user_query  TEXT
recommendation  VARCHAR(500)
confidence  FLOAT
confidence_band VARCHAR(20)
input_data_json TEXT    # Full input as JSON
factors_json    TEXT    # Factor scores as JSON
result_json     TEXT    # Complete result as JSON
```

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env`:

```bash
# Optional: Live nearby search
GOOGLE_MAPS_API_KEY=your_key_here

# Optional: Live product search
SERP_API_KEY=your_key_here
```

**The application runs fully without any API keys.** All features have local fallbacks.

---

## 🛠️ Troubleshooting

### Port already in use
```bash
# Backend
uvicorn main:app --reload --port 8001

# Frontend (update vite.config.js proxy target accordingly)
```

### CORS errors
Ensure the backend is running on port 8000. The frontend's Vite dev server proxies `/api` requests automatically, but direct API calls go to `http://localhost:8000`. Check that `CORS_ORIGINS` in `config.py` includes `http://localhost:5173`.

### Module not found (Python)
```bash
py -m pip install -r requirements.txt
```
If `scikit-learn` fails on Python 3.14+, it's not used for core features — remove it from requirements.txt if needed. The decision engine uses pure Python scoring.

### npm install failures
```bash
cd frontend
npm cache clean --force
npm install
```

### Backend unavailable
The frontend shows a full-page "Backend not running" message with instructions and a Retry button — it will not show a blank page.

### Optional API integrations unavailable
If `GOOGLE_MAPS_API_KEY` is not set, nearby search returns a helpful message with alternative suggestions instead of crashing.

---

## 💡 Innovation Highlights

### Custom Counterfactual Generation
The system incrementally changes important decision factors (e.g., budget in 10% steps, performance level) and re-evaluates the recommendation at each step — stopping when the recommendation changes. This requires no pre-built counterfactual library and works entirely offline.

### Dual Decision Explanation
The system exposes the major weighted factors behind each recommendation as a horizontal bar chart with percentage scores. Multiple alternative options are scored simultaneously, allowing direct trade-off comparison without requiring a user to ask.

### Confidence-Aware Decisions
Confidence is computed as `avg_factor_score × (0.5 + 0.5 × completeness_ratio)`, where completeness measures how many fields were provided. Missing information reduces confidence proportionally — clearly labeled as "Recommendation confidence" to avoid overstating certainty.

### Impact Analysis
Every recommendation includes a structured 6-section impact analysis (Immediate / Cost / Long-term / Trade-offs / Risks / Maintenance) generated from category-specific templates personalized with the user's budget and quantity.

### Real-World Action Layer
Recommendations connect users to a demo product catalog (30+ items) and a nearby search system. When no location API is configured, the system provides targeted search suggestions for Google Maps and authorised dealers instead of showing an error.

### Company Bulk Decision Support
Organizations can enter total budget + quantity to get per-unit cost analysis, estimated total spend, remaining budget, and enterprise-specific recommendations (warranty, delivery, maintenance considerations).

---

## 📝 Notes

- All demo catalog prices are labeled as **estimates** and are not live market data.
- The decision engine is **fully heuristic/rule-based** — it does not use statistical models or SHAP values.
- No personal data beyond decision inputs is stored. No analytics, no tracking.
- The application works completely **offline** except for optional API integrations.
