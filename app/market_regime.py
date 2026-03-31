from __future__ import annotations

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.config import settings
from app.logger import get_logger
from app.schemas import MarketSnapshot

log = get_logger(__name__)


def detect_market_regime(symbol: str | None = None, period: str | None = None) -> MarketSnapshot:
    symbol = symbol or settings.market_symbol
    period = period or settings.market_lookback_period

    log.info("Fetching market data: symbol=%s period=%s", symbol, period)
    try:
        history = yf.download(symbol, period=period, auto_adjust=True, progress=False)
    except Exception as exc:
        log.error("Failed to download market data: %s — using fallback snapshot", exc)
        history = pd.DataFrame()

    if history.empty:
        log.warning("Market data is empty — using fallback snapshot")
        return _fallback_snapshot()

    features = _build_features(history)
    latest_row = features.iloc[-1]

    scaler = StandardScaler()
    feature_matrix = scaler.fit_transform(features[list(settings.regime_features)])
    model = KMeans(n_clusters=4, n_init=20, random_state=42)
    clusters = model.fit_predict(feature_matrix)
    features = features.assign(cluster=clusters)

    cluster_labels = _label_clusters(features)
    latest_cluster = int(features.iloc[-1]["cluster"])
    regime = cluster_labels[latest_cluster]

    return MarketSnapshot(
        regime=regime,
        latest_close=round(float(history["Close"].iloc[-1]), 2),
        annualized_volatility=round(float(latest_row["volatility_21d"] * np.sqrt(252)), 4),
        momentum_63d=round(float(latest_row["momentum_63d"]), 4),
        drawdown_126d=round(float(latest_row["drawdown_126d"]), 4),
        as_of=str(features.index[-1].date()),
    )


def _build_features(history: pd.DataFrame) -> pd.DataFrame:
    close = history["Close"].copy()
    returns = close.pct_change()

    frame = pd.DataFrame(index=close.index)
    frame["return_21d"] = close.pct_change(21)
    frame["volatility_21d"] = returns.rolling(21).std()
    frame["momentum_63d"] = close.pct_change(63)
    rolling_max = close.rolling(126).max()
    frame["drawdown_126d"] = close / rolling_max - 1

    return frame.dropna()


def _label_clusters(features: pd.DataFrame) -> dict[int, str]:
    cluster_stats = (
        features.groupby("cluster")[["return_21d", "volatility_21d", "momentum_63d", "drawdown_126d"]]
        .mean()
        .reset_index()
    )

    labels: dict[int, str] = {}
    for row in cluster_stats.itertuples(index=False):
        if row.volatility_21d > cluster_stats["volatility_21d"].quantile(0.75):
            label = "high_volatility"
        elif row.return_21d > 0.03 and row.momentum_63d > 0.05:
            label = "bull"
        elif row.return_21d < -0.03 or row.drawdown_126d < -0.10:
            label = "bear"
        else:
            label = "sideways"
        labels[int(row.cluster)] = label

    return labels


def _fallback_snapshot() -> MarketSnapshot:
    return MarketSnapshot(
        regime="sideways",
        latest_close=0.0,
        annualized_volatility=0.16,
        momentum_63d=0.01,
        drawdown_126d=-0.04,
        as_of="offline-mode",
    )
