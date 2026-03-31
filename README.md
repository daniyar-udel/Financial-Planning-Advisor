# AI Investment Strategy Advisor

> A full-stack, market-aware investment planning system powered by ML and LLMs.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript)
![Tests](https://img.shields.io/badge/tests-44%20passed-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What It Does

Most portfolio projects are either a toy ML notebook or a simple chatbot wrapper. This one is different.

Given a user's **age, income, savings, risk tolerance, and financial goal**, the system:

1. Classifies their **risk profile** (conservative / moderate / aggressive)
2. Builds a **base portfolio allocation** (stocks / bonds / REITs / alternatives)
3. Downloads real market data and detects the current **market regime** via KMeans clustering
4. **Adapts the allocation** based on whether the market is bull, bear, sideways, or high-volatility
5. Runs **10,000 Monte Carlo simulations** to estimate goal-achievement probability
6. Generates a **plain-English explanation** of the full recommendation
7. Lets the user ask follow-up questions via an **AI copilot** (LangGraph + Groq)

---

## Live Demo

> 🔗 [vivacious-imagination-production-f472.up.railway.app](https://vivacious-imagination-production-f472.up.railway.app)

---

## Example

**User:** Age 28, $90K income, $15K savings, $800/month contribution, goal $500K in 25 years, medium risk.

**System response:**
```json
{
  "strategy_profile": "moderate",
  "market_regime": "bear",
  "recommended_strategy": {
    "stocks": 0.4,
    "bonds": 0.45,
    "reits": 0.1,
    "gold": 0.05
  },
  "probability_of_reaching_goal": 0.35,
  "median_terminal_value": 409559.00,
  "explanation": "Given current high-volatility conditions, your moderate strategy has been adjusted..."
}
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Data / ML | pandas, numpy, scikit-learn (KMeans), yfinance |
| Simulation | NumPy Monte Carlo (10K paths) |
| AI Copilot | LangGraph, LangChain, Groq (llama-3.3-70b) |
| Auth | JWT (PyJWT), PBKDF2 password hashing |
| Database | SQLite |
| Frontend | React 18, TypeScript, Vite, Recharts |
| Rate Limiting | slowapi |

---

## Architecture

```
User Profile
    ↓
Risk Profiling          → conservative / moderate / aggressive
    ↓
Base Allocation         → stocks / bonds / REITs / alternatives
    ↓
Market Regime           → KMeans on 5y of S&P 500 features
    ↓
Adaptive Allocation     → adjust weights by regime
    ↓
Monte Carlo (10K runs)  → probability of reaching goal
    ↓
AI Explanation          → plain-English recommendation
    ↓
AI Copilot              → LangGraph + Groq for follow-up Q&A
```

---

## Project Structure

```
financial-assistant/
├── app/
│   ├── main.py             # FastAPI app, routes, rate limiting
│   ├── advisor.py          # Orchestration layer
│   ├── risk_profile.py     # Risk classification
│   ├── portfolio.py        # Base & adaptive allocation
│   ├── market_regime.py    # KMeans market regime detection
│   ├── monte_carlo.py      # Goal probability simulation
│   ├── explanation.py      # Natural-language recommendation
│   ├── agent.py            # LangGraph + Groq AI copilot
│   ├── auth.py             # JWT authentication
│   ├── security.py         # Password hashing, token encoding
│   ├── onboarding.py       # User profile persistence
│   ├── database.py         # SQLite connection & schema
│   ├── logger.py           # Centralized logging
│   ├── schemas.py          # Pydantic request/response models
│   └── config.py           # Portfolio presets & settings
├── web/                    # React + TypeScript frontend (Vite)
│   └── src/
│       ├── pages/          # Login, Signup, Onboarding, Strategy, Simulation
│       └── components/     # AICopilot chat widget
├── tests/
│   ├── test_risk_profile.py
│   ├── test_monte_carlo.py
│   ├── test_portfolio.py
│   └── test_market_regime.py
├── .env.example            # Environment variable template
├── requirements.txt
└── dashboard.py            # Streamlit demo (alternative UI)
```

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/signup` | — | Register new user |
| POST | `/auth/login` | — | Login, get JWT token |
| GET | `/auth/me` | JWT | Get current user |
| POST | `/onboarding/profile` | JWT | Save financial profile |
| GET | `/onboarding/profile` | JWT | Load saved profile |
| GET | `/strategy/result` | JWT | Generate full strategy |
| POST | `/agent/chat` | JWT | Chat with AI copilot |
| POST | `/advisor/plan` | — | One-shot strategy (no auth) |
| GET | `/health` | — | Health check |

Interactive docs available at `/docs` after starting the server.

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ (for the React frontend)
- A free [Groq API key](https://console.groq.com)

### 1. Clone & set up environment

```bash
git clone https://github.com/daniyar-udel/Financial-Planning-Advisor.git
cd financial-assistant
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your GROQ_API_KEY and JWT_SECRET
```

Generate a secure JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Run the backend

```bash
uvicorn app.main:app --reload
# API docs → http://127.0.0.1:8000/docs
```

### 4. Run the frontend

```bash
cd web
npm install
npm run dev
# App → http://localhost:5173
```

### 5. Run tests

```bash
pytest tests/ -v
```

---

## What This Demonstrates

| Skill | Evidence |
|---|---|
| ML thinking | KMeans regime detection, probabilistic Monte Carlo |
| System design | Modular pipeline: risk → portfolio → regime → simulation → explanation |
| Backend engineering | FastAPI, JWT auth, rate limiting, structured logging, SQLite |
| AI integration | LangGraph agent, Groq LLM, RAG-ready with ChromaDB |
| Frontend | React 18, TypeScript, Recharts, protected routes |
| Code quality | Pydantic validation, type hints throughout, 44 passing tests |
| Security | PBKDF2 hashing, JWT tokens, env-based secrets |

---

## Future Improvements

- [ ] Train a supervised risk profiling model on historical investor data
- [ ] Add macroeconomic features to market regime detection (CPI, yield curve)
- [ ] Support ETF-level portfolio recommendations
- [ ] Add stress testing and rebalancing simulation
- [ ] Portfolio comparison across multiple strategies

---

## Disclaimer

This project is for educational and portfolio purposes only. It does not constitute financial advice.
