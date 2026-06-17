
import React, { useState, useEffect } from "react";
import { Wifi, WifiOff, Shield, Brain, BookOpen, ChevronRight } from "lucide-react";
import ChatBox from "../components/ChatBox";
import { healthCheck } from "../services/api";

const TABS = {
  chat: { label: "Emergency Chat", icon: Shield, desc: "RAG-powered emergency guidance from your knowledge base" },
  agents: { label: "Agent Mode", icon: Brain, desc: "Multi-agent routing — queries go to specialist AI agents" },
  docs: { label: "Knowledge Base", icon: BookOpen, desc: "View indexed documents and knowledge base status" },
};

export default function Home({ activeTab }) {
  const [backendOk, setBackendOk] = useState(null);
  const [sessionId] = useState(() => `session_${Date.now()}`);

  useEffect(() => {
    healthCheck()
      .then(() => setBackendOk(true))
      .catch(() => setBackendOk(false));
  }, []);

  const tab = TABS[activeTab] || TABS.chat;
  const TabIcon = tab.icon;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between bg-slate-900/50 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <TabIcon size={18} className="text-indigo-400" />
          <div>
            <h2 className="text-sm font-semibold text-slate-100">{tab.label}</h2>
            <p className="text-xs text-slate-500">{tab.desc}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {backendOk === null && (
            <span className="text-xs text-slate-500">Connecting...</span>
          )}
          {backendOk === true && (
            <span className="flex items-center gap-1.5 text-xs text-emerald-400">
              <Wifi size={12} /> Backend online
            </span>
          )}
          {backendOk === false && (
            <span className="flex items-center gap-1.5 text-xs text-red-400">
              <WifiOff size={12} /> Backend offline
            </span>
          )}
        </div>
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-hidden">
        {(activeTab === "chat" || activeTab === "agents") && (
          <ChatBox useAgents={activeTab === "agents"} sessionId={sessionId} />
        )}

        {activeTab === "docs" && (
          <div className="p-6 space-y-4">
            <div className="bg-slate-800/40 border border-slate-700 rounded-2xl p-5">
              <h3 className="text-sm font-semibold text-slate-200 mb-1">About the Knowledge Base</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Upload emergency response PDFs in the sidebar. They will be parsed, chunked into 1000-character
                segments with 200-character overlap, embedded using <code className="text-indigo-400">all-MiniLM-L6-v2</code>,
                and stored in ChromaDB for semantic retrieval.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                { title: "Flood Response Manuals", hint: "NDMA flood management guidelines" },
                { title: "Earthquake Safety Guides", hint: "Drop, cover, hold procedures" },
                { title: "Medical First Aid PDFs", hint: "Red Cross, WHO first aid manuals" },
                { title: "Fire Safety Procedures", hint: "NFPA evacuation standards" },
              ].map((item, i) => (
                <div key={i} className="bg-slate-800/30 border border-slate-700/60 rounded-xl p-4">
                  <p className="text-sm font-medium text-slate-300 mb-1">{item.title}</p>
                  <p className="text-xs text-slate-500 flex items-center gap-1">
                    <ChevronRight size={11} className="text-indigo-400" />
                    {item.hint}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
