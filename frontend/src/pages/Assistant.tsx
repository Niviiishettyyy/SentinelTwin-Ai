import { useState } from "react";
import { askAssistant, AssistantAnswer } from "../api/client";

interface Msg {
  role: "user" | "assistant";
  text: string;
  confidence?: number;
  sources?: string[];
}

const SUGGESTIONS = [
  "What is the riskiest node right now?",
  "Is there an active attack path?",
  "What threats have been detected?",
];

export default function Assistant() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "assistant", text: "Ask me about current risk, flagged threats, or attack paths in the twin." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async (question: string) => {
    if (!question.trim()) return;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const res: AssistantAnswer = await askAssistant(question);
      setMessages((m) => [...m, { role: "assistant", text: res.answer, confidence: res.confidence, sources: res.sources }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", text: "Could not reach the assistant. Is the backend running and are you logged in?" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-xl font-semibold">Assistant</h1>
        <p className="text-sm text-muted mt-1">Explainable chat interface backed by evidence from the twin.</p>
      </header>

      <div className="card p-5 flex flex-col h-[560px]">
        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[75%] rounded-lg px-4 py-3 text-sm ${
                m.role === "user" ? "bg-accent/15 border border-accent/30" : "bg-raised border border-border"
              }`}>
                <p>{m.text}</p>
                {m.confidence !== undefined && (
                  <div className="flex items-center gap-2 mt-2">
                    <span className="pill pill-muted">confidence {Math.round(m.confidence * 100)}%</span>
                    {m.sources?.map((s) => (
                      <span key={s} className="pill pill-muted font-mono">{s}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && <p className="text-xs text-muted">Assistant is thinking...</p>}
        </div>

        <div className="flex gap-2 flex-wrap mt-4 mb-2">
          {SUGGESTIONS.map((s) => (
            <button key={s} onClick={() => send(s)} className="pill pill-muted hover:border-accent/40 transition">
              {s}
            </button>
          ))}
        </div>

        <div className="flex gap-2 mt-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send(input)}
            placeholder="Ask about risk, threats, or attack paths..."
            className="flex-1 bg-raised border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-accent/50"
          />
          <button className="btn-primary" onClick={() => send(input)}>Send</button>
        </div>
      </div>
    </div>
  );
}
