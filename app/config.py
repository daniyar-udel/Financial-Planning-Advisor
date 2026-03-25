import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


load_dotenv()


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
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_timeout_seconds: float = 20.0
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
