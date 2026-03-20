# Final Scope V1

## Project Name

AI Investment Strategy Advisor

## One-Sentence Positioning

An AI-powered investment planning system that generates personalized long-term portfolio strategies based on a user's financial profile, goals, risk preference, and current market conditions, then estimates the probability of reaching those goals.

## Core Product Idea

The product is not a stock-price predictor and not a generic finance chatbot.

The product helps a user answer a more practical question:

> Given my income, savings ability, goal, time horizon, and risk preference, what investment strategy should I follow today, and how likely am I to reach my target?

## Primary User Flow

1. The user enters financial profile data.
2. The system interprets the user's goal, investment horizon, and risk preference.
3. The system generates a base portfolio strategy.
4. The system detects the current market regime.
5. The system adjusts the portfolio allocation to reflect market conditions.
6. The system runs Monte Carlo simulations.
7. The system returns a recommended strategy, allocation, and probability of success.
8. The system explains the recommendation in plain English.

## User Inputs

- age
- annual income
- current savings
- monthly contribution
- savings rate
- target goal amount
- investment horizon in years
- risk preference

## Main Outputs

- recommended strategy profile
- base asset allocation
- market-aware adjusted allocation
- current market regime
- probability of achieving the goal
- median, pessimistic, and optimistic portfolio outcomes
- plain-English explanation

## What The Project Is

- a goal-based investment planning advisor
- a market-aware portfolio recommendation engine
- a financial simulation product
- a portfolio-grade AI/ML system design project

## What The Project Is Not

- not a stock-price prediction project
- not a trading bot
- not a brokerage integration platform
- not a generic LLM wrapper
- not a pure risk-classification demo

## V1 Functional Scope

### Included

- user profile intake
- goal and horizon capture
- risk preference capture
- base strategy generation
- market regime detection
- market-aware allocation adjustment
- Monte Carlo probability estimation
- recommendation explanation
- dashboard-based demo flow

### Excluded

- real brokerage execution
- live trade automation
- tax optimization
- advanced retirement planning logic
- portfolio rebalancing engine
- multi-user authentication
- supervised ML risk prediction model

## Intelligence Layers In V1

### Strategy Layer

Builds the base portfolio recommendation using user inputs and risk preference.

### Market Layer

Interprets the current market regime and adjusts allocation accordingly.

### Simulation Layer

Estimates the likelihood of reaching the target goal under uncertain market paths.

### Explanation Layer

Converts the recommendation into a plain-language summary suitable for a user-facing assistant.

## Why This Version Is Strong

This scope is intentionally focused on product value rather than adding ML models for their own sake.

It demonstrates:

- financial domain thinking
- simulation-based reasoning
- modular backend architecture
- portfolio strategy design
- user-facing AI product thinking

## Definition Of Done For V1

V1 is complete when:

1. A user can enter a realistic financial profile and target goal.
2. The app returns a strategy and allocation that reflect both user preferences and market conditions.
3. The app estimates goal-achievement probability through simulation.
4. The dashboard presents the result clearly with charts and recommendation text.
5. The README explains the product in a way that is easy for recruiters and hiring managers to understand.
