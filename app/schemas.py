from typing import Literal

from pydantic import BaseModel, EmailStr, Field, computed_field


RiskPreference = Literal["low", "medium", "high"]
StrategyProfile = Literal["conservative", "moderate", "aggressive"]
MarketRegime = Literal["bull", "bear", "sideways", "high_volatility"]
GoalType = Literal[
    "long_term_wealth",
    "retirement",
    "home_purchase",
    "financial_independence",
    "custom_goal",
]
StressResponse = Literal["buy_more", "hold", "sell_some", "sell_all"]
StrategyPreference = Literal["classic", "responsible", "income_focused"]
AgentMessageRole = Literal["user", "assistant"]


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


class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class OnboardingProfileRequest(BaseModel):
    goal_type: GoalType
    goal_amount: float = Field(..., gt=0)
    investment_horizon_years: int = Field(..., ge=1, le=50)
    age: int = Field(..., ge=18, le=100)
    date_of_birth: str = Field(..., min_length=8, max_length=20)
    marital_status: str = Field(..., min_length=2, max_length=40)
    address: str = Field(..., min_length=5, max_length=200)
    annual_income: float = Field(..., gt=0)
    current_savings: float = Field(..., ge=0)
    monthly_contribution: float = Field(..., ge=0)
    savings_rate: float = Field(..., ge=0, le=1)
    risk_preference: RiskPreference
    stress_response: StressResponse
    strategy_preference: StrategyPreference


class OnboardingProfileResponse(OnboardingProfileRequest):
    user_id: int


class StrategyResultResponse(BaseModel):
    onboarding_profile: OnboardingProfileResponse
    recommendation: "AdvisorResponse"
    strategy_horizon_note: str
    platform_notice: str
    disclaimer: str


class MarketSnapshot(BaseModel):
    regime: MarketRegime
    latest_close: float
    annualized_volatility: float
    momentum_63d: float
    drawdown_126d: float
    as_of: str


class ProjectionPoint(BaseModel):
    year: int
    pessimistic_value: float
    median_value: float
    optimistic_value: float


class AllocationSummary(BaseModel):
    strategy_profile: StrategyProfile
    expected_annual_return: float
    annual_volatility: float
    allocation: dict[str, float]


class SimulationSummary(BaseModel):
    probability_of_reaching_goal: float
    probability_of_reaching_90_percent_of_goal: float
    median_terminal_value: float
    median_goal_gap: float
    pessimistic_terminal_value: float
    optimistic_terminal_value: float
    expected_annual_return: float
    annual_volatility: float
    required_monthly_contribution_for_80_percent_success: float
    yearly_projection: list[ProjectionPoint]


class AdvisorResponse(BaseModel):
    strategy_profile: StrategyProfile
    base_strategy: AllocationSummary
    market_regime: MarketRegime
    market_snapshot: MarketSnapshot
    recommended_strategy: AllocationSummary
    simulation: SimulationSummary
    explanation: str


class AgentChatMessage(BaseModel):
    role: AgentMessageRole
    content: str = Field(..., min_length=1, max_length=4_000)


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4_000)
    history: list[AgentChatMessage] = Field(default_factory=list, max_length=12)


class AgentChatResponse(BaseModel):
    reply: str
    provider: str
    model: str
    fallback_used: bool
    sample_prompts: list[str]


StrategyResultResponse.model_rebuild()
