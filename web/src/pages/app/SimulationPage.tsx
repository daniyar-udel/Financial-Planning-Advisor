import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useStrategyResult } from "../../hooks/useStrategyResult";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export default function SimulationPage() {
  const { result, loading, error } = useStrategyResult();

  if (loading) {
    return <div className="route-loader">Loading your simulation...</div>;
  }

  if (error || !result) {
    return <div className="route-loader">{error ?? "Strategy result not found."}</div>;
  }

  const simulation = result.recommendation.simulation;

  return (
    <div className="app-page">
      <header className="app-page-header">
        <div>
          <div className="eyebrow">Simulation</div>
          <h1>Projected portfolio outcomes</h1>
          <p>
            Explore the range of potential outcomes across many simulated market paths.
          </p>
        </div>
      </header>

      <div className="app-metric-grid">
        <MetricCard label="Goal probability" value={`${Math.round(simulation.probability_of_reaching_goal * 100)}%`} />
        <MetricCard label="Reach 90% of goal" value={`${Math.round(simulation.probability_of_reaching_90_percent_of_goal * 100)}%`} />
        <MetricCard label="Pessimistic outcome" value={currencyFormatter.format(simulation.pessimistic_terminal_value)} />
        <MetricCard label="Optimistic outcome" value={currencyFormatter.format(simulation.optimistic_terminal_value)} />
      </div>

      <div className="app-two-column app-two-column-wide">
        <section className="app-panel">
          <div className="section-heading">
            <h2>Median and confidence range</h2>
            <p>Projected growth under pessimistic, median, and optimistic scenarios.</p>
          </div>
          <ResponsiveContainer width="100%" height={360}>
            <AreaChart data={simulation.yearly_projection}>
              <defs>
                <linearGradient id="projectionFillApp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0e6d63" stopOpacity={0.28} />
                  <stop offset="100%" stopColor="#0e6d63" stopOpacity={0.04} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(122, 133, 124, 0.16)" vertical={false} />
              <XAxis dataKey="year" stroke="#6b7280" />
              <YAxis stroke="#6b7280" tickFormatter={(value) => `$${Math.round(value / 1000)}k`} />
              <Tooltip
                formatter={(value: number) => currencyFormatter.format(value)}
                contentStyle={{
                  borderRadius: 16,
                  border: "1px solid rgba(15, 23, 42, 0.08)",
                  background: "rgba(255,255,255,0.96)",
                }}
              />
              <Area type="monotone" dataKey="optimistic_value" stroke="transparent" fill="transparent" />
              <Area type="monotone" dataKey="pessimistic_value" stroke="transparent" fill="url(#projectionFillApp)" />
              <Area type="monotone" dataKey="median_value" stroke="#0e6d63" strokeWidth={3} fill="transparent" />
            </AreaChart>
          </ResponsiveContainer>
        </section>

        <section className="app-panel">
          <div className="section-heading">
            <h2>How to read this range</h2>
            <p>Use the simulation to think in scenarios rather than a single forecast.</p>
          </div>
          <div className="summary-stack">
            <div className="dashboard-goal-metric">
              <span>Median outcome</span>
              <strong>{currencyFormatter.format(simulation.median_terminal_value)}</strong>
            </div>
            <div className="dashboard-goal-metric">
              <span>What may still be missing</span>
              <strong>
                {simulation.median_goal_gap >= 0
                  ? `${currencyFormatter.format(simulation.median_goal_gap)} above target`
                  : `${currencyFormatter.format(Math.abs(simulation.median_goal_gap))} left`}
              </strong>
            </div>
            <div className="dashboard-goal-metric">
              <span>Suggested monthly contribution for stronger odds</span>
              <strong>
                {currencyFormatter.format(
                  simulation.required_monthly_contribution_for_80_percent_success,
                )}{" "}
                / month
              </strong>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function MetricCard(props: { label: string; value: string }) {
  return (
    <div className="metric-card">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}
