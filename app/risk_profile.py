from app.schemas import StrategyProfile, UserProfile


def determine_strategy_profile(profile: UserProfile) -> StrategyProfile:
    score = 0

    if profile.investment_horizon_years >= 20:
        score += 2
    elif profile.investment_horizon_years >= 10:
        score += 1

    if profile.age < 35:
        score += 2
    elif profile.age < 50:
        score += 1

    if profile.savings_rate >= 0.2:
        score += 2
    elif profile.savings_rate >= 0.1:
        score += 1

    if profile.current_savings >= profile.annual_income:
        score += 1

    preference_bonus = {"low": 0, "medium": 1, "high": 2}
    score += preference_bonus[profile.risk_preference]

    if score >= 7:
        return "aggressive"
    if score >= 4:
        return "moderate"
    return "conservative"
