from typing import Literal

from pydantic import BaseModel, Field, computed_field


RiskPreference = Literal["low", "medium", "high"]
RiskProfile = Literal["conservative", "moderate", "aggressive"]
MarketRegime = Literal["bull", "bear", "sideways", "high_volatility"]


class UserProfile(BaseModel):
    age: int = Field(..., ge=18, le=100)
    annual_income: float = Field(..., gt=0)
    savings_rate: float = Field(..., ge=0, le=1)
    current_savings: float = Field(..., ge=0)
    monthly_contribution: float = Field(..., ge=0)
    goal_amount: float = Field(..., gt=0)
    investment_horizon_years: int = Field(..., ge=1, le=50)
    risk_preference: RiskPreference

    @computed_field
    @property
    def monthly_income(self) -> float:
        return self.annual_income / 12


class MarketSnapshot(BaseModel):
    regime: MarketRegime
    latest_close: float
    annualized_volatility: float
    momentum_63d: float
    drawdown_126d: float
    as_of: str


class SimulationSummary(BaseModel):
    probability_of_reaching_goal: float
    median_terminal_value: float
    pessimistic_terminal_value: float
    optimistic_terminal_value: float
    expected_annual_return: float
    annual_volatility: float


class AdvisorResponse(BaseModel):
    risk_profile: RiskProfile
    base_portfolio: dict[str, float]
    market_regime: MarketRegime
    market_snapshot: MarketSnapshot
    adjusted_portfolio: dict[str, float]
    simulation: SimulationSummary
    explanation: str
