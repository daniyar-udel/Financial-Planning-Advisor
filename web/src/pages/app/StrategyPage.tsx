import { useStrategyResult } from "../../hooks/useStrategyResult";

export default function StrategyPage() {
  const { result, loading, error } = useStrategyResult();

  if (loading) {
    return <div className="route-loader">Loading your strategy...</div>;
  }

  if (error || !result) {
    return <div className="route-loader">{error ?? "Strategy result not found."}</div>;
  }

  const baseAllocation = Object.entries(result.recommendation.base_strategy.allocation);
  const recommendedAllocation = Object.entries(result.recommendation.recommended_strategy.allocation);

  return (
    <div className="app-page">
      <header className="app-page-header">
        <div>
          <div className="eyebrow">Strategy</div>
          <h1>Base strategy vs market-aware recommendation</h1>
          <p>
            Compare your original long-term allocation with the current market-adjusted strategy.
          </p>
        </div>
      </header>

      <div className="app-two-column">
        <section className="app-panel">
          <div className="section-heading">
            <h2>Base strategy</h2>
            <p>Your portfolio before market regime adjustments.</p>
          </div>
          <div className="allocation-list">
            {baseAllocation.map(([asset, value]) => (
              <div key={asset} className="allocation-row">
                <span>{asset.replace(/_/g, " ")}</span>
                <strong>{Math.round(value * 100)}%</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="app-panel">
          <div className="section-heading">
            <h2>Recommended strategy</h2>
            <p>Adjusted to reflect the current market regime.</p>
          </div>
          <div className="allocation-list">
            {recommendedAllocation.map(([asset, value]) => (
              <div key={asset} className="allocation-row">
                <span>{asset.replace(/_/g, " ")}</span>
                <strong>{Math.round(value * 100)}%</strong>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
