# AI Investment Strategy Advisor

An AI-powered investment planning system that helps users turn a financial goal into a realistic long-term portfolio strategy.

Instead of predicting random stock prices, the system focuses on a more practical problem: how a user should invest based on income, savings behavior, risk preference, time horizon, and current market conditions.

## Recruiter Snapshot

This project is designed to showcase:

- applied AI/ML thinking for market-aware strategy generation
- probabilistic financial modeling with Monte Carlo simulation
- production-style backend engineering with FastAPI
- product thinking for a realistic fintech AI use case
- clear separation between financial logic, ML logic, and explanation layer

If you review only one part of this repository, start with the architecture and example API flow below.

## Why This Project

Most portfolio projects stop at either:

- a toy ML notebook
- a simple chatbot wrapper
- a stock-price prediction demo with weak product value

This project is intentionally different. It is built as a realistic AI/ML system:

- user financial profile intake
- goal-based portfolio construction
- market regime detection
- adaptive asset allocation
- Monte Carlo portfolio simulation
- goal-achievement probability estimation
- plain-English recommendation generation

The goal is to demonstrate applied machine learning, financial modeling, backend engineering, and product thinking in one end-to-end system.

## Product Vision

The user enters:

- age
- income
- current savings
- savings rate
- monthly contribution
- target financial goal
- investment horizon
- risk preference

The system then:

- interprets the user's goals and risk preference
- generates a base portfolio strategy
- detects the current market regime
- adjusts allocation to reflect market conditions
- runs Monte Carlo simulations
- estimates probability of reaching the target
- explains the recommendation in plain English

This is closer to a lightweight robo-advisor MVP than a generic finance chatbot.

## V1 Scope

The MVP focuses on:

- collecting a user financial profile
- assigning a risk profile
- generating a base portfolio allocation
- detecting the current market regime from market data
- adjusting the allocation based on that regime
- estimating the probability of reaching a financial goal
- returning a clear explanation suitable for a financial planning assistant

## Why This Is Strong For ML Roles

This repository demonstrates:

- `ML thinking`: regime analysis and probabilistic simulation
- `system design`: modular services instead of one notebook
- `domain knowledge`: portfolio allocation, risk, regime-based adaptation
- `backend skills`: API design, schemas, orchestration layer
- `product sense`: user-centric output, interpretability, realistic use case

For ML Engineer or Applied AI roles, this is much closer to production work than classic beginner portfolio projects.

## Example User Question

> I am 28, earn $90,000 per year, have $15,000 in savings, can invest $800 per month, and want to reach $500,000 in 25 years. What strategy should I follow?

## Example Outcome

The system returns:

- `risk_profile`: moderate
- `market_regime`: high_volatility
- `base_portfolio`: 60% stocks / 30% bonds / 10% REITs
- `adjusted_portfolio`: more defensive allocation
- `goal_probability`: probability of reaching the target under simulated market paths
- `explanation`: plain-English summary of why the strategy fits the user

## System Design

```text
User Profile
    -> Risk Profiling
    -> Base Portfolio Allocation
    -> Market Regime Detection
    -> Adaptive Allocation
    -> Monte Carlo Simulation
    -> Goal Probability Estimation
    -> Natural-Language Recommendation
```

## Architecture Overview

```text
app/
  main.py             FastAPI entrypoint
  schemas.py          request/response models
  advisor.py          orchestration layer
  risk_profile.py     user risk classification
  portfolio.py        base and adaptive allocation logic
  market_regime.py    market regime detection
  monte_carlo.py      goal probability simulation
  explanation.py      recommendation narrative
  config.py           portfolio assumptions and settings
```

## ML Components

### 1. Risk Profiling

The current MVP uses interpretable portfolio logic driven by the user's financial profile, goal, and risk preference.

This keeps the first version product-focused and explainable, while leaving room for more advanced ML components later.

### 2. Market Regime Detection

The system uses historical market data and features such as:

- rolling returns
- rolling volatility
- momentum
- drawdown

It then applies clustering to identify regimes such as:

- bull
- bear
- sideways
- high volatility

### 3. Monte Carlo Simulation

The simulation engine estimates the probability of reaching a long-term financial goal under many possible return paths.

This moves the project beyond fixed deterministic calculators and introduces realistic uncertainty into planning outcomes.

## Tech Stack

- Python
- FastAPI
- pandas
- numpy
- scikit-learn
- yfinance
- plotly

## API Output

The API returns:

- user risk profile
- base portfolio allocation
- current market regime
- adjusted allocation
- goal achievement probability
- projected portfolio value
- scenario summary
- plain-English explanation

## Demo Flow

The ideal demo flow for this project is:

1. user enters a profile and goal
2. API returns a personalized investment plan
3. dashboard shows portfolio allocation, market regime, and goal probability
4. user sees a plain-English explanation of the recommendation

This is the flow the repository is being built around.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the interactive API docs at `http://127.0.0.1:8000/docs`.

To run the dashboard:

```bash
streamlit run dashboard.py
```

## Example Request

```json
{
  "age": 28,
  "annual_income": 90000,
  "savings_rate": 0.15,
  "current_savings": 15000,
  "monthly_contribution": 800,
  "goal_amount": 500000,
  "investment_horizon_years": 25,
  "risk_preference": "medium"
}
```

## Example Endpoint

```bash
curl -X POST "http://127.0.0.1:8000/advisor/plan" ^
  -H "Content-Type: application/json" ^
  -d "{\"age\":28,\"annual_income\":90000,\"savings_rate\":0.15,\"current_savings\":15000,\"monthly_contribution\":800,\"goal_amount\":500000,\"investment_horizon_years\":25,\"risk_preference\":\"medium\"}"
```

## What This Project Signals

This project is intentionally designed to be portfolio-grade:

- combines finance domain knowledge with ML/AI
- shows system design instead of isolated notebooks
- demonstrates reasoning about uncertainty, risk, and outcomes
- can be extended into a full product with dashboarding and user sessions

## Planned Demo Assets

To make the project recruiter-friendly, the next steps are:

- add a dashboard UI
- add screenshots and a short demo GIF
- add one or two polished example scenarios
- add charts for allocation and projected goal outcomes

## Future Improvements

- train a supervised risk profiling model
- add macroeconomic features to market regime detection
- support ETF-level recommendations
- add stress testing and rebalancing suggestions
- build an interactive frontend dashboard

## Disclaimer

This project is for educational and portfolio purposes only and does not provide financial advice.
