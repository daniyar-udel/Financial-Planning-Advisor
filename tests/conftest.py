import os
import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-for-testing-only-32chars!!")
os.environ.setdefault("GROQ_API_KEY", "test-key")


from app.schemas import UserProfile


@pytest.fixture
def base_profile() -> UserProfile:
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
