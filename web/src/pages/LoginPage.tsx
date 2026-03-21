import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth";

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
      navigate("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to log in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      <form className="auth-card" onSubmit={handleSubmit}>
        <div className="eyebrow">Welcome back</div>
        <h1>Log in to your account</h1>
        <p>Access your investment strategy, simulations, and saved profile.</p>

        <div className="field">
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
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
    </div>
  );
}
