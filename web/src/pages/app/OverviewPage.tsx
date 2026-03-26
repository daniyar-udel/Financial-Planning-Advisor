import type { ReactNode } from "react";
import { Link } from "react-router-dom";

import { useStrategyResult } from "../../hooks/useStrategyResult";
import { capitalizeWords } from "../../utils";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percentFormatter = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

export default function OverviewPage() {
  const { result, loading, error } = useStrategyResult();

  if (loading) {
    return <div className="route-loader">Loading your strategy overview...</div>;
  }

  if (error || !result) {
    return <div className="route-loader">{error ?? "Strategy result not found."}</div>;
  }

  const { recommendation, onboarding_profile: profile } = result;
  const simulation = recommendation.simulation;

  return (
    <div className="app-page">
      <header className="app-page-header">
        <div>
          <div className="eyebrow">Overview</div>
          <h1>Your long-term strategy at a glance</h1>
          <p>
            This workspace summarizes your current market-aware plan, projected outcome,
            and what may still be missing by your target date.
          </p>
        </div>
        <Link className="secondary-button link-button" to="/strategy/result">
          View result page
        </Link>
      </header>

      <div className="app-metric-grid">
        <MetricCard label="Strategy profile" value={capitalizeWords(recommendation.strategy_profile)} />
        <MetricCard label="Market regime" value={capitalizeWords(recommendation.market_regime.replace(/_/g, " "))} />
        <MetricCard label="Goal probability" value={percentFormatter.format(simulation.probability_of_reaching_goal)} accent />
        <MetricCard label="What you'll likely accumulate" value={currencyFormatter.format(simulation.median_terminal_value)} />
      </div>

      <div className="app-two-column">
        <section className="app-panel">
          <div className="section-heading">
            <h2>Key takeaways</h2>
            <p>The most important planning signals from your current recommendation.</p>
          </div>
          <div className="summary-stack">
            <SummaryBox label="What may still be missing by your target date">
              {simulation.median_goal_gap >= 0
                ? `${currencyFormatter.format(simulation.median_goal_gap)} above target`
                : `${currencyFormatter.format(Math.abs(simulation.median_goal_gap))} left`}
            </SummaryBox>
            <SummaryBox label="To improve your odds, invest about">
              {currencyFormatter.format(simulation.required_monthly_contribution_for_80_percent_success)} / month
            </SummaryBox>
            <SummaryBox label="Selected investment horizon">
              {profile.investment_horizon_years} years
            </SummaryBox>
          </div>
        </section>

        <section className="app-panel">
          <div className="section-heading">
            <h2>Advisor summary</h2>
            <p>Why the current strategy fits the profile you provided.</p>
          </div>
          <p className="narrative-copy">{recommendation.explanation}</p>
          <p className="result-note">{result.strategy_horizon_note}</p>
          <p className="result-disclaimer">{result.disclaimer}</p>
        </section>
      </div>
    </div>
  );
}

function MetricCard(props: { label: string; value: string; accent?: boolean }) {
  return (
    <div className={`metric-card${props.accent ? " metric-card-accent" : ""}`}>
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}

function SummaryBox(props: { label: string; children: ReactNode }) {
  return (
    <div className="dashboard-goal-metric">
      <span>{props.label}</span>
      <strong>{props.children}</strong>
    </div>
  );
}
