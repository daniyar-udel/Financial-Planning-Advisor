from __future__ import annotations

import numpy as np

from app.config import settings
from app.schemas import ProjectionPoint, SimulationSummary, UserProfile


def run_goal_simulation(
    profile: UserProfile,
    expected_annual_return: float,
    annual_volatility: float,
    runs: int | None = None,
) -> SimulationSummary:
    runs = runs or settings.simulation_runs
    months = profile.investment_horizon_years * 12

    monthly_return = (1 + expected_annual_return) ** (1 / 12) - 1
    monthly_volatility = annual_volatility / np.sqrt(12)

    random_returns = np.random.normal(
        loc=monthly_return,
        scale=monthly_volatility,
        size=(runs, months),
    )

    portfolio_values = np.full(shape=runs, fill_value=profile.current_savings, dtype=float)
    contribution = profile.monthly_contribution
    yearly_snapshots: list[np.ndarray] = []

    growth_from_initial = np.full(shape=runs, fill_value=profile.current_savings, dtype=float)
    contribution_sensitivity = np.zeros(shape=runs, dtype=float)

    for month in range(months):
        monthly_growth = 1 + random_returns[:, month]
        portfolio_values = (portfolio_values + contribution) * monthly_growth
        growth_from_initial = growth_from_initial * monthly_growth
        contribution_sensitivity = (contribution_sensitivity + 1.0) * monthly_growth
        if (month + 1) % 12 == 0:
            yearly_snapshots.append(portfolio_values.copy())

    probability = float(np.mean(portfolio_values >= profile.goal_amount))
    near_goal_probability = float(np.mean(portfolio_values >= profile.goal_amount * 0.9))
    median_terminal_value = float(np.percentile(portfolio_values, 50))
    median_goal_gap = median_terminal_value - profile.goal_amount
    required_monthly_contribution = _estimate_required_monthly_contribution(
        goal_amount=profile.goal_amount,
        terminal_growth_from_initial=growth_from_initial,
        terminal_contribution_sensitivity=contribution_sensitivity,
        target_probability=0.8,
    )
    yearly_projection = [
        ProjectionPoint(
            year=index + 1,
            pessimistic_value=round(float(np.percentile(values, 10)), 2),
            median_value=round(float(np.percentile(values, 50)), 2),
            optimistic_value=round(float(np.percentile(values, 90)), 2),
        )
        for index, values in enumerate(yearly_snapshots)
    ]

    return SimulationSummary(
        probability_of_reaching_goal=round(probability, 4),
        probability_of_reaching_90_percent_of_goal=round(near_goal_probability, 4),
        median_terminal_value=round(median_terminal_value, 2),
        median_goal_gap=round(median_goal_gap, 2),
        pessimistic_terminal_value=round(float(np.percentile(portfolio_values, 10)), 2),
        optimistic_terminal_value=round(float(np.percentile(portfolio_values, 90)), 2),
        expected_annual_return=round(expected_annual_return, 4),
        annual_volatility=round(annual_volatility, 4),
        required_monthly_contribution_for_80_percent_success=round(required_monthly_contribution, 2),
        yearly_projection=yearly_projection,
    )


def _estimate_required_monthly_contribution(
    goal_amount: float,
    terminal_growth_from_initial: np.ndarray,
    terminal_contribution_sensitivity: np.ndarray,
    target_probability: float,
) -> float:
    safe_sensitivity = np.maximum(terminal_contribution_sensitivity, 1e-9)
    required_contributions = (goal_amount - terminal_growth_from_initial) / safe_sensitivity
    clipped = np.maximum(required_contributions, 0.0)
    return float(np.quantile(clipped, target_probability))
