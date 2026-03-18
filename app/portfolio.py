from app.config import settings
from app.schemas import MarketRegime, RiskProfile


def get_base_portfolio(risk_profile: RiskProfile) -> dict[str, float]:
    return dict(settings.portfolio_presets[risk_profile].allocations)


def adjust_portfolio_for_market_regime(
    risk_profile: RiskProfile,
    market_regime: MarketRegime,
) -> dict[str, float]:
    base = get_base_portfolio(risk_profile)
    adjusted = dict(base)

    if market_regime == "bull":
        adjusted["stocks"] = min(adjusted.get("stocks", 0.0) + 0.10, 0.90)
        adjusted["bonds"] = max(adjusted.get("bonds", 0.0) - 0.10, 0.05)
    elif market_regime == "bear":
        adjusted["stocks"] = max(adjusted.get("stocks", 0.0) - 0.20, 0.20)
        adjusted["bonds"] = adjusted.get("bonds", 0.0) + 0.15
        adjusted["gold"] = adjusted.get("gold", 0.0) + 0.05
        adjusted.pop("alternatives", None)
    elif market_regime == "high_volatility":
        adjusted["stocks"] = max(adjusted.get("stocks", 0.0) - 0.10, 0.25)
        adjusted["bonds"] = adjusted.get("bonds", 0.0) + 0.10
    elif market_regime == "sideways":
        adjusted["reits"] = adjusted.get("reits", 0.0) + 0.05
        adjusted["stocks"] = max(adjusted.get("stocks", 0.0) - 0.05, 0.25)

    return _normalize_allocations(adjusted)


def get_portfolio_assumptions(
    risk_profile: RiskProfile,
    market_regime: MarketRegime,
) -> tuple[float, float]:
    preset = settings.portfolio_presets[risk_profile]
    expected_return = preset.expected_return
    annual_volatility = preset.annual_volatility

    if market_regime == "bull":
        expected_return += 0.01
    elif market_regime == "bear":
        expected_return -= 0.025
        annual_volatility += 0.03
    elif market_regime == "high_volatility":
        annual_volatility += 0.04
    elif market_regime == "sideways":
        expected_return -= 0.005

    return expected_return, annual_volatility


def _normalize_allocations(allocations: dict[str, float]) -> dict[str, float]:
    positive_only = {asset: max(weight, 0.0) for asset, weight in allocations.items()}
    total = sum(positive_only.values())
    if total == 0:
        return positive_only
    return {asset: round(weight / total, 4) for asset, weight in positive_only.items()}
