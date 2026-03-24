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

      <section className="app-panel">
        <div className="section-heading">
          <h2>Median and confidence range</h2>
          <p>Projected growth under pessimistic, median, and optimistic scenarios.</p>
        </div>
        <ResponsiveContainer width="100%" height={360}>
          <AreaChart data={simulation.yearly_projection}>
            <defs>
              <linearGradient id="projectionFillApp" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#0f766e" stopOpacity={0.24} />
                <stop offset="100%" stopColor="#0f766e" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(148,163,184,0.18)" vertical={false} />
            <XAxis dataKey="year" stroke="#64748b" />
            <YAxis stroke="#64748b" tickFormatter={(value) => `$${Math.round(value / 1000)}k`} />
            <Tooltip formatter={(value: number) => currencyFormatter.format(value)} />
            <Area type="monotone" dataKey="optimistic_value" stroke="transparent" fill="transparent" />
            <Area type="monotone" dataKey="pessimistic_value" stroke="transparent" fill="url(#projectionFillApp)" />
            <Area type="monotone" dataKey="median_value" stroke="#0f766e" strokeWidth={3} fill="transparent" />
          </AreaChart>
        </ResponsiveContainer>
      </section>
    </div>
  );
}
