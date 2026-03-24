export type RiskPreference = "low" | "medium" | "high";
export type StrategyProfile = "conservative" | "moderate" | "aggressive";
export type MarketRegime = "bull" | "bear" | "sideways" | "high_volatility";
export type GoalType =
  | "long_term_wealth"
  | "retirement"
  | "home_purchase"
  | "financial_independence"
  | "custom_goal";
export type StressResponse = "buy_more" | "hold" | "sell_some" | "sell_all";
export type StrategyPreference = "classic" | "responsible" | "income_focused";

export interface SignupPayload {
  full_name: string;
  email: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface OnboardingProfilePayload {
  goal_type: GoalType;
  goal_amount: number;
  investment_horizon_years: number;
  age: number;
  date_of_birth: string;
  marital_status: string;
  address: string;
  annual_income: number;
  current_savings: number;
  monthly_contribution: number;
  savings_rate: number;
  risk_preference: RiskPreference;
  stress_response: StressResponse;
  strategy_preference: StrategyPreference;
}

export interface OnboardingProfileResponse extends OnboardingProfilePayload {
  user_id: number;
}

export interface UserProfilePayload {
  age: number;
  annual_income: number;
  savings_rate: number;
  current_savings: number;
  monthly_contribution: number;
  goal_amount: number;
  investment_horizon_years: number;
  risk_preference: RiskPreference;
}

export interface MarketSnapshot {
  regime: MarketRegime;
  latest_close: number;
  annualized_volatility: number;
  momentum_63d: number;
  drawdown_126d: number;
  as_of: string;
}

export interface AllocationSummary {
  strategy_profile: StrategyProfile;
  expected_annual_return: number;
  annual_volatility: number;
  allocation: Record<string, number>;
}

export interface ProjectionPoint {
  year: number;
  pessimistic_value: number;
  median_value: number;
  optimistic_value: number;
}

export interface SimulationSummary {
  probability_of_reaching_goal: number;
  median_terminal_value: number;
  pessimistic_terminal_value: number;
  optimistic_terminal_value: number;
  expected_annual_return: number;
  annual_volatility: number;
  yearly_projection: ProjectionPoint[];
}

export interface AdvisorResponse {
  strategy_profile: StrategyProfile;
  base_strategy: AllocationSummary;
  market_regime: MarketRegime;
  market_snapshot: MarketSnapshot;
  recommended_strategy: AllocationSummary;
  simulation: SimulationSummary;
  explanation: string;
}

export interface StrategyResultResponse {
  onboarding_profile: OnboardingProfileResponse;
  recommendation: AdvisorResponse;
  strategy_horizon_note: string;
  platform_notice: string;
  disclaimer: string;
}
