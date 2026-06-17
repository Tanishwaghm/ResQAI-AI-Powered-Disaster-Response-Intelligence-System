
import React from "react";
import { AlertTriangle, AlertCircle, Info, CheckCircle, Activity, Shield, Map, Phone, Heart } from "lucide-react";

const SEVERITY_CONFIG = {
  CRITICAL: { bg: "bg-red-950/60", border: "border-red-500", text: "text-red-400", icon: AlertTriangle, label: "CRITICAL" },
  HIGH:     { bg: "bg-orange-950/60", border: "border-orange-500", text: "text-orange-400", icon: AlertCircle, label: "HIGH" },
  MEDIUM:   { bg: "bg-yellow-950/60", border: "border-yellow-600", text: "text-yellow-400", icon: Info, label: "MEDIUM" },
  LOW:      { bg: "bg-green-950/60", border: "border-green-600", text: "text-green-400", icon: CheckCircle, label: "LOW" },
};

const AGENT_ICONS = {
  medical:       { Icon: Heart,    color: "text-red-400",    label: "Medical Agent" },
  rescue:        { Icon: Shield,   color: "text-orange-400", label: "Rescue Agent" },
  navigation:    { Icon: Map,      color: "text-blue-400",   label: "Navigation Agent" },
  communication: { Icon: Phone,    color: "text-green-400",  label: "Communication Agent" },
};

const ConfidenceMeter = ({ score }) => {
  const color = score >= 75 ? "bg-emerald-500" : score >= 50 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2 mt-2">
      <span className="text-xs text-slate-500 w-20 shrink-0">Confidence</span>
      <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-700 ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-xs text-slate-400 w-10 text-right">{score}%</span>
    </div>
  );
};

export default function MessageBubble({ msg }) {
  const isUser = msg.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[78%] bg-indigo-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm text-sm leading-relaxed shadow-lg">
          {msg.content}
        </div>
      </div>
    );
  }

  const sev = SEVERITY_CONFIG[msg.severity] || SEVERITY_CONFIG.LOW;
  const SevIcon = sev.icon;
  const agentInfo = msg.agent_used ? AGENT_ICONS[msg.agent_used] : null;

  return (
    <div className="flex justify-start">
      <div className="max-w-[88%] space-y-2">
        {/* Agent badge */}
        {agentInfo && (
          <div className={`flex items-center gap-1.5 text-xs ${agentInfo.color} font-medium`}>
            <agentInfo.Icon size={13} />
            <span>{agentInfo.label}</span>
            {msg.agent_explanation && (
              <span className="text-slate-500 font-normal">— {msg.agent_explanation}</span>
            )}
          </div>
        )}

        {/* Main bubble */}
        <div className={`${sev.bg} border ${sev.border} px-4 py-3 rounded-2xl rounded-tl-sm shadow-lg`}>
          <p className="text-slate-100 text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
        </div>

        {/* Meta row */}
        <div className="flex flex-wrap items-center gap-2 px-1">
          {/* Severity */}
          <span className={`flex items-center gap-1 text-xs font-bold ${sev.text}`}>
            <SevIcon size={11} />
            {sev.label}
          </span>

          {/* Category */}
          {msg.category && (
            <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full">
              {msg.category}
            </span>
          )}

          {/* RAG indicator */}
          {msg.rag_used !== undefined && (
            <span className={`flex items-center gap-1 text-xs ${msg.rag_used ? "text-emerald-400" : "text-slate-500"}`}>
              <Activity size={11} />
              {msg.rag_used ? "RAG" : "LLM only"}
            </span>
          )}
        </div>

        {/* Confidence meter */}
        {msg.confidence_score !== undefined && (
          <div className="px-1">
            <ConfidenceMeter score={msg.confidence_score} />
          </div>
        )}

        {/* Sources */}
        {msg.sources && msg.sources.length > 0 && (
          <details className="px-1">
            <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-300 transition-colors">
              {msg.sources.length} source{msg.sources.length > 1 ? "s" : ""}
            </summary>
            <div className="mt-2 space-y-2">
              {msg.sources.map((src, i) => (
                <div key={i} className="bg-slate-800/60 border border-slate-700 rounded-lg p-3">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-xs font-medium text-indigo-400">{src.document_name}</span>
                    {src.page && <span className="text-xs text-slate-500">p.{src.page}</span>}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{src.chunk_preview}</p>
                  <div className="mt-1.5 flex items-center gap-1">
                    <div className="flex-1 h-1 bg-slate-700 rounded-full">
                      <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${src.relevance_score}%` }} />
                    </div>
                    <span className="text-xs text-slate-500">{src.relevance_score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
