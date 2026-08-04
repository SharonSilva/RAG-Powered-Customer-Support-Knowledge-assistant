import { useState } from "react";
import { askQuestion, type AskResponse } from "../api";
import "./ChatPanel.css";

const FALLBACK_TEXT = "I don't have information on that in the knowledge base.";

interface Message {
  role: "user" | "assistant";
  text: string;
  sources?: AskResponse["sources"];
  queryLogId?: number;
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const result = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: result.answer,
          sources: result.sources,
          queryLogId: result.query_log_id,
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

  return (
    <div className="chat-panel">
      <div className="message-list">
        {messages.length === 0 && (
          <div className="empty-state">
            Ask a question about your uploaded documents to get started.
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
    </div>
  );
}
