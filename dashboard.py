from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.advisor import build_advice
from app.schemas import UserProfile


st.set_page_config(
    page_title="AI Investment Strategy Advisor",
    page_icon="chart_with_upwards_trend",
    layout="wide",
)


def main() -> None:
    _inject_styles()

    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">AI Investment Strategy Advisor</div>
          <h1>Turn a long-term financial goal into a market-aware portfolio strategy.</h1>
          <p>
            This demo combines client preferences, strategy generation, market regime detection,
            adaptive allocation, and Monte Carlo simulation to help users understand how likely
            they are to reach a target over time.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1.45], gap="large")

    with left:
        profile = _render_input_panel()

    with right:
        advice = build_advice(profile)
        _render_summary(advice)
        _render_strategy_overview(advice)
        _render_charts(advice)
        _render_explanation(advice)


def _render_input_panel() -> UserProfile:
    st.markdown("### User Profile")
    st.caption("Use this panel to simulate a client profile and generate a personalized plan.")

    with st.container(border=True):
        age = st.slider("Age", min_value=18, max_value=70, value=28)
        annual_income = st.number_input(
            "Annual income ($)",
            min_value=10000,
            max_value=1000000,
            step=5000,
            value=90000,
        )
        savings_rate_percent = st.slider(
            "Savings rate (% of income)",
            min_value=0,
            max_value=50,
            value=15,
        )
        current_savings = st.number_input(
            "Current savings ($)",
            min_value=0,
            max_value=5000000,
            step=5000,
            value=15000,
        )
        monthly_contribution = st.number_input(
            "Monthly contribution ($)",
            min_value=0,
            max_value=100000,
            step=100,
            value=800,
        )
        goal_amount = st.number_input(
            "Target goal amount ($)",
            min_value=10000,
            max_value=10000000,
            step=10000,
            value=500000,
        )
        investment_horizon_years = st.slider(
            "Investment horizon (years)",
            min_value=1,
            max_value=40,
            value=25,
        )
        risk_preference_label = st.select_slider(
            "Self-reported risk preference",
            options=["low", "medium", "high"],
            value="medium",
        )

    return UserProfile(
        age=age,
        annual_income=float(annual_income),
        savings_rate=savings_rate_percent / 100,
        current_savings=float(current_savings),
        monthly_contribution=float(monthly_contribution),
        goal_amount=float(goal_amount),
        investment_horizon_years=investment_horizon_years,
        risk_preference=risk_preference_label,
    )


