import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth";

const signupHighlights = [
  "Create an account first, then continue to the planning questionnaire",
  "Keep your strategy, profile inputs, and copilot in one workspace",
  "Review a portfolio result before ever placing a trade",
];

export default function SignupPage() {
  const navigate = useNavigate();
  const { signupUser } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await signupUser({ full_name: fullName, email, password });
      navigate("/onboarding");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create account.");
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
          <div className="eyebrow">Account setup</div>
          <h1>Start with an account, then let the platform build the plan.</h1>
          <p>
            Registration stays intentionally simple. The richer financial questions come
            next during onboarding so the flow stays clean and focused.
          </p>
          <div className="auth-highlight-list">
            {signupHighlights.map((item) => (
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
          <div className="eyebrow">Create account</div>
          <h2>Create your planning workspace</h2>
          <p>Sign up, then continue to onboarding and strategy generation.</p>

          <div className="field">
            <label htmlFor="signup-name">Full name</label>
            <input
              id="signup-name"
              className="text-input"
              type="text"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="signup-email">Email</label>
            <input
              id="signup-email"
              className="text-input"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="signup-password">Password</label>
            <input
              id="signup-password"
              className="text-input"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />
          </div>

          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Create account"}
          </button>
          {error ? <p className="error-message">{error}</p> : null}

          <p className="auth-footer">
            Already have an account? <Link to="/login">Log in</Link>
          </p>
        </form>
      </section>
    </div>
  );
}
