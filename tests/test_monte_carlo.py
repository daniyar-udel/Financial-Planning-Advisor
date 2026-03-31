import numpy as np
import pytest
from app.schemas import UserProfile
from app.monte_carlo import run_goal_simulation


FAST_RUNS = 500  # keep tests quick


@pytest.fixture
def profile():
    return UserProfile(
        age=30,
        annual_income=80_000,
        savings_rate=0.15,
        current_savings=20_000,
        monthly_contribution=800,
        goal_amount=500_000,
        investment_horizon_years=25,
        risk_preference="medium",
    )


class TestRunGoalSimulation:
    def test_returns_simulation_summary(self, profile):
        np.random.seed(42)
        result = run_goal_simulation(profile, 0.07, 0.13, runs=FAST_RUNS)
        assert result is not None

    def test_probability_between_0_and_1(self, profile):
        np.random.seed(42)
        result = run_goal_simulation(profile, 0.07, 0.13, runs=FAST_RUNS)
        assert 0.0 <= result.probability_of_reaching_goal <= 1.0
        assert 0.0 <= result.probability_of_reaching_90_percent_of_goal <= 1.0

    def test_near_goal_probability_gte_goal_probability(self, profile):
        np.random.seed(42)
        result = run_goal_simulation(profile, 0.07, 0.13, runs=FAST_RUNS)
        assert result.probability_of_reaching_90_percent_of_goal >= result.probability_of_reaching_goal

    def test_pessimistic_lte_median_lte_optimistic(self, profile):
        np.random.seed(42)
        result = run_goal_simulation(profile, 0.07, 0.13, runs=FAST_RUNS)
        assert result.pessimistic_terminal_value <= result.median_terminal_value
        assert result.median_terminal_value <= result.optimistic_terminal_value

    def test_yearly_projection_length_matches_horizon(self, profile):
        np.random.seed(42)
        result = run_goal_simulation(profile, 0.07, 0.13, runs=FAST_RUNS)
        assert len(result.yearly_projection) == profile.investment_horizon_years

    def test_yearly_projection_years_are_sequential(self, profile):
        np.random.seed(42)
        result = run_goal_simulation(profile, 0.07, 0.13, runs=FAST_RUNS)
        years = [p.year for p in result.yearly_projection]
        assert years == list(range(1, profile.investment_horizon_years + 1))

    def test_high_return_increases_success_probability(self, profile):
        np.random.seed(42)
        low = run_goal_simulation(profile, 0.02, 0.05, runs=FAST_RUNS)
        np.random.seed(42)
        high = run_goal_simulation(profile, 0.12, 0.05, runs=FAST_RUNS)
        assert high.probability_of_reaching_goal > low.probability_of_reaching_goal

    def test_impossible_goal_has_low_probability(self):
        np.random.seed(42)
        profile = UserProfile(
            age=60,
            annual_income=30_000,
            savings_rate=0.05,
            current_savings=1_000,
            monthly_contribution=50,
            goal_amount=10_000_000,
            investment_horizon_years=3,
            risk_preference="low",
        )
        result = run_goal_simulation(profile, 0.03, 0.05, runs=FAST_RUNS)
        assert result.probability_of_reaching_goal < 0.05

    def test_certain_goal_has_high_probability(self):
        np.random.seed(42)
        profile = UserProfile(
            age=25,
            annual_income=200_000,
            savings_rate=0.50,
            current_savings=500_000,
            monthly_contribution=5_000,
            goal_amount=100_000,
            investment_horizon_years=20,
            risk_preference="high",
        )
        result = run_goal_simulation(profile, 0.09, 0.18, runs=FAST_RUNS)
        assert result.probability_of_reaching_goal > 0.95

    def test_required_monthly_contribution_is_non_negative(self, profile):
        np.random.seed(42)
        result = run_goal_simulation(profile, 0.07, 0.13, runs=FAST_RUNS)
        assert result.required_monthly_contribution_for_80_percent_success >= 0.0

    def test_median_goal_gap_reflects_median_vs_goal(self, profile):
        np.random.seed(42)
        result = run_goal_simulation(profile, 0.07, 0.13, runs=FAST_RUNS)
        expected_gap = result.median_terminal_value - profile.goal_amount
        assert abs(result.median_goal_gap - expected_gap) < 1.0
