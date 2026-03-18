from app.explanation import build_explanation
from app.market_regime import detect_market_regime
from app.monte_carlo import run_goal_simulation
from app.portfolio import (
    adjust_portfolio_for_market_regime,
    get_base_portfolio,
    get_portfolio_assumptions,
)
from app.risk_profile import classify_risk_profile
from app.schemas import AdvisorResponse, UserProfile


def build_advice(profile: UserProfile) -> AdvisorResponse:
    risk_profile = classify_risk_profile(profile)
    base_portfolio = get_base_portfolio(risk_profile)
    market_snapshot = detect_market_regime()
    adjusted_portfolio = adjust_portfolio_for_market_regime(risk_profile, market_snapshot.regime)
    expected_return, annual_volatility = get_portfolio_assumptions(
        risk_profile,
        market_snapshot.regime,
    )
    simulation = run_goal_simulation(profile, expected_return, annual_volatility)
    explanation = build_explanation(
        risk_profile=risk_profile,
        market_regime=market_snapshot.regime,
        adjusted_portfolio=adjusted_portfolio,
        simulation=simulation,
        goal_amount=profile.goal_amount,
        investment_horizon_years=profile.investment_horizon_years,
    )

    return AdvisorResponse(
        risk_profile=risk_profile,
        base_portfolio=base_portfolio,
        market_regime=market_snapshot.regime,
        market_snapshot=market_snapshot,
        adjusted_portfolio=adjusted_portfolio,
        simulation=simulation,
        explanation=explanation,
    )
