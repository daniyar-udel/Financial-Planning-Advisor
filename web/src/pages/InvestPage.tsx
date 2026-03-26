import { Link } from "react-router-dom";

const trustStats = [
  { label: "Planning engine", value: "Goal-based" },
  { label: "Allocation logic", value: "Market-aware" },
  { label: "Outcome model", value: "Monte Carlo" },
  { label: "Assistant layer", value: "AI copilot" },
];

const journey = [
  {
    step: "01",
    title: "Tell us what you are building toward",
    body: "Define the goal, target amount, contribution level, and horizon so the strategy starts from a real financial objective.",
  },
  {
    step: "02",
    title: "We build the strategy around your profile",
    body: "The system combines your financial inputs, risk preference, and the current market regime to shape the recommendation.",
  },
  {
    step: "03",
    title: "Review, simulate, and ask AI",
    body: "See the portfolio, understand goal feasibility, and use the AI copilot for explanation and what-if analysis.",
  },
];

const principles = [
  {
    title: "Goal-first planning",
    body: "The product is built around the question of how to reach a target responsibly, not around predicting the next stock move.",
  },
  {
    title: "Adaptive portfolio logic",
    body: "The allocation stays aligned to the user's long-term risk band while adjusting to the current market environment.",
  },
  {
    title: "Probability over certainty",
    body: "Monte Carlo simulation helps frame the plan in distributions and ranges rather than a single deterministic outcome.",
  },
];

const faqs = [
  {
    question: "Is this meant to replace a broker or advisor?",
    answer:
      "No. The platform focuses on planning, explanation, and strategy exploration. It does not execute trades or replace regulated financial advice.",
  },
  {
    question: "Why use AI in a planning product?",
    answer:
      "AI acts as a copilot on top of the planning engine. It explains allocation decisions, market context, and what-if tradeoffs without replacing the underlying strategy logic.",
  },
  {
    question: "Who is this useful for?",
    answer:
      "It is designed for users who want a more realistic investing workflow than a stock tip or one-page calculator, whether they are just starting or already investing regularly.",
  },
];

export default function InvestPage() {
  return (
    <div className="marketing-shell">
      <div className="brand-haze brand-haze-left" />
      <div className="brand-haze brand-haze-right" />

      <header className="site-nav">
        <Link className="site-brand" to="/invest">
          <span className="site-brand-mark">AISA</span>
          <span>AI Investment Strategy Advisor</span>
        </Link>
        <nav className="site-nav-links">
          <a href="#process">Process</a>
          <a href="#copilot">AI copilot</a>
          <a href="#faq">FAQ</a>
        </nav>
        <div className="site-nav-actions">
          <Link className="ghost-button link-button" to="/login">
            Log in
          </Link>
          <Link className="primary-button link-button" to="/signup">
            Get started
          </Link>
        </div>
      </header>

      <section className="marketing-hero surface">
        <div className="hero-copy">
          <div className="eyebrow">Guided investing platform</div>
          <h1>Build a long-term investment strategy around your actual goal.</h1>
          <p>
            Move from onboarding to a personalized portfolio recommendation with a calmer,
            more realistic investing workflow focused on goals, risk, and market-aware
            planning.
          </p>
          <div className="hero-chip-row">
            <span className="hero-chip">Goal-based planning</span>
            <span className="hero-chip">Market-aware allocation</span>
            <span className="hero-chip">Monte Carlo outcomes</span>
            <span className="hero-chip">AI copilot Q&amp;A</span>
          </div>
          <div className="marketing-actions">
            <Link className="primary-button link-button" to="/signup">
              Build my strategy
            </Link>
            <Link className="secondary-button link-button" to="/login">
              View my workspace
            </Link>
          </div>
          <p className="hero-footnote">
            Educational planning workflow. No brokerage linking, no trade execution, no
            stock-picking hype.
          </p>
        </div>

        <div className="hero-visual">
          <div className="hero-visual-card hero-visual-primary">
            <span>Recommended strategy</span>
            <strong>Moderate, market-aware</strong>
            <p>Designed to support long-term growth while staying inside a stable risk band.</p>
          </div>
          <div className="hero-visual-grid">
            <div className="hero-visual-card">
              <span>Goal probability</span>
              <strong>62%</strong>
            </div>
            <div className="hero-visual-card">
              <span>Likely accumulation</span>
              <strong>$582k</strong>
            </div>
          </div>
          <div className="hero-curve" aria-hidden="true">
            <div className="hero-curve-band hero-curve-band-wide" />
            <div className="hero-curve-band hero-curve-band-mid" />
            <div className="hero-curve-line" />
          </div>
        </div>
      </section>

      <section className="trust-strip surface surface-muted">
        {trustStats.map((item) => (
          <article key={item.label} className="trust-stat">
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </section>

      <section id="process" className="section-block">
        <div className="section-intro">
          <div className="eyebrow">How it works</div>
          <h2>Structured like a real investing service, not a one-off calculator.</h2>
          <p>
            The product guides the user through a planning workflow, then reveals a
            strategy with feasibility analysis and a private workspace for ongoing review.
          </p>
        </div>
        <div className="journey-grid">
          {journey.map((item) => (
            <article key={item.step} className="journey-card surface">
              <span className="journey-step">{item.step}</span>
              <h3>{item.title}</h3>
              <p>{item.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="feature-band">
        <div className="section-intro">
          <div className="eyebrow">Why this feels different</div>
          <h2>Built for people who want a plan they can actually reason about.</h2>
        </div>
        <div className="principles-grid">
          {principles.map((item) => (
            <article key={item.title} className="principle-card surface">
              <h3>{item.title}</h3>
              <p>{item.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="copilot" className="assistant-callout surface">
        <div>
          <div className="eyebrow">AI copilot</div>
          <h2>An assistant layered on top of the strategy, not a black-box allocator.</h2>
          <p>
            The portfolio is computed by the planning engine. The AI copilot explains
            allocations, surfaces strategy context, and helps explore what-if changes with
            tool calling and retrieval.
          </p>
        </div>
        <div className="assistant-panel">
          <div className="assistant-badge">Groq + LangGraph</div>
          <ul className="assistant-list">
            <li>Explain why the current allocation looks this way</li>
            <li>Explore changes to contribution level or horizon</li>
            <li>Ground answers in strategy-aware finance context</li>
          </ul>
        </div>
      </section>

      <section id="faq" className="section-block">
        <div className="section-intro">
          <div className="eyebrow">FAQ</div>
          <h2>Still deciding if this planning workflow fits your use case?</h2>
        </div>
        <div className="faq-grid">
          {faqs.map((item) => (
            <article key={item.question} className="faq-card surface">
              <h3>{item.question}</h3>
              <p>{item.answer}</p>
            </article>
          ))}
        </div>
      </section>

      <footer className="marketing-footer">
        <div>
          <strong>AI Investment Strategy Advisor</strong>
          <p>
            Educational investing workflow for long-term planning, AI explanation, and
            product-grade decision support.
          </p>
        </div>
        <p>
          This platform does not provide financial advice and does not execute trades.
          Users remain responsible for their own investing decisions.
        </p>
      </footer>
    </div>
  );
}
