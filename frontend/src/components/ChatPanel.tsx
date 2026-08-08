import { useState } from "react";
import { askQuestion, type AskResponse } from "../api";
import "./ChatPanel.css";

const FALLBACK_TEXT = "I don't have information on that in the knowledge base.";

const SAMPLE_QUESTIONS = [
  "What's your return policy?",
  "How do I reset my password?",
  "Can I cancel my subscription?",
  "What are your support hours?",
];

interface Message {
  role: "user" | "assistant";
  text: string;
  sources?: AskResponse["sources"];
  queryLogId?: number;
  responseTimeMs?: number;
  confidence?: number | null;
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage(question: string) {
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    const startTime = performance.now();

    try {
      const result = await askQuestion(question);
      const responseTimeMs = Math.round(performance.now() - startTime);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: result.answer,
          sources: result.sources,
          queryLogId: result.query_log_id,
          responseTimeMs,
          confidence: result.confidence,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSend() {
    sendMessage(input.trim());
  }

  return (
    <div className="chat-panel">
      <div className="message-list">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Ask a question about your uploaded documents to get started.</p>
            <div className="sample-chips">
              {SAMPLE_QUESTIONS.map((q) => (
                <button key={q} className="sample-chip" onClick={() => sendMessage(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) =>
          msg.role === "user" ? (
            <div key={i} className="message message--user">
              <div className="bubble">{msg.text}</div>
            </div>
          ) : (
            <div key={i} className="message message--assistant">
              <div className={msg.text === FALLBACK_TEXT ? "answer-text answer-text--fallback" : "answer-text"}>
                {msg.text}
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources-row">
                  {msg.sources.map((source) => (
                    <div key={source.ref} className="source-tag">
                      <span className="ref-number">{source.ref}</span>
                      <span>{source.section_title || "Untitled section"}</span>
                    </div>
                  ))}
                </div>
              )}
              {msg.responseTimeMs !== undefined && (
                <div className="response-meta">
                  Answered in {(msg.responseTimeMs / 1000).toFixed(1)}s
                  {msg.confidence !== null && msg.confidence !== undefined && (
                    <> · confidence {Math.round(msg.confidence * 100)}%</>
                  )}
                </div>
              )}
            </div>
          )
        )}
        {loading && <div className="thinking">Thinking…</div>}
      </div>

      <div className="chat-input-row">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about billing, shipping, returns…"
        />
        <button className="send-button" onClick={handleSend} disabled={loading}>
          Send
        </button>
      </div>

      <div className="tech-badge">RAG · pgvector · GPT-4o-mini</div>
    </div>
  );
}
