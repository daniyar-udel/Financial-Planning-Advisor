from dataclasses import dataclass, field


@dataclass(frozen=True)
class PortfolioPreset:
    allocations: dict[str, float]
    expected_return: float
    annual_volatility: float


@dataclass(frozen=True)
class Settings:
    simulation_runs: int = 10_000
    trading_days_per_year: int = 252
    market_symbol: str = "^GSPC"
    market_lookback_period: str = "5y"
    regime_features: tuple[str, ...] = (
        "return_21d",
        "volatility_21d",
        "momentum_63d",
        "drawdown_126d",
    )
    portfolio_presets: dict[str, PortfolioPreset] = field(
        default_factory=lambda: {
            "conservative": PortfolioPreset(
                allocations={"stocks": 0.35, "bonds": 0.55, "reits": 0.10},
                expected_return=0.05,
                annual_volatility=0.08,
            ),
            "moderate": PortfolioPreset(
                allocations={"stocks": 0.60, "bonds": 0.30, "reits": 0.10},
                expected_return=0.07,
                annual_volatility=0.13,
            ),
            "aggressive": PortfolioPreset(
                allocations={"stocks": 0.80, "bonds": 0.10, "alternatives": 0.10},
                expected_return=0.09,
                annual_volatility=0.18,
            ),
        }
    )


settings = Settings()