def _render_summary(advice) -> None:
    st.markdown("### Recommendation Snapshot")
    probability = advice.simulation.probability_of_reaching_goal
    success_label = _probability_label(probability)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Strategy Profile", advice.strategy_profile.replace("_", " ").title())
    col2.metric("Market Regime", advice.market_regime.replace("_", " ").title())
    col3.metric("Goal Probability", f"{probability:.0%}")
    col4.metric("Median Outcome", _format_currency(advice.simulation.median_terminal_value))

    st.markdown(
        f"""
        <div class="insight-card">
          <strong>Planning Signal:</strong> {success_label}. The current portfolio is adjusted using the
          detected market regime and projected over long-term simulated market paths.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_strategy_overview(advice) -> None:
    st.markdown("### Why This Strategy")
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        regime_label = advice.market_regime.replace("_", " ").title()
        strategy_label = advice.strategy_profile.title()
        probability = advice.simulation.probability_of_reaching_goal
        explanation_points = _strategy_reasoning(advice)

        bullets = "".join(f"<li>{point}</li>" for point in explanation_points)
        st.markdown(
            f"""
            <div class="strategy-card">
              <div class="strategy-kicker">Recommended Strategy</div>
              <h3>{strategy_label} allocation with {regime_label.lower()} market adjustment</h3>
              <p>
                The portfolio starts from your long-term preference profile, then adjusts exposure
                based on the current market regime to balance growth and downside risk.
              </p>
              <ul>{bullets}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class="probability-panel">
              <div class="probability-label">Probability Of Reaching Goal</div>
              <div class="probability-value">{probability:.0%}</div>
              <div class="probability-caption">{_probability_label(probability)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_charts(advice) -> None:
    allocation_col, projection_col = st.columns([0.95, 1.35], gap="large")

    with allocation_col:
        st.markdown("### Portfolio Allocation")
        allocation_mode = st.radio(
            "Portfolio view",
            options=["Adjusted allocation", "Base allocation"],
            horizontal=True,
            label_visibility="collapsed",
        )
        allocation = (
            advice.recommended_strategy.allocation
            if allocation_mode == "Adjusted allocation"
            else advice.base_strategy.allocation
        )
        st.plotly_chart(_allocation_chart(allocation), use_container_width=True)

        comp1, comp2 = st.columns(2)
        comp1.metric("Base Return", f"{advice.base_strategy.expected_annual_return:.1%}")
        comp2.metric("Recommended Return", f"{advice.recommended_strategy.expected_annual_return:.1%}")

        snapshot = advice.market_snapshot
        st.markdown("### Market Snapshot")
        snap1, snap2, snap3 = st.columns(3)
        snap1.metric("Volatility", f"{snapshot.annualized_volatility:.1%}")
        snap2.metric("Momentum", f"{snapshot.momentum_63d:.1%}")
        snap3.metric("Drawdown", f"{snapshot.drawdown_126d:.1%}")
        st.caption(f"Data as of: `{snapshot.as_of}`")

    with projection_col:
        st.markdown("### Projected Goal Outcomes")
        st.plotly_chart(_projection_chart(advice), use_container_width=True)

        sim = advice.simulation
        p1, p2, p3 = st.columns(3)
        p1.metric("P10 Outcome", _format_currency(sim.pessimistic_terminal_value))
        p2.metric("P50 Outcome", _format_currency(sim.median_terminal_value))
        p3.metric("P90 Outcome", _format_currency(sim.optimistic_terminal_value))

        st.markdown("### Strategy Comparison")
        comparison_df = pd.DataFrame(
            [
                {
                    "Strategy": "Base",
                    "Expected return": advice.base_strategy.expected_annual_return,
                    "Volatility": advice.base_strategy.annual_volatility,
                },
                {
                    "Strategy": "Recommended",
                    "Expected return": advice.recommended_strategy.expected_annual_return,
                    "Volatility": advice.recommended_strategy.annual_volatility,
                },
            ]
        )
        comparison_df["Expected return"] = comparison_df["Expected return"].map(lambda x: f"{x:.1%}")
        comparison_df["Volatility"] = comparison_df["Volatility"].map(lambda x: f"{x:.1%}")
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        gap = advice.recommended_strategy.expected_annual_return - advice.base_strategy.expected_annual_return
        st.caption(
            f"Market-aware adjustment changed expected annual return by {gap:+.1%} versus the base strategy."
        )


def _render_explanation(advice) -> None:
    st.markdown("### Advisor Narrative")
    st.markdown(
        f"""
        <div class="narrative-card">
          {advice.explanation}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _allocation_chart(allocation: dict[str, float]) -> go.Figure:
    df = pd.DataFrame(
        {
            "asset": [key.replace("_", " ").title() for key in allocation.keys()],
            "weight": list(allocation.values()),
        }
    )
    fig = px.pie(
        df,
        names="asset",
        values="weight",
        hole=0.55,
        color_discrete_sequence=["#0f766e", "#f59e0b", "#1d4ed8", "#dc2626", "#6b7280"],
    )
    fig.update_traces(textinfo="label+percent")
    fig.update_layout(
        margin=dict(t=20, l=0, r=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig


def _projection_chart(advice) -> go.Figure:
    projection_df = pd.DataFrame(
        [
            {
                "year": point.year,
                "pessimistic": point.pessimistic_value,
                "median": point.median_value,
                "optimistic": point.optimistic_value,
            }
            for point in advice.simulation.yearly_projection
        ]
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=projection_df["year"],
            y=projection_df["optimistic"],
            mode="lines",
            line=dict(color="#cbd5e1", width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=projection_df["year"],
            y=projection_df["pessimistic"],
            mode="lines",
            line=dict(color="#cbd5e1", width=0),
            fill="tonexty",
            fillcolor="rgba(15, 118, 110, 0.16)",
            name="P10-P90 range",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=projection_df["year"],
            y=projection_df["median"],
            mode="lines",
            line=dict(color="#0f766e", width=4),
            name="Median outcome",
        )
    )
    fig.add_hline(
        y=projection_df["median"].iloc[-1],
        line_dash="dot",
        line_color="#94a3b8",
        annotation_text="Median terminal value",
        annotation_position="top left",
    )
    fig.update_layout(
        margin=dict(t=10, l=10, r=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.0)",
        legend=dict(orientation="h", y=1.08, x=0.01),
        xaxis_title="Year",
        yaxis_title="Portfolio value ($)",
        yaxis_tickprefix="$",
    )
    return fig


def _probability_label(probability: float) -> str:
    if probability >= 0.8:
        return "This goal looks strong under the current assumptions"
    if probability >= 0.6:
        return "This plan is viable, but there is still meaningful uncertainty"
    return "This goal may require a higher savings rate, longer horizon, or more aggressive allocation"


def _strategy_reasoning(advice) -> list[str]:
    points = [
        f"Base strategy profile: {advice.strategy_profile.title()}",
        f"Current market regime: {advice.market_regime.replace('_', ' ').title()}",
        f"Recommended allocation emphasizes {', '.join(_top_assets(advice.recommended_strategy.allocation))}",
    ]

    probability = advice.simulation.probability_of_reaching_goal
    if probability < 0.6:
        points.append("The current plan may need stronger monthly contributions or a longer horizon to improve success odds.")
    elif probability < 0.8:
        points.append("The plan is credible, though long-term outcomes still depend on market uncertainty and saving consistency.")
    else:
        points.append("The current profile and contribution pattern produce a strong long-term probability of success.")

    return points


def _top_assets(allocation: dict[str, float]) -> list[str]:
    ranked = sorted(allocation.items(), key=lambda item: item[1], reverse=True)
    return [asset.replace("_", " ") for asset, _ in ranked[:2]]


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(20, 184, 166, 0.14), transparent 32%),
                radial-gradient(circle at top right, rgba(245, 158, 11, 0.14), transparent 28%),
                linear-gradient(180deg, #f8fafc 0%, #eef6f5 100%);
        }
        .hero {
            padding: 1.4rem 1.5rem 1.1rem 1.5rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.84);
            backdrop-filter: blur(8px);
            margin-bottom: 1rem;
        }
        .hero h1 {
            font-size: 2.2rem;
            line-height: 1.1;
            margin: 0.2rem 0 0.5rem 0;
            color: #0f172a;
        }
        .hero p {
            margin: 0;
            color: #334155;
            font-size: 1rem;
            max-width: 760px;
        }
        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.75rem;
            color: #0f766e;
            font-weight: 700;
        }
        .insight-card, .narrative-card {
            border-radius: 18px;
            padding: 1rem 1.1rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            background: rgba(255, 255, 255, 0.9);
            color: #0f172a;
        }
        .strategy-card, .probability-panel {
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            background: rgba(255, 255, 255, 0.92);
            color: #0f172a;
            min-height: 220px;
        }
        .strategy-card h3 {
            margin: 0.2rem 0 0.6rem 0;
            font-size: 1.25rem;
            color: #0f172a;
        }
        .strategy-card p {
            margin: 0 0 0.85rem 0;
            color: #334155;
        }
        .strategy-card ul {
            margin: 0;
            padding-left: 1.1rem;
            color: #0f172a;
        }
        .strategy-kicker {
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            color: #1d4ed8;
            font-weight: 700;
        }
        .probability-panel {
            background:
                linear-gradient(180deg, rgba(15, 118, 110, 0.96) 0%, rgba(13, 148, 136, 0.92) 100%);
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .probability-label {
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
            opacity: 0.85;
            font-weight: 700;
        }
        .probability-value {
            font-size: 3.2rem;
            line-height: 1;
            margin: 0.45rem 0 0.55rem 0;
            font-weight: 800;
        }
        .probability-caption {
            font-size: 1rem;
            line-height: 1.5;
            max-width: 18rem;
            opacity: 0.95;
        }
        .narrative-card {
            font-size: 1rem;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
else:
    main()
