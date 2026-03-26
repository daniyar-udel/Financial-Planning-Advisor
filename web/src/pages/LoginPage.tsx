import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth";

const loginHighlights = [
  "Review your latest strategy recommendation",
  "Continue from onboarding into your private workspace",
  "Use the AI copilot to explore plan tradeoffs",
];

export default function LoginPage() {
  const navigate = useNavigate();
  const { loginUser } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await loginUser({ email, password });
      navigate("/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to log in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="brand-haze brand-haze-left" />
      <div className="brand-haze brand-haze-right" />
      <section className="auth-layout">
        <div className="auth-aside surface surface-dark">
          <div className="eyebrow">Private workspace</div>
          <h1>Return to your guided investing workspace.</h1>
          <p>
            Log in to review your strategy, inspect simulations, and use the AI copilot
            across the planning workspace.
          </p>
          <div className="auth-highlight-list">
            {loginHighlights.map((item) => (
              <div key={item} className="auth-highlight-item">
                <span className="auth-highlight-mark">01</span>
                <p>{item}</p>
              </div>
            ))}
          </div>
          <Link className="ghost-button link-button" to="/invest">
            Back to invest
          </Link>
        </div>

        <form className="auth-card" onSubmit={handleSubmit}>
          <div className="eyebrow">Welcome back</div>
          <h2>Log in to your account</h2>
          <p>Access your strategy, profile inputs, simulations, and AI copilot.</p>

          <div className="field">
            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              className="text-input"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              className="text-input"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Log in"}
          </button>
          {error ? <p className="error-message">{error}</p> : null}

          <p className="auth-footer">
            Need an account? <Link to="/signup">Create one</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
