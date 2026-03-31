import pytest
from app.portfolio import build_base_strategy, build_recommended_strategy, _normalize_allocations


class TestNormalizeAllocations:
    def test_sums_to_1(self):
        result = _normalize_allocations({"stocks": 0.6, "bonds": 0.3, "reits": 0.1})
        assert abs(sum(result.values()) - 1.0) < 1e-9

    def test_empty_dict_returns_empty(self):
        assert _normalize_allocations({}) == {}

    def test_negative_values_clamped_to_zero(self):
        result = _normalize_allocations({"stocks": 0.8, "bonds": -0.2})
        assert result["bonds"] == 0.0
        assert result["stocks"] == 1.0

    def test_all_zeros_returns_zeros(self):
        result = _normalize_allocations({"stocks": 0.0, "bonds": 0.0})
        assert result == {"stocks": 0.0, "bonds": 0.0}


class TestBuildBaseStrategy:
    def test_conservative_allocation_sums_to_1(self):
        result = build_base_strategy("conservative")
        assert abs(sum(result.allocation.values()) - 1.0) < 1e-6

    def test_moderate_allocation_sums_to_1(self):
        result = build_base_strategy("moderate")
        assert abs(sum(result.allocation.values()) - 1.0) < 1e-6

    def test_aggressive_allocation_sums_to_1(self):
        result = build_base_strategy("aggressive")
        assert abs(sum(result.allocation.values()) - 1.0) < 1e-6

    def test_aggressive_has_higher_return_than_conservative(self):
        conservative = build_base_strategy("conservative")
        aggressive = build_base_strategy("aggressive")
        assert aggressive.expected_annual_return > conservative.expected_annual_return

    def test_aggressive_has_higher_volatility_than_conservative(self):
        conservative = build_base_strategy("conservative")
        aggressive = build_base_strategy("aggressive")
        assert aggressive.annual_volatility > conservative.annual_volatility

    def test_strategy_profile_matches_input(self):
        for profile in ("conservative", "moderate", "aggressive"):
            result = build_base_strategy(profile)
            assert result.strategy_profile == profile


class TestBuildRecommendedStrategy:
    def test_bear_regime_reduces_stocks(self):
        base = build_base_strategy("moderate").allocation["stocks"]
        recommended = build_recommended_strategy("moderate", "bear")
        assert recommended.allocation.get("stocks", 0) < base

    def test_bull_regime_increases_stocks(self):
        base = build_base_strategy("moderate").allocation["stocks"]
        recommended = build_recommended_strategy("moderate", "bull")
        assert recommended.allocation.get("stocks", 0) > base

    def test_bear_regime_adds_gold(self):
        result = build_recommended_strategy("moderate", "bear")
        assert result.allocation.get("gold", 0) > 0

    def test_high_volatility_reduces_stocks(self):
        base = build_base_strategy("moderate").allocation["stocks"]
        result = build_recommended_strategy("moderate", "high_volatility")
        assert result.allocation.get("stocks", 0) < base

    def test_allocation_always_sums_to_1(self):
        for profile in ("conservative", "moderate", "aggressive"):
            for regime in ("bull", "bear", "sideways", "high_volatility"):
                result = build_recommended_strategy(profile, regime)
                total = sum(result.allocation.values())
                assert abs(total - 1.0) < 1e-3, f"{profile}/{regime} sums to {total}"
