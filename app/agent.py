from __future__ import annotations

import hashlib
import json
import math
import re
from functools import lru_cache
from pathlib import Path
from textwrap import dedent
from typing import Optional

from app.advisor import build_advice
from app.config import settings
from app.onboarding import build_strategy_result
from app.schemas import AgentChatRequest, AgentChatResponse, StrategyResultResponse, UserProfile, UserResponse

SAMPLE_PROMPTS = [
    "Why is my probability of success this low?",
    "How can I improve my plan?",
    "Why is my portfolio allocated this way?",
    "What if I invest $300 more each month?",
]


def chat_with_copilot(user: UserResponse, payload: AgentChatRequest) -> AgentChatResponse:
    strategy_result = build_strategy_result(user)
    fallback_reply = _build_fallback_reply(payload.message, strategy_result)

    try:
        reply, provider, model = _call_langgraph_agent(strategy_result, payload)
    except Exception:
        return AgentChatResponse(
            reply=fallback_reply,
            provider="fallback",
            model="local-strategy-copilot",
            fallback_used=True,
            sample_prompts=SAMPLE_PROMPTS,
        )

    return AgentChatResponse(
        reply=reply,
        provider=provider,
        model=model,
        fallback_used=False,
        sample_prompts=SAMPLE_PROMPTS,
    )


