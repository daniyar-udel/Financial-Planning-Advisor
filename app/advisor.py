from app.explanation import build_explanation
from app.logger import get_logger
from app.market_regime import detect_market_regime
from app.monte_carlo import run_goal_simulation
from app.portfolio import (
    build_base_strategy,
    build_recommended_strategy,
)
from app.risk_profile import determine_strategy_profile
from app.schemas import AdvisorResponse, UserProfile

log = get_logger(__name__)


def build_advice(profile: UserProfile) -> AdvisorResponse:
    log.info("Building advice | age=%d horizon=%dy goal=$%.0f risk=%s",
             profile.age, profile.investment_horizon_years, profile.goal_amount, profile.risk_preference)

    strategy_profile = determine_strategy_profile(profile)
    log.info("Strategy profile determined: %s", strategy_profile)

    base_strategy = build_base_strategy(strategy_profile)
    market_snapshot = detect_market_regime()
    log.info("Market regime detected: %s (as_of=%s)", market_snapshot.regime, market_snapshot.as_of)

    recommended_strategy = build_recommended_strategy(
        strategy_profile,
        market_snapshot.regime,
    )
    simulation = run_goal_simulation(
        profile,
        recommended_strategy.expected_annual_return,
        recommended_strategy.annual_volatility,
    )
    log.info("Simulation complete | probability=%.1f%% median_value=$%.0f",
             simulation.probability_of_reaching_goal * 100, simulation.median_terminal_value)

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
