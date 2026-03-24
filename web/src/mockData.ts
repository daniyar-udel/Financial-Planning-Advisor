import type { AdvisorResponse, UserProfilePayload } from "./types";

export const defaultProfile: UserProfilePayload = {
  age: 28,
  annual_income: 90000,
  savings_rate: 0.15,
  current_savings: 15000,
  monthly_contribution: 800,
  goal_amount: 500000,
  investment_horizon_years: 25,
  risk_preference: "medium",
};

export const mockAdvice: AdvisorResponse = {
  strategy_profile: "moderate",
  base_strategy: {
    strategy_profile: "moderate",
    expected_annual_return: 0.07,
    annual_volatility: 0.13,
    allocation: {
      stocks: 0.6,
      bonds: 0.3,
      reits: 0.1,
    },
  },
  market_regime: "sideways",
  market_snapshot: {
    regime: "sideways",
    latest_close: 0,
    annualized_volatility: 0.16,
    momentum_63d: 0.01,
    drawdown_126d: -0.04,
    as_of: "offline-mode",
  },
  recommended_strategy: {
    strategy_profile: "moderate",
    expected_annual_return: 0.065,
    annual_volatility: 0.13,
    allocation: {
      stocks: 0.55,
      bonds: 0.3,
      reits: 0.15,
    },
  },
  simulation: {
    probability_of_reaching_goal: 0.64,
    probability_of_reaching_90_percent_of_goal: 0.79,
    median_terminal_value: 587043.11,
    median_goal_gap: 87043.11,
    pessimistic_terminal_value: 333123.14,
    optimistic_terminal_value: 1071379.14,
    expected_annual_return: 0.065,
    annual_volatility: 0.13,
    required_monthly_contribution_for_80_percent_success: 980,
    yearly_projection: [
      { year: 1, pessimistic_value: 22421.55, median_value: 25789.54, optimistic_value: 29627.62 },
      { year: 5, pessimistic_value: 58585.68, median_value: 75510.65, optimistic_value: 98113.93 },
      { year: 10, pessimistic_value: 111056.05, median_value: 155441.45, optimistic_value: 222322.38 },
      { year: 15, pessimistic_value: 172531.66, median_value: 260543.66, optimistic_value: 408081.62 },
      { year: 20, pessimistic_value: 247812.49, median_value: 399339.79, optimistic_value: 668421.05 },
      { year: 25, pessimistic_value: 333123.14, median_value: 587043.11, optimistic_value: 1071379.14 },
    ],
  },
  explanation:
    "Based on your profile, a moderate long-term strategy is recommended. The current market regime is sideways, so the portfolio is adjusted to stocks 55%, bonds 30%, reits 15%. Based on the simulation, this plan looks achievable but still carries meaningful uncertainty: the probability of reaching $500,000 over 25 years is 64%, with a median projected portfolio value of $587,043.",
};
