
import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2, Zap, Bot } from "lucide-react";
import MessageBubble from "./MessageBubble";
import { sendChat, sendAgentChat } from "../services/api";

const STARTER_QUESTIONS = [
  "What should I do during a flood?",
  "How do I perform CPR?",
  "What are safe evacuation procedures for earthquake?",
  "Emergency helpline numbers in India?",
];

export default function ChatBox({ useAgents, sessionId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (text) => {
    const query = (text || input).trim();
    if (!query || loading) return;

    setInput("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setLoading(true);

    try {
      const res = useAgents
        ? await sendAgentChat(query, sessionId)
        : await sendChat(query, sessionId);

      const d = res.data;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: d.answer,
          severity: d.severity,
          category: d.category,
          confidence_score: d.confidence_score,
          sources: d.sources,
          rag_used: d.rag_used,
          agent_used: d.agent_used,
          agent_explanation: d.agent_explanation,
        },
      ]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-10">
            <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
              <Bot size={32} className="text-indigo-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-200 mb-1">ResQAI ready</h2>
              <p className="text-sm text-slate-500 max-w-sm">
                Ask anything about disaster response, first aid, evacuation, or emergency procedures.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
              {STARTER_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  className="text-left text-xs text-slate-400 bg-slate-800/60 border border-slate-700 hover:border-indigo-500/50 hover:text-slate-200 px-3 py-2.5 rounded-xl transition-all duration-150"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} />
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 border border-slate-700 px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-2">
              <Loader2 size={14} className="text-indigo-400 animate-spin" />
              <span className="text-xs text-slate-400">
                {useAgents ? "Routing to specialist agent..." : "Retrieving knowledge..."}
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-950/40 border border-red-800 rounded-xl px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-800 p-4">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder="Describe your emergency situation..."
            className="flex-1 bg-slate-800 border border-slate-700 focus:border-indigo-500 text-slate-100 placeholder-slate-500 rounded-xl px-4 py-3 text-sm outline-none transition-colors"
            disabled={loading}
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-colors"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </div>
        <div className="flex items-center gap-1.5 mt-2 px-1">
          <Zap size={11} className={useAgents ? "text-purple-400" : "text-indigo-400"} />
          <span className="text-xs text-slate-600">
            {useAgents ? "Multi-agent mode — queries route to specialist AI agents" : "RAG mode — answers retrieved from knowledge base"}
          </span>
        </div>
      </div>
    </div>
  );
}
