import numpy as np
import pandas as pd
import pytest
from app.market_regime import _build_features, _label_clusters, _fallback_snapshot


def make_price_history(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic S&P-like price history for testing."""
    rng = np.random.default_rng(seed)
    daily_returns = rng.normal(loc=0.0003, scale=0.01, size=n)
    prices = 4000.0 * np.cumprod(1 + daily_returns)
    dates = pd.date_range(end="2024-01-01", periods=n, freq="B")
    return pd.DataFrame({"Close": prices}, index=dates)


class TestBuildFeatures:
    def test_returns_dataframe_with_required_columns(self):
        history = make_price_history()
        features = _build_features(history)
        for col in ("return_21d", "volatility_21d", "momentum_63d", "drawdown_126d"):
            assert col in features.columns, f"Missing column: {col}"

    def test_no_nan_values_after_dropna(self):
        history = make_price_history()
        features = _build_features(history)
        assert not features.isna().any().any()

    def test_drawdown_is_non_positive(self):
        history = make_price_history()
        features = _build_features(history)
        assert (features["drawdown_126d"] <= 0).all()

    def test_volatility_is_non_negative(self):
        history = make_price_history()
        features = _build_features(history)
        assert (features["volatility_21d"] >= 0).all()

    def test_shorter_history_still_works(self):
        history = make_price_history(n=150)
        features = _build_features(history)
        assert len(features) > 0

    def test_returns_fewer_rows_than_input_due_to_rolling(self):
        history = make_price_history(n=300)
        features = _build_features(history)
        assert len(features) < len(history)


class TestLabelClusters:
    def test_returns_dict_with_4_entries(self):
        history = make_price_history()
        features = _build_features(history)
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        feature_cols = ["return_21d", "volatility_21d", "momentum_63d", "drawdown_126d"]
        scaler = StandardScaler()
        matrix = scaler.fit_transform(features[feature_cols])
        model = KMeans(n_clusters=4, n_init=20, random_state=42)
        features = features.assign(cluster=model.fit_predict(matrix))
        labels = _label_clusters(features)
        assert len(labels) == 4

    def test_all_labels_are_valid_regime_strings(self):
        history = make_price_history()
        features = _build_features(history)
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        feature_cols = ["return_21d", "volatility_21d", "momentum_63d", "drawdown_126d"]
        scaler = StandardScaler()
        matrix = scaler.fit_transform(features[feature_cols])
        model = KMeans(n_clusters=4, n_init=20, random_state=42)
        features = features.assign(cluster=model.fit_predict(matrix))
        labels = _label_clusters(features)
        valid = {"bull", "bear", "sideways", "high_volatility"}
        for label in labels.values():
            assert label in valid


class TestFallbackSnapshot:
    def test_returns_valid_snapshot(self):
        snapshot = _fallback_snapshot()
        assert snapshot.regime == "sideways"
        assert snapshot.as_of == "offline-mode"
        assert snapshot.annualized_volatility > 0

    def test_fallback_regime_is_valid(self):
        snapshot = _fallback_snapshot()
        assert snapshot.regime in {"bull", "bear", "sideways", "high_volatility"}
