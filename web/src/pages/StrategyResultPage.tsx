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
  const baseEntries = Object.entries(recommendation.base_strategy.allocation);
  const allocationEntries = Object.entries(recommendation.recommended_strategy.allocation);
  const simulation = recommendation.simulation;
  const accumulatedLabel = `$${simulation.median_terminal_value.toLocaleString()}`;
  const remainingLabel =
    simulation.median_goal_gap >= 0
      ? `+$${simulation.median_goal_gap.toLocaleString()} above target`
      : `$${Math.abs(simulation.median_goal_gap).toLocaleString()} left to target`;

  return (
    <div className="result-shell">
      <div className="brand-haze brand-haze-left" />
      <div className="brand-haze brand-haze-right" />
      <section className="result-card">
        <div className="eyebrow">Your personalized portfolio is ready</div>
        <h1>Based on your profile, we built a {recommendation.strategy_profile} long-term strategy.</h1>
        <p>
          The portfolio below reflects your goal, risk preference, savings capacity, and
          the current market regime. It is designed for a planning horizon of about{" "}
          {profile.investment_horizon_years} years.
        </p>

        <div className="result-top-grid">
          <div className="result-hero-panel">
            <span>Goal probability</span>
            <strong>{Math.round(simulation.probability_of_reaching_goal * 100)}%</strong>
            <p>chance of reaching your target under simulated long-term market outcomes</p>
          </div>

          <div className="result-summary-list">
            <SummaryItem label="Portfolio style" value={profile.strategy_preference.replace(/_/g, " ")} />
            <SummaryItem label="Strategy profile" value={recommendation.strategy_profile} />
            <SummaryItem label="Risk preference" value={profile.risk_preference} />
            <SummaryItem label="Current market regime" value={recommendation.market_regime.replace(/_/g, " ")} />
            <SummaryItem label="What you'll likely accumulate" value={accumulatedLabel} />
            <SummaryItem label="Selected horizon" value={`${profile.investment_horizon_years} years`} />
          </div>
        </div>

        <section className="result-section">
          <h2>Goal feasibility at a glance</h2>
          <div className="result-feasibility-grid">
            <SummaryItem label="What you'll likely accumulate" value={accumulatedLabel} />
            <SummaryItem label="What may still be missing by your target date" value={remainingLabel} />
            <SummaryItem
              label="To improve your odds, invest about"
              value={`$${simulation.required_monthly_contribution_for_80_percent_success.toLocaleString()}`}
            />
            <SummaryItem
              label="You're currently investing"
              value={`$${profile.monthly_contribution.toLocaleString()}`}
            />
          </div>
          <p className="result-note">
            These figures are based on the median simulated outcome. If the projected amount
            remains below your target, the remaining gap shows what may still be missing by
            your target date.
          </p>
        </section>

        <section className="result-section">
          <h2>From strategic base to live recommendation</h2>
          <div className="result-strategy-grid">
            <div className="result-strategy-column">
              <div className="section-heading">
                <h3>Base strategy</h3>
                <p>Your long-term allocation before market regime adjustments.</p>
              </div>
              <div className="result-allocation-list">
                {baseEntries.map(([asset, value]) => (
                  <div key={asset} className="result-allocation-row">
                    <div>
                      <strong>{asset.replace(/_/g, " ")}</strong>
                      <p>Strategic allocation</p>
                    </div>
                    <span>{Math.round(value * 100)}%</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="result-strategy-column">
              <div className="section-heading">
                <h3>Market-aware recommendation</h3>
                <p>Adjusted to reflect the current regime without breaking your overall risk band.</p>
              </div>
              <div className="result-allocation-list">
                {allocationEntries.map(([asset, value]) => (
                  <div key={asset} className="result-allocation-row">
                    <div>
                      <strong>{asset.replace(/_/g, " ")}</strong>
                      <p>Recommended allocation now</p>
                    </div>
                    <span>{Math.round(value * 100)}%</span>
                  </div>
                ))}
              </div>
            </div>
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
            Enter workspace
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
