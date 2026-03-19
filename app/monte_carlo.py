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

    for month in range(months):
        portfolio_values = (portfolio_values + contribution) * (1 + random_returns[:, month])
        if (month + 1) % 12 == 0:
            yearly_snapshots.append(portfolio_values.copy())

    probability = float(np.mean(portfolio_values >= profile.goal_amount))
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
        median_terminal_value=round(float(np.percentile(portfolio_values, 50)), 2),
        pessimistic_terminal_value=round(float(np.percentile(portfolio_values, 10)), 2),
        optimistic_terminal_value=round(float(np.percentile(portfolio_values, 90)), 2),
        expected_annual_return=round(expected_annual_return, 4),
        annual_volatility=round(annual_volatility, 4),
        yearly_projection=yearly_projection,
    )