def _call_langgraph_agent(
    strategy_result: StrategyResultResponse,
    payload: AgentChatRequest,
) -> tuple[str, str, str]:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
    from langchain_core.tools import tool
    from langchain_groq import ChatGroq
    from langgraph.graph import MessagesState, START, StateGraph
    from langgraph.prebuilt import ToolNode, tools_condition

    tools = _build_agent_tools(strategy_result)
    model = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        base_url=settings.groq_base_url,
        temperature=0.2,
        timeout=settings.groq_timeout_seconds,
        max_retries=2,
    ).bind_tools(tools)

    system_prompt = _build_system_prompt(strategy_result)

    def assistant(state: MessagesState) -> dict[str, list[AIMessage]]:
        reply = model.invoke([SystemMessage(content=system_prompt), *state["messages"]])
        return {"messages": [reply]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    graph = builder.compile()

    messages = _to_langchain_messages(payload)
    result = graph.invoke({"messages": messages}, config={"recursion_limit": 8})

    last_message = next(
        (
            message
            for message in reversed(result["messages"])
            if isinstance(message, AIMessage) and _message_text(message)
        ),
        None,
    )

    if last_message is None:
        raise RuntimeError("Agent returned no final AI message.")

    return _message_text(last_message), "groq-langgraph", settings.groq_model


def _build_agent_tools(strategy_result: StrategyResultResponse) -> list:
    from langchain_core.tools import tool

    profile = strategy_result.onboarding_profile
    recommendation = strategy_result.recommendation
    simulation = recommendation.simulation

    @tool
    def get_current_strategy() -> str:
        """Return the user's current strategy, allocation, and success metrics."""

        payload = {
            "goal_amount": profile.goal_amount,
            "investment_horizon_years": profile.investment_horizon_years,
            "risk_preference": profile.risk_preference,
            "strategy_profile": recommendation.strategy_profile,
            "market_regime": recommendation.market_regime,
            "goal_probability": round(simulation.probability_of_reaching_goal, 4),
            "probability_of_reaching_90_percent_of_goal": round(
                simulation.probability_of_reaching_90_percent_of_goal,
                4,
            ),
            "median_accumulated_amount": round(simulation.median_terminal_value, 2),
            "median_goal_gap": round(simulation.median_goal_gap, 2),
            "required_monthly_contribution_for_80_percent_success": round(
                simulation.required_monthly_contribution_for_80_percent_success,
                2,
            ),
            "base_strategy_allocation": recommendation.base_strategy.allocation,
            "recommended_strategy_allocation": recommendation.recommended_strategy.allocation,
        }
        return json.dumps(payload, indent=2)

    @tool
    def get_market_context() -> str:
        """Return details about the current detected market regime and why it matters."""

        snapshot = recommendation.market_snapshot
        return (
            f"Market regime: {recommendation.market_regime.replace('_', ' ')}. "
            f"Annualized volatility: {snapshot.annualized_volatility:.1%}. "
            f"63-day momentum: {snapshot.momentum_63d:.1%}. "
            f"126-day drawdown: {snapshot.drawdown_126d:.1%}. "
            f"Latest close: {snapshot.latest_close:,.2f}. "
            f"As of: {snapshot.as_of}."
        )

    @tool
    def run_what_if(
        monthly_contribution: Optional[float] = None,
        investment_horizon_years: Optional[int] = None,
        goal_amount: Optional[float] = None,
        risk_preference: Optional[str] = None,
    ) -> str:
        """
        Run a hypothetical scenario by changing contribution, horizon, goal amount,
        or risk preference.
        """

        adjusted_profile = UserProfile(
            age=profile.age,
            annual_income=profile.annual_income,
            savings_rate=profile.savings_rate,
            current_savings=profile.current_savings,
            monthly_contribution=monthly_contribution
            if monthly_contribution is not None
            else profile.monthly_contribution,
            goal_amount=goal_amount if goal_amount is not None else profile.goal_amount,
            investment_horizon_years=investment_horizon_years
            if investment_horizon_years is not None
            else profile.investment_horizon_years,
            risk_preference=_normalize_risk_preference(
                risk_preference if risk_preference is not None else profile.risk_preference
            ),
        )
        what_if = build_advice(adjusted_profile)
        scenario = {
            "strategy_profile": what_if.strategy_profile,
            "market_regime": what_if.market_regime,
            "recommended_strategy_allocation": what_if.recommended_strategy.allocation,
            "goal_probability": round(what_if.simulation.probability_of_reaching_goal, 4),
            "median_accumulated_amount": round(what_if.simulation.median_terminal_value, 2),
            "median_goal_gap": round(what_if.simulation.median_goal_gap, 2),
            "required_monthly_contribution_for_80_percent_success": round(
                what_if.simulation.required_monthly_contribution_for_80_percent_success,
                2,
            ),
        }
        return json.dumps(scenario, indent=2)

    @tool
    def retrieve_knowledge(query: str) -> str:
        """Retrieve grounded educational context from the product knowledge base."""

        store = _get_vector_store()
        retriever = store.as_retriever(search_kwargs={"k": 3})
        documents = retriever.invoke(query)
        if not documents:
            return "No additional knowledge base context found."
        return "\n\n".join(
            f"Source: {document.metadata.get('source', 'unknown')}\n{document.page_content}"
            for document in documents
        )

    return [get_current_strategy, get_market_context, run_what_if, retrieve_knowledge]


@lru_cache(maxsize=1)
def _get_vector_store():
    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_core.embeddings import Embeddings

    class HashEmbeddings(Embeddings):
        def __init__(self, dimensions: int = 128) -> None:
            self.dimensions = dimensions

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return [self._embed(text) for text in texts]

        def embed_query(self, text: str) -> list[float]:
            return self._embed(text)

        def _embed(self, text: str) -> list[float]:
            vector = [0.0] * self.dimensions
            tokens = re.findall(r"[a-zA-Z0-9_]+", text.lower())
            if not tokens:
                return vector
            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                for index in range(0, len(digest), 2):
                    bucket = digest[index] % self.dimensions
                    sign = 1.0 if digest[index + 1] % 2 == 0 else -1.0
                    vector[bucket] += sign
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            return [value / norm for value in vector]

    knowledge_dir = Path(__file__).with_name("knowledge_base")
    documents = [
        Document(
            page_content=path.read_text(encoding="utf-8"),
            metadata={"source": path.name},
        )
        for path in sorted(knowledge_dir.glob("*.md"))
    ]
    store = Chroma(
        collection_name="investment_copilot_knowledge",
        embedding_function=HashEmbeddings(),
    )
    if documents:
        store.add_documents(documents)
    return store


def _build_system_prompt(strategy_result: StrategyResultResponse) -> str:
    recommendation = strategy_result.recommendation
    profile = strategy_result.onboarding_profile
    simulation = recommendation.simulation
    base_allocation = _format_allocation(recommendation.base_strategy.allocation)
    recommended_allocation = _format_allocation(recommendation.recommended_strategy.allocation)

    return dedent(
        f"""
        You are the AI copilot inside an investment planning product.
        You help users understand a strategy that has already been computed by the system.

        Operating rules:
        - Stay grounded in the portfolio data and tool outputs.
        - Use tools whenever the user asks about current strategy details, market context,
          or hypothetical changes.
        - Use retrieve_knowledge for conceptual explanations about diversification,
          risk, market regimes, and Monte Carlo outcomes.
        - Never invent performance numbers, instruments, or unsupported guarantees.
        - Do not present your answer as financial advice.
        - Keep answers concise, helpful, and product-style.

        Current strategy context:
        - Goal type: {profile.goal_type}
        - Goal amount: ${profile.goal_amount:,.0f}
        - Investment horizon: {profile.investment_horizon_years} years
        - Monthly contribution: ${profile.monthly_contribution:,.0f}
        - Current savings: ${profile.current_savings:,.0f}
        - Risk preference: {profile.risk_preference}
        - Strategy preference: {profile.strategy_preference}
        - Strategy profile: {recommendation.strategy_profile}
        - Market regime: {recommendation.market_regime}
        - Goal probability: {simulation.probability_of_reaching_goal:.0%}
        - Probability of reaching 90% of goal: {simulation.probability_of_reaching_90_percent_of_goal:.0%}
        - Median accumulated amount: ${simulation.median_terminal_value:,.0f}
        - Median goal gap: ${simulation.median_goal_gap:,.0f}
        - Base strategy allocation: {base_allocation}
        - Recommended strategy allocation: {recommended_allocation}
        - Product explanation: {recommendation.explanation}
        - Horizon note: {strategy_result.strategy_horizon_note}
        - Disclaimer: {strategy_result.disclaimer}
        """
    ).strip()


def _to_langchain_messages(payload: AgentChatRequest) -> list:
    from langchain_core.messages import AIMessage, HumanMessage

    messages = []
    for message in payload.history[-8:]:
        if message.role == "assistant":
            messages.append(AIMessage(content=message.content))
        else:
            messages.append(HumanMessage(content=message.content))
    messages.append(HumanMessage(content=payload.message))
    return messages


def _message_text(message) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_chunks = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_chunks.append(str(block.get("text", "")))
            else:
                text_chunks.append(str(block))
        return "\n".join(chunk.strip() for chunk in text_chunks if chunk).strip()
    return str(content).strip()


def _normalize_risk_preference(risk_preference: str) -> str:
    normalized = risk_preference.strip().lower()
    if normalized in {"low", "medium", "high"}:
        return normalized
    return "medium"


def _build_fallback_reply(message: str, strategy_result: StrategyResultResponse) -> str:
    recommendation = strategy_result.recommendation
    simulation = recommendation.simulation
    profile = strategy_result.onboarding_profile
    normalized = message.lower()

    if "probability" in normalized or "chance" in normalized or "goal" in normalized:
        return (
            f"Your current probability of reaching the full goal is "
            f"{simulation.probability_of_reaching_goal:.0%}. In the median scenario, "
            f"you would accumulate about ${simulation.median_terminal_value:,.0f}. "
            f"If you want stronger odds, the model estimates about "
            f"${simulation.required_monthly_contribution_for_80_percent_success:,.0f} "
            f"per month for an 80% success rate."
        )

    if "improve" in normalized or "better" in normalized or "change" in normalized:
        return (
            f"The strongest lever right now is monthly contribution. You currently invest "
            f"${profile.monthly_contribution:,.0f} per month, while the plan estimates about "
            f"${simulation.required_monthly_contribution_for_80_percent_success:,.0f} per month "
            f"for an 80% success rate. You could also extend the horizon or lower the target amount."
        )

    if "what if" in normalized or "invest" in normalized:
        return (
            f"If you increase monthly investing from ${profile.monthly_contribution:,.0f}, "
            "your probability of success should improve, and the agent can estimate that once "
            "the Groq-powered tool layer is active."
        )

    if "bond" in normalized or "allocated" in normalized or "portfolio" in normalized:
        return (
            f"Your portfolio is shaped by both your {recommendation.strategy_profile} strategy profile "
            f"and the current {recommendation.market_regime.replace('_', ' ')} market regime. "
            f"The recommended allocation is {_format_allocation(recommendation.recommended_strategy.allocation)}. "
            f"This keeps the plan aligned with your risk preference while adapting to current market conditions."
        )

    if "market" in normalized or "regime" in normalized or "volatility" in normalized:
        return (
            f"The current market regime is {recommendation.market_regime.replace('_', ' ')}. "
            f"That affects how defensive or growth-oriented the recommended mix becomes. "
            f"Right now, the adjusted allocation is {_format_allocation(recommendation.recommended_strategy.allocation)}."
        )

    return (
        f"Your plan is built for a {profile.investment_horizon_years}-year horizon with a "
        f"{recommendation.strategy_profile} strategy profile. The current recommendation is "
        f"{_format_allocation(recommendation.recommended_strategy.allocation)}, and the model "
        f"estimates a {simulation.probability_of_reaching_goal:.0%} probability of reaching "
        f"your full goal."
    )


def _format_allocation(allocation: dict[str, float]) -> str:
    return ", ".join(
        f"{asset.replace('_', ' ')} {weight:.0%}" for asset, weight in allocation.items()
    )
