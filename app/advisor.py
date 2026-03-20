from app.explanation import build_explanation
from app.market_regime import detect_market_regime
from app.monte_carlo import run_goal_simulation
from app.portfolio import (
    build_base_strategy,
    build_recommended_strategy,
)
from app.risk_profile import determine_strategy_profile
from app.schemas import AdvisorResponse, UserProfile


def build_advice(profile: UserProfile) -> AdvisorResponse:
    strategy_profile = determine_strategy_profile(profile)
    base_strategy = build_base_strategy(strategy_profile)
    market_snapshot = detect_market_regime()
    recommended_strategy = build_recommended_strategy(
        strategy_profile,
        market_snapshot.regime,
    )
    simulation = run_goal_simulation(
        profile,
        recommended_strategy.expected_annual_return,
        recommended_strategy.annual_volatility,
    )
    explanation = build_explanation(
        strategy_profile=strategy_profile,
        market_regime=market_snapshot.regime,
        recommended_allocation=recommended_strategy.allocation,
        simulation=simulation,
        goal_amount=profile.goal_amount,
        investment_horizon_years=profile.investment_horizon_years,
    )

    return AdvisorResponse(
        strategy_profile=strategy_profile,
        base_strategy=base_strategy,
        market_regime=market_snapshot.regime,
        market_snapshot=market_snapshot,
        recommended_strategy=recommended_strategy,
        simulation=simulation,
        explanation=explanation,
    )
