import { useAuth } from "../../auth";
import { useStrategyResult } from "../../hooks/useStrategyResult";

export default function ProfilePage() {
  const { user } = useAuth();
  const { result, loading, error } = useStrategyResult();

  if (loading) {
    return <div className="route-loader">Loading your profile...</div>;
  }

  if (error || !result) {
    return <div className="route-loader">{error ?? "Profile not found."}</div>;
  }

  const profile = result.onboarding_profile;

  return (
    <div className="app-page">
      <header className="app-page-header">
        <div>
          <div className="eyebrow">Profile</div>
          <h1>Your account and planning inputs</h1>
          <p>Review the information that drives your planning recommendation and AI workspace.</p>
        </div>
      </header>

      <div className="app-two-column">
        <section className="app-panel">
          <div className="section-heading">
            <h2>Account</h2>
            <p>Basic authenticated user information and saved context.</p>
          </div>
          <div className="review-grid">
            <ReviewItem label="Full name" value={user?.full_name ?? "Unknown"} />
            <ReviewItem label="Email" value={user?.email ?? "Unknown"} />
            <ReviewItem label="Goal horizon" value={`${profile.investment_horizon_years} years`} />
            <ReviewItem label="Address" value={profile.address} />
          </div>
        </section>

        <section className="app-panel">
          <div className="section-heading">
            <h2>Planning profile</h2>
            <p>Saved onboarding inputs used to generate the strategy recommendation.</p>
          </div>
          <div className="review-grid">
            <ReviewItem label="Goal" value={profile.goal_type.replace(/_/g, " ")} />
            <ReviewItem label="Goal amount" value={`$${profile.goal_amount.toLocaleString()}`} />
            <ReviewItem label="Annual income" value={`$${profile.annual_income.toLocaleString()}`} />
            <ReviewItem label="Monthly contribution" value={`$${profile.monthly_contribution.toLocaleString()}`} />
            <ReviewItem label="Current savings" value={`$${profile.current_savings.toLocaleString()}`} />
            <ReviewItem label="Risk preference" value={profile.risk_preference} />
            <ReviewItem label="Strategy preference" value={profile.strategy_preference.replace(/_/g, " ")} />
          </div>
        </section>
      </div>
    </div>
  );
}

function ReviewItem(props: { label: string; value: string }) {
  return (
    <div className="review-item">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}
