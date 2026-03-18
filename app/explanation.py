from app.schemas import MarketRegime, SimulationSummary


def build_explanation(
    risk_profile: str,
    market_regime: MarketRegime,
    adjusted_portfolio: dict[str, float],
    simulation: SimulationSummary,
    goal_amount: float,
    investment_horizon_years: int,
) -> str:
    allocation_text = ", ".join(
        f"{asset} {weight:.0%}" for asset, weight in adjusted_portfolio.items()
    )
    probability = simulation.probability_of_reaching_goal

    if probability >= 0.8:
        feasibility = "has a strong likelihood of success"
    elif probability >= 0.6:
        feasibility = "looks achievable but still carries meaningful uncertainty"
    else:
        feasibility = "may require a higher contribution, longer horizon, or more risk tolerance"

    return (
        f"You were classified as a {risk_profile} investor. "
        f"The current market regime is {market_regime.replace('_', ' ')}, so the portfolio is adjusted to {allocation_text}. "
        f"Based on the simulation, this plan {feasibility}: the probability of reaching ${goal_amount:,.0f} "
        f"over {investment_horizon_years} years is {probability:.0%}, with a median projected portfolio value of "
        f"${simulation.median_terminal_value:,.0f}."
    )
