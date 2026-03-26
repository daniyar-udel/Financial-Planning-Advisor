import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getStrategyResult } from "../api";
import { useAuth } from "../auth";

const steps = [
  "Analyzing your investor profile",
  "Evaluating market conditions",
  "Building your investment mix",
  "Estimating your goal probability",
] as const;

export default function StrategyLoadingPage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setActiveStep((current) => Math.min(current + 1, steps.length - 1));
    }, 950);

    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    async function buildResult() {
      if (!token) {
        return;
      }

      try {
        const result = await getStrategyResult(token);
        sessionStorage.setItem("strategy_result", JSON.stringify(result));
        window.setTimeout(() => navigate("/strategy/result"), 2500);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to build your strategy.");
      }
    }

    void buildResult();
  }, [navigate, token]);

  return (
    <div className="loading-shell">
      <div className="brand-haze brand-haze-left" />
      <div className="brand-haze brand-haze-right" />
      <div className="loading-card">
        <div className="eyebrow">Personalized strategy</div>
        <h1>We&apos;re building your personalized portfolio.</h1>
        <p>
          The planning engine is translating your goal, finances, and market conditions
          into a long-term recommendation designed for realistic decision making.
        </p>

        <div className="loading-showcase">
          <div className="loading-curve" aria-hidden="true">
            <div className="loading-line loading-line-soft" />
            <div className="loading-line loading-line-strong" />
          </div>

          <div className="loading-steps">
            {steps.map((step, index) => (
              <div
                key={step}
                className={`loading-step${index <= activeStep ? " loading-step-active" : ""}`}
              >
                <span className="loading-check">
                  {index < activeStep ? "Done" : index === activeStep ? "Now" : "Next"}
                </span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </div>

        {error ? <p className="error-message">{error}</p> : null}
      </div>
    </div>
  );
}
