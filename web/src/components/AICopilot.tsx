import { useMemo, useState } from "react";

import { sendAgentMessage } from "../api";
import { useAuth } from "../auth";
import type { AgentChatMessage } from "../types";

const INITIAL_MESSAGE: AgentChatMessage = {
  role: "assistant",
  content:
    "I'm your AI investment copilot. Ask me about your portfolio, goal probability, or how current market conditions affect your strategy.",
};

const FALLBACK_PROMPTS = [
  "Why is my probability of success this low?",
  "How can I improve my plan?",
  "Why is my portfolio allocated this way?",
  "How does the current market regime affect my strategy?",
];

export default function AICopilot() {
  const { token } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<AgentChatMessage[]>([INITIAL_MESSAGE]);
  const [suggestedPrompts, setSuggestedPrompts] = useState(FALLBACK_PROMPTS);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [providerLabel, setProviderLabel] = useState("Ready");
  const [providerTone, setProviderTone] = useState<"neutral" | "active" | "fallback">("neutral");

  const conversationHistory = useMemo(
    () => messages.filter((message) => message !== INITIAL_MESSAGE),
    [messages],
  );

  async function handleSubmit(nextMessage?: string) {
    const content = (nextMessage ?? draft).trim();
    if (!content || !token || isSending) {
      return;
    }

    const nextUserMessage: AgentChatMessage = {
      role: "user",
      content,
    };

    setMessages((current) => [...current, nextUserMessage]);
    setDraft("");
    setIsSending(true);
    setError(null);

    try {
      const response = await sendAgentMessage(token, content, conversationHistory);
      setSuggestedPrompts(response.sample_prompts);
      if (response.fallback_used) {
        setProviderLabel("Fallback mode");
        setProviderTone("fallback");
      } else {
        setProviderLabel("Groq active");
        setProviderTone("active");
      }
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.reply,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to contact the AI copilot.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <>
      <button
        type="button"
        className="copilot-trigger"
        onClick={() => setIsOpen((current) => !current)}
      >
        {isOpen ? "Close copilot" : "Ask AI"}
      </button>

      {isOpen ? (
        <section className="copilot-panel" aria-label="AI investment copilot">
          <div className="copilot-header">
            <div>
              <span className="eyebrow">AI Copilot</span>
              <h3>Ask about your plan</h3>
              <div className={`copilot-provider copilot-provider-${providerTone}`}>{providerLabel}</div>
            </div>
            <button
              type="button"
              className="copilot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close AI copilot"
            >
              x
            </button>
          </div>

          <div className="copilot-prompts">
            {suggestedPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="copilot-prompt"
                onClick={() => void handleSubmit(prompt)}
                disabled={isSending}
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="copilot-messages">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`copilot-message copilot-message-${message.role}`}
              >
                <span>{message.role === "assistant" ? "AI" : "You"}</span>
                <p>{message.content}</p>
              </div>
            ))}
            {isSending ? <div className="copilot-status">AI copilot is thinking...</div> : null}
          </div>

          <form
            className="copilot-composer"
            onSubmit={(event) => {
              event.preventDefault();
              void handleSubmit();
            }}
          >
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask why your allocation looks this way, what to change, or how the market affects your plan..."
              rows={3}
            />
            <button type="submit" className="primary-button slim-button" disabled={isSending}>
              Send
            </button>
          </form>

          {error ? <p className="error-message">{error}</p> : null}
        </section>
      ) : null}
    </>
  );
}
