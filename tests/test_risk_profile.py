import pytest
from app.schemas import UserProfile
from app.risk_profile import determine_strategy_profile


def profile(**kwargs) -> UserProfile:
    defaults = dict(
        age=30,
        annual_income=80_000,
        savings_rate=0.15,
        current_savings=10_000,
        monthly_contribution=800,
        goal_amount=500_000,
        investment_horizon_years=20,
        risk_preference="medium",
    )
    defaults.update(kwargs)
    return UserProfile(**defaults)


class TestDetermineStrategyProfile:
    def test_young_high_savings_high_risk_is_aggressive(self):
        p = profile(age=24, investment_horizon_years=30, savings_rate=0.25, risk_preference="high")
        assert determine_strategy_profile(p) == "aggressive"

    def test_old_short_horizon_low_risk_is_conservative(self):
        p = profile(age=58, investment_horizon_years=5, savings_rate=0.05, risk_preference="low")
        assert determine_strategy_profile(p) == "conservative"

    def test_balanced_is_moderate(self):
        p = profile(age=35, investment_horizon_years=20, savings_rate=0.15, risk_preference="medium")
        assert determine_strategy_profile(p) == "moderate"

    def test_high_savings_buffer_boosts_score(self):
        p_rich = profile(age=45, annual_income=50_000, current_savings=60_000, savings_rate=0.10,
                         investment_horizon_years=10, risk_preference="medium")
        p_poor = profile(age=45, annual_income=50_000, current_savings=5_000, savings_rate=0.10,
                         investment_horizon_years=10, risk_preference="medium")
        strategies = {"conservative": 0, "moderate": 1, "aggressive": 2}
        assert strategies[determine_strategy_profile(p_rich)] >= strategies[determine_strategy_profile(p_poor)]

    def test_risk_preference_low_reduces_score(self):
        p_low = profile(age=28, investment_horizon_years=25, savings_rate=0.20, risk_preference="low")
        p_high = profile(age=28, investment_horizon_years=25, savings_rate=0.20, risk_preference="high")
        strategies = {"conservative": 0, "moderate": 1, "aggressive": 2}
        assert strategies[determine_strategy_profile(p_high)] >= strategies[determine_strategy_profile(p_low)]

    def test_horizon_below_10_years_no_time_bonus(self):
        p = profile(age=50, investment_horizon_years=8, savings_rate=0.05, risk_preference="low")
        assert determine_strategy_profile(p) == "conservative"

    def test_horizon_10_to_19_partial_bonus(self):
        p = profile(age=40, investment_horizon_years=15, savings_rate=0.10, risk_preference="medium")
        result = determine_strategy_profile(p)
        assert result in ("moderate", "conservative")

    def test_returns_valid_literal(self):
        valid = {"conservative", "moderate", "aggressive"}
        for risk in ("low", "medium", "high"):
            p = profile(risk_preference=risk)
            assert determine_strategy_profile(p) in valid
