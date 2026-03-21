import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { generateStrategy } from "../api";
import { useAuth } from "../auth";
import { defaultProfile, mockAdvice } from "../mockData";
import type { AdvisorResponse, RiskPreference, UserProfilePayload } from "../types";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percentFormatter = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 0,
});

export default function DashboardPage() {
  const { user, logoutUser } = useAuth();
  const [profile, setProfile] = useState<UserProfilePayload>(defaultProfile);
  const [advice, setAdvice] = useState<AdvisorResponse>(mockAdvice);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const nextAdvice = await generateStrategy(profile);
      setAdvice(nextAdvice);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error.");
    } finally {
      setLoading(false);
    }
  }

  const allocationEntries = Object.entries(advice.recommended_strategy.allocation).map(
    ([asset, value]) => ({
      name: asset.replace("_", " ").replace(/\b\w/g, (char) => char.toUpperCase()),
      value: Number((value * 100).toFixed(1)),
    }),
  );

  const probability = advice.simulation.probability_of_reaching_goal;

  return (
    <div className="page-shell">
      <div className="background-orb background-orb-left" />
      <div className="background-orb background-orb-right" />

      <header className="hero-card app-hero">
        <div className="hero-copy">
          <div className="eyebrow">AI Investment Strategy Advisor</div>
          <h1>Welcome back, {user?.full_name.split(" ")[0] ?? "Investor"}.</h1>
          <p>
            Your authenticated workspace is ready. Next we can layer onboarding,
            saved profiles, and a full multi-step product flow on top of this foundation.
          </p>
        </div>
        <div className="hero-actions">
          <Link className="secondary-button link-button" to="/invest">
            Public invest page
          </Link>
          <button className="primary-button slim-button" onClick={logoutUser} type="button">
            Log out
          </button>
        </div>
      </header>

      <main className="layout-grid">
        <section className="panel form-panel">
          <div className="section-heading">
            <h2>Client Profile</h2>
            <p>Authenticated strategy workspace. Use it to generate a recommendation.</p>
          </div>

          <form className="profile-form" onSubmit={handleSubmit}>
            <InputGroup
              label="Age"
              value={profile.age}
              min={18}
              max={75}
              onChange={(value) => setProfile((current) => ({ ...current, age: value }))}
            />
            <InputGroup
              label="Annual income"
              value={profile.annual_income}
              min={10000}
              step={5000}
              prefix="$"
              onChange={(value) =>
                setProfile((current) => ({ ...current, annual_income: value }))
              }
            />
            <InputGroup
              label="Savings rate"
              value={profile.savings_rate * 100}
              min={0}
              max={50}
              suffix="%"
              onChange={(value) =>
                setProfile((current) => ({ ...current, savings_rate: value / 100 }))
              }
            />
            <InputGroup
              label="Current savings"
              value={profile.current_savings}
              min={0}
              step={5000}
              prefix="$"
              onChange={(value) =>
                setProfile((current) => ({ ...current, current_savings: value }))
              }
            />
            <InputGroup
              label="Monthly contribution"
              value={profile.monthly_contribution}
              min={0}
              step={100}
              prefix="$"
              onChange={(value) =>
                setProfile((current) => ({ ...current, monthly_contribution: value }))
              }
            />
            <InputGroup
              label="Goal amount"
              value={profile.goal_amount}
              min={10000}
              step={10000}
              prefix="$"
              onChange={(value) =>
                setProfile((current) => ({ ...current, goal_amount: value }))
              }
            />
            <InputGroup
              label="Horizon (years)"
              value={profile.investment_horizon_years}
              min={1}
              max={40}
              onChange={(value) =>
                setProfile((current) => ({ ...current, investment_horizon_years: value }))
              }
            />

            <div className="field">
              <label htmlFor="risk-preference">Risk preference</label>
              <select
                id="risk-preference"
                value={profile.risk_preference}
                onChange={(event) =>
                  setProfile((current) => ({
                    ...current,
                    risk_preference: event.target.value as RiskPreference,
                  }))
                }
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? "Generating strategy..." : "Generate strategy"}
            </button>
            {error ? <p className="error-message">{error}</p> : null}
          </form>
        </section>

        <section className="results-column">
          <div className="metric-grid">
            <MetricCard label="Strategy profile" value={capitalize(advice.strategy_profile)} />
            <MetricCard
              label="Market regime"
              value={capitalize(advice.market_regime.replace("_", " "))}
            />
            <MetricCard
              label="Goal probability"
              value={percentFormatter.format(probability)}
              accent
            />
            <MetricCard
              label="Median outcome"
              value={currencyFormatter.format(advice.simulation.median_terminal_value)}
            />
          </div>

          <div className="insight-grid">
            <section className="panel recommendation-panel">
              <div className="section-heading">
                <h2>Why this strategy</h2>
                <p>The system combines client inputs with market-aware allocation rules.</p>
              </div>
              <div className="strategy-banner">
                <span>Recommended strategy</span>
                <strong>{capitalize(advice.strategy_profile)} allocation</strong>
              </div>
              <ul className="reason-list">
                <li>Starts from the user&apos;s preferred long-term risk band.</li>
                <li>Adjusts exposure based on the current market regime.</li>
                <li>Simulates many future paths to estimate goal feasibility.</li>
              </ul>
            </section>

            <section className="probability-card">
              <span>Probability of success</span>
              <strong>{percentFormatter.format(probability)}</strong>
              <p>{probabilityMessage(probability)}</p>
            </section>
          </div>

          <div className="charts-grid">
            <section className="panel chart-panel">
              <div className="section-heading">
                <h2>Recommended Allocation</h2>
                <p>Asset-class mix after adapting the base strategy to current market conditions.</p>
              </div>
              <div className="pie-wrap">
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={allocationEntries}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={60}
                      outerRadius={98}
                      paddingAngle={4}
                    />
                    <Tooltip formatter={(value: number) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="allocation-list">
                {allocationEntries.map((entry) => (
                  <div key={entry.name} className="allocation-row">
                    <span>{entry.name}</span>
                    <strong>{entry.value}%</strong>
                  </div>
                ))}
              </div>
            </section>

            <section className="panel chart-panel">
              <div className="section-heading">
                <h2>Projected Goal Outcomes</h2>
                <p>Median and confidence band across simulated market outcomes.</p>
              </div>
              <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={advice.simulation.yearly_projection}>
                  <defs>
                    <linearGradient id="projectionFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#0f766e" stopOpacity={0.24} />
                      <stop offset="100%" stopColor="#0f766e" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(148,163,184,0.18)" vertical={false} />
                  <XAxis dataKey="year" stroke="#64748b" />
                  <YAxis
                    stroke="#64748b"
                    tickFormatter={(value) => `$${Math.round(value / 1000)}k`}
                  />
                  <Tooltip formatter={(value: number) => currencyFormatter.format(value)} />
                  <Area
                    type="monotone"
                    dataKey="optimistic_value"
                    stroke="transparent"
                    fill="transparent"
                  />
                  <Area
                    type="monotone"
                    dataKey="pessimistic_value"
                    stroke="transparent"
                    fill="url(#projectionFill)"
                  />
                  <Area
                    type="monotone"
                    dataKey="median_value"
                    stroke="#0f766e"
                    strokeWidth={3}
                    fill="transparent"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </section>
          </div>
        </section>
      </main>
    </div>
  );
}

function InputGroup(props: {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  prefix?: string;
  suffix?: string;
  onChange: (value: number) => void;
}) {
  const { label, value, min, max, step = 1, prefix, suffix, onChange } = props;

  return (
    <div className="field">
      <label>{label}</label>
      <div className="input-shell">
        {prefix ? <span>{prefix}</span> : null}
        <input
          type="number"
          value={value}
          min={min}
          max={max}
          step={step}
          onChange={(event) => onChange(Number(event.target.value))}
        />
        {suffix ? <span>{suffix}</span> : null}
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

function capitalize(value: string) {
  return value.replace(/\b\w/g, (char) => char.toUpperCase());
}

function probabilityMessage(probability: number) {
  if (probability >= 0.8) {
    return "Strong long-term outlook under the current assumptions.";
  }
  if (probability >= 0.6) {
    return "Viable plan, though outcomes still carry meaningful uncertainty.";
  }
  return "This goal may require a higher contribution rate or longer horizon.";
}
