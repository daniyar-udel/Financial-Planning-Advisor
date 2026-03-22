from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.database import get_connection
from app.schemas import OnboardingProfileRequest, OnboardingProfileResponse, UserResponse


def save_onboarding_profile(
    user: UserResponse,
    payload: OnboardingProfileRequest,
) -> OnboardingProfileResponse:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO onboarding_profiles (
                user_id,
                goal_type,
                goal_amount,
                investment_horizon_years,
                age,
                date_of_birth,
                marital_status,
                address,
                annual_income,
                current_savings,
                monthly_contribution,
                savings_rate,
                risk_preference,
                stress_response,
                strategy_preference,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                goal_type = excluded.goal_type,
                goal_amount = excluded.goal_amount,
                investment_horizon_years = excluded.investment_horizon_years,
                age = excluded.age,
                date_of_birth = excluded.date_of_birth,
                marital_status = excluded.marital_status,
                address = excluded.address,
                annual_income = excluded.annual_income,
                current_savings = excluded.current_savings,
                monthly_contribution = excluded.monthly_contribution,
                savings_rate = excluded.savings_rate,
                risk_preference = excluded.risk_preference,
                stress_response = excluded.stress_response,
                strategy_preference = excluded.strategy_preference,
                updated_at = excluded.updated_at
            """,
            (
                user.id,
                payload.goal_type,
                payload.goal_amount,
                payload.investment_horizon_years,
                payload.age,
                payload.date_of_birth,
                payload.marital_status,
                payload.address,
                payload.annual_income,
                payload.current_savings,
                payload.monthly_contribution,
                payload.savings_rate,
                payload.risk_preference,
                payload.stress_response,
                payload.strategy_preference,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    return OnboardingProfileResponse(user_id=user.id, **payload.model_dump())


def get_onboarding_profile(user: UserResponse) -> OnboardingProfileResponse:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                user_id,
                goal_type,
                goal_amount,
                investment_horizon_years,
                age,
                date_of_birth,
                marital_status,
                address,
                annual_income,
                current_savings,
                monthly_contribution,
                savings_rate,
                risk_preference,
                stress_response,
                strategy_preference
            FROM onboarding_profiles
            WHERE user_id = ?
            """,
            (user.id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding profile not found.",
        )

    return OnboardingProfileResponse(**dict(row))
