import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { getStrategyResult } from "../api";
import { useAuth } from "../auth";
import type { StrategyResultResponse } from "../types";

export default function StrategyResultPage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [result, setResult] = useState<StrategyResultResponse | null>(() => {
    const stored = sessionStorage.getItem("strategy_result");
    return stored ? (JSON.parse(stored) as StrategyResultResponse) : null;
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function hydrateResult() {
      if (result || !token) {
        return;
      }

      try {
        const nextResult = await getStrategyResult(token);
        setResult(nextResult);
        sessionStorage.setItem("strategy_result", JSON.stringify(nextResult));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load strategy result.");
      }
    }

    void hydrateResult();
  }, [result, token]);

  if (error) {
    return <div className="route-loader">{error}</div>;
  }

  if (!result) {
    return <div className="route-loader">Loading your portfolio result...</div>;
  }

  const { recommendation, onboarding_profile: profile } = result;
  const allocationEntries = Object.entries(recommendation.recommended_strategy.allocation);
  const simulation = recommendation.simulation;
  const accumulatedLabel = `$${simulation.median_terminal_value.toLocaleString()}`;
  const remainingLabel =
    simulation.median_goal_gap >= 0
      ? `+$${simulation.median_goal_gap.toLocaleString()} above target`
      : `$${Math.abs(simulation.median_goal_gap).toLocaleString()} left to target`;

  return (
    <div className="result-shell">
      <section className="result-card">
        <div className="eyebrow">Your personalized portfolio is ready</div>
        <h1>Based on your profile, we built a {recommendation.strategy_profile} strategy.</h1>
        <p>
          The portfolio below reflects your goal, risk preference, and the current market
          regime. It is designed for a long-term horizon of about {profile.investment_horizon_years} years.
        </p>

        <div className="result-top-grid">
          <div className="result-hero-panel">
            <span>Goal probability</span>
            <strong>{Math.round(simulation.probability_of_reaching_goal * 100)}%</strong>
            <p>chance of reaching your target under simulated market outcomes</p>
          </div>

          <div className="result-summary-list">
            <SummaryItem label="Portfolio type" value={profile.strategy_preference.replace(/_/g, " ")} />
            <SummaryItem label="Risk preference" value={profile.risk_preference} />
            <SummaryItem label="Market regime" value={recommendation.market_regime.replace(/_/g, " ")} />
            <SummaryItem label="Estimated amount accumulated" value={accumulatedLabel} />
          </div>
        </div>

        <section className="result-section">
          <h2>Goal feasibility</h2>
          <div className="result-feasibility-grid">
            <SummaryItem
              label="Estimated amount accumulated"
              value={accumulatedLabel}
            />
            <SummaryItem label="Still left to reach the goal" value={remainingLabel} />
            <SummaryItem
              label="Monthly contribution for 80% success"
              value={`$${simulation.required_monthly_contribution_for_80_percent_success.toLocaleString()}`}
            />
            <SummaryItem
              label="Current monthly contribution"
              value={`$${profile.monthly_contribution.toLocaleString()}`}
            />
          </div>
          <p className="result-note">
            The accumulated amount is based on the median simulation outcome. If it is still below your target,
            the remaining gap shows how much would still be missing by the end of the selected horizon.
          </p>
        </section>

        <section className="result-section">
          <h2>Recommended allocation</h2>
          <div className="result-allocation-list">
            {allocationEntries.map(([asset, value]) => (
              <div key={asset} className="result-allocation-row">
                <div>
                  <strong>{asset.replace(/_/g, " ")}</strong>
                  <p>Market-aware asset class allocation</p>
                </div>
                <span>{Math.round(value * 100)}%</span>
              </div>
            ))}
          </div>
        </section>

        <section className="result-section">
          <h2>Why this portfolio</h2>
          <p className="result-copy">{recommendation.explanation}</p>
          <p className="result-note">{result.strategy_horizon_note}</p>
          <p className="result-note">{result.platform_notice}</p>
          <p className="result-disclaimer">{result.disclaimer}</p>
        </section>

        <div className="result-actions">
          <button className="primary-button slim-button" type="button" onClick={() => navigate("/app")}>
            Confirm and continue
          </button>
          <Link className="secondary-button link-button" to="/onboarding">
            Edit answers
          </Link>
        </div>
      </section>
    </div>
  );
}

function SummaryItem(props: { label: string; value: string }) {
  return (
    <div className="result-summary-item">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}
