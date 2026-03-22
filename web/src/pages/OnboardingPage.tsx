import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getOnboardingProfile, saveOnboardingProfile } from "../api";
import { useAuth } from "../auth";
import type { GoalType, OnboardingProfilePayload, RiskPreference, StrategyPreference, StressResponse } from "../types";

const steps = [
  "Goal",
  "Personal",
  "Financial",
  "Risk",
  "Review",
] as const;

const defaultProfile: OnboardingProfilePayload = {
  goal_type: "long_term_wealth",
  goal_amount: 500000,
  investment_horizon_years: 25,
  age: 28,
  date_of_birth: "1998-01-01",
  marital_status: "single",
  address: "",
  annual_income: 90000,
  current_savings: 15000,
  monthly_contribution: 800,
  savings_rate: 0.15,
  risk_preference: "medium",
  stress_response: "hold",
  strategy_preference: "classic",
};

export default function OnboardingPage() {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [stepIndex, setStepIndex] = useState(0);
  const [profile, setProfile] = useState<OnboardingProfilePayload>(defaultProfile);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProfile() {
      if (!token) {
        return;
      }

      try {
        const existing = await getOnboardingProfile(token);
        if (existing) {
          const { user_id: _userId, ...payload } = existing;
          setProfile(payload);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load onboarding profile.");
      } finally {
        setLoading(false);
      }
    }

    void loadProfile();
  }, [token]);

  async function handleFinish() {
    if (!token) {
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await saveOnboardingProfile(token, profile);
      navigate("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save onboarding profile.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div className="route-loader">Preparing onboarding...</div>;
  }

  return (
    <div className="onboarding-shell">
      <section className="onboarding-card">
        <div className="onboarding-header">
          <div>
            <div className="eyebrow">Onboarding</div>
            <h1>Let&apos;s build your investment strategy, {user?.full_name.split(" ")[0]}.</h1>
            <p>
              We&apos;ll ask a few questions about your goal, profile, finances, and
              investing behavior before generating your strategy.
            </p>
          </div>
          <div className="step-indicator">
            <span>Step {stepIndex + 1} of {steps.length}</span>
            <strong>{steps[stepIndex]}</strong>
          </div>
        </div>

        <div className="progress-row">
          {steps.map((step, index) => (
            <div
              key={step}
              className={`progress-pill${index <= stepIndex ? " progress-pill-active" : ""}`}
            >
              {step}
            </div>
          ))}
        </div>

        <div className="onboarding-body">
          {stepIndex === 0 ? (
            <div className="onboarding-grid">
              <SelectField
                label="What are you investing for?"
                value={profile.goal_type}
                onChange={(value) =>
                  setProfile((current) => ({ ...current, goal_type: value as GoalType }))
                }
                options={[
                  ["long_term_wealth", "Long-term wealth"],
                  ["retirement", "Retirement"],
                  ["home_purchase", "Home purchase"],
                  ["financial_independence", "Financial independence"],
                  ["custom_goal", "Custom goal"],
                ]}
              />
              <NumberField
                label="Target goal amount"
                value={profile.goal_amount}
                min={10000}
                step={10000}
                prefix="$"
                onChange={(value) => setProfile((current) => ({ ...current, goal_amount: value }))}
              />
              <NumberField
                label="Investment horizon"
                value={profile.investment_horizon_years}
                min={1}
                max={50}
                suffix="years"
                onChange={(value) =>
                  setProfile((current) => ({ ...current, investment_horizon_years: value }))
                }
              />
            </div>
          ) : null}

          {stepIndex === 1 ? (
            <div className="onboarding-grid">
              <NumberField
                label="Age"
                value={profile.age}
                min={18}
                max={100}
                onChange={(value) => setProfile((current) => ({ ...current, age: value }))}
              />
              <TextField
                label="Date of birth"
                type="date"
                value={profile.date_of_birth}
                onChange={(value) =>
                  setProfile((current) => ({ ...current, date_of_birth: value }))
                }
              />
              <SelectField
                label="Marital status"
                value={profile.marital_status}
                onChange={(value) =>
                  setProfile((current) => ({ ...current, marital_status: value }))
                }
                options={[
                  ["single", "Single"],
                  ["married", "Married"],
                  ["partnered", "Partnered"],
                ]}
              />
              <TextField
                label="Address"
                value={profile.address}
                onChange={(value) => setProfile((current) => ({ ...current, address: value }))}
              />
            </div>
          ) : null}

          {stepIndex === 2 ? (
            <div className="onboarding-grid">
              <NumberField
                label="Annual income"
                value={profile.annual_income}
                min={10000}
                step={5000}
                prefix="$"
                onChange={(value) =>
                  setProfile((current) => ({ ...current, annual_income: value }))
                }
              />
              <NumberField
                label="Current savings"
                value={profile.current_savings}
                min={0}
                step={5000}
                prefix="$"
                onChange={(value) =>
                  setProfile((current) => ({ ...current, current_savings: value }))
                }
              />
              <NumberField
                label="Monthly contribution"
                value={profile.monthly_contribution}
                min={0}
                step={100}
                prefix="$"
                onChange={(value) =>
                  setProfile((current) => ({ ...current, monthly_contribution: value }))
                }
              />
              <NumberField
                label="Savings rate"
                value={profile.savings_rate * 100}
                min={0}
                max={50}
                suffix="%"
                onChange={(value) =>
                  setProfile((current) => ({ ...current, savings_rate: value / 100 }))
                }
              />
            </div>
          ) : null}

          {stepIndex === 3 ? (
            <div className="onboarding-grid">
              <SelectField
                label="Risk preference"
                value={profile.risk_preference}
                onChange={(value) =>
                  setProfile((current) => ({ ...current, risk_preference: value as RiskPreference }))
                }
                options={[
                  ["low", "Low"],
                  ["medium", "Medium"],
                  ["high", "High"],
                ]}
              />
              <SelectField
                label="If markets drop sharply, what would you do?"
                value={profile.stress_response}
                onChange={(value) =>
                  setProfile((current) => ({ ...current, stress_response: value as StressResponse }))
                }
                options={[
                  ["buy_more", "Buy more"],
                  ["hold", "Hold steady"],
                  ["sell_some", "Sell some"],
                  ["sell_all", "Sell all"],
                ]}
              />
              <SelectField
                label="Preferred strategy style"
                value={profile.strategy_preference}
                onChange={(value) =>
                  setProfile((current) => ({
                    ...current,
                    strategy_preference: value as StrategyPreference,
                  }))
                }
                options={[
                  ["classic", "Classic"],
                  ["responsible", "Responsible"],
                  ["income_focused", "Income focused"],
                ]}
              />
            </div>
          ) : null}

          {stepIndex === 4 ? (
            <div className="review-grid">
              <ReviewItem label="Goal" value={profile.goal_type.replace(/_/g, " ")} />
              <ReviewItem label="Goal amount" value={`$${profile.goal_amount.toLocaleString()}`} />
              <ReviewItem label="Horizon" value={`${profile.investment_horizon_years} years`} />
              <ReviewItem label="Age" value={String(profile.age)} />
              <ReviewItem label="Marital status" value={profile.marital_status} />
              <ReviewItem label="Annual income" value={`$${profile.annual_income.toLocaleString()}`} />
              <ReviewItem label="Current savings" value={`$${profile.current_savings.toLocaleString()}`} />
              <ReviewItem label="Monthly contribution" value={`$${profile.monthly_contribution.toLocaleString()}`} />
              <ReviewItem label="Risk preference" value={profile.risk_preference} />
              <ReviewItem label="Stress response" value={profile.stress_response.replace(/_/g, " ")} />
              <ReviewItem label="Strategy preference" value={profile.strategy_preference.replace(/_/g, " ")} />
            </div>
          ) : null}
        </div>

        {error ? <p className="error-message">{error}</p> : null}

        <div className="onboarding-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={() => setStepIndex((current) => Math.max(current - 1, 0))}
            disabled={stepIndex === 0}
          >
            Back
          </button>
          {stepIndex < steps.length - 1 ? (
            <button
              className="primary-button slim-button"
              type="button"
              onClick={() => setStepIndex((current) => Math.min(current + 1, steps.length - 1))}
            >
              Continue
            </button>
          ) : (
            <button className="primary-button slim-button" type="button" onClick={handleFinish} disabled={saving}>
              {saving ? "Saving profile..." : "Finish onboarding"}
            </button>
          )}
        </div>
      </section>
    </div>
  );
}

function NumberField(props: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  prefix?: string;
  suffix?: string;
}) {
  return (
    <div className="field">
      <label>{props.label}</label>
      <div className="input-shell">
        {props.prefix ? <span>{props.prefix}</span> : null}
        <input
          type="number"
          value={props.value}
          onChange={(event) => props.onChange(Number(event.target.value))}
          min={props.min}
          max={props.max}
          step={props.step ?? 1}
        />
        {props.suffix ? <span>{props.suffix}</span> : null}
      </div>
    </div>
  );
}

function TextField(props: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}) {
  return (
    <div className="field">
      <label>{props.label}</label>
      <input
        className="standalone-input"
        type={props.type ?? "text"}
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
      />
    </div>
  );
}

function SelectField(props: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<[string, string]>;
}) {
  return (
    <div className="field">
      <label>{props.label}</label>
      <select value={props.value} onChange={(event) => props.onChange(event.target.value)}>
        {props.options.map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
    </div>
  );
}

function ReviewItem(props: { label: string; value: string }) {
  return (
    <div className="review-item">
      <span>{props.label}</span>
      <strong>{props.value}</strong>
    </div>
  );
}
