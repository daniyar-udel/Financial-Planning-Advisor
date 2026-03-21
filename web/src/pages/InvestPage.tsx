import { Link } from "react-router-dom";

export default function InvestPage() {
  return (
    <div className="marketing-shell">
      <section className="marketing-hero">
        <div className="eyebrow">Invest</div>
        <h1>Build a personalized investment strategy before you ever place a trade.</h1>
        <p>
          AI Investment Strategy Advisor helps users translate a financial goal into a
          market-aware portfolio strategy, projected outcomes, and a clear action plan.
        </p>
        <div className="marketing-actions">
          <Link className="primary-button link-button" to="/signup">
            Get started
          </Link>
          <Link className="secondary-button link-button" to="/login">
            Log in
          </Link>
        </div>
      </section>

      <section className="marketing-grid">
        <article className="marketing-card">
          <h2>How it works</h2>
          <p>
            We combine your goal, timeline, savings capacity, and risk preference with
            market regime detection and Monte Carlo simulation.
          </p>
        </article>
        <article className="marketing-card">
          <h2>What you get</h2>
          <p>
            A recommended strategy profile, market-aware allocation, projected outcomes,
            and a plain-English explanation of why the plan fits.
          </p>
        </article>
        <article className="marketing-card">
          <h2>Why it matters</h2>
          <p>
            Instead of chasing stock predictions, the platform focuses on realistic
            long-term planning and goal feasibility.
          </p>
        </article>
      </section>
    </div>
  );
}
