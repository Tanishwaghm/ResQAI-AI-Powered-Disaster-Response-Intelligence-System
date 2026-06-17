
import React, { useEffect, useState } from "react";
import { Shield, FileText, Brain, BarChart2, Loader2, RefreshCw, BookOpen } from "lucide-react";
import UploadPDF from "./UploadPDF";
import { getDocuments } from "../services/api";

const NAV_ITEMS = [
  { id: "chat", icon: Shield, label: "Emergency Chat" },
  { id: "agents", icon: Brain, label: "Agent Mode" },
  { id: "docs", icon: BookOpen, label: "Knowledge Base" },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  const [documents, setDocuments] = useState([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const fetchDocs = async () => {
    setLoadingDocs(true);
    try {
      const res = await getDocuments();
      setDocuments(res.data.documents);
      setTotalChunks(res.data.total_chunks);
    } catch {
      // silently fail
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  return (
    <aside className="w-64 shrink-0 bg-slate-900 border-r border-slate-800 flex flex-col h-full">
      {/* Logo */}
      <div className="p-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-red-600 rounded-xl flex items-center justify-center shadow-lg shadow-red-900/40">
            <Shield size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight">ResQAI</h1>
            <p className="text-xs text-slate-500">Disaster Intelligence</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="p-3 space-y-1">
        {NAV_ITEMS.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150
              ${activeTab === id
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-900/40"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"}`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>

      <div className="px-3 pt-1 pb-3">
        <div className="h-px bg-slate-800" />
      </div>

      {/* Upload section */}
      <div className="px-3 mb-2">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest px-1 mb-2">
          Upload PDF
        </p>
        <UploadPDF onUploadSuccess={fetchDocs} />
      </div>

      {/* Knowledge base stats */}
      <div className="mt-auto p-3 border-t border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
            Knowledge Base
          </p>
          <button
            onClick={fetchDocs}
            disabled={loadingDocs}
            className="text-slate-600 hover:text-slate-400 transition-colors"
          >
            {loadingDocs ? <Loader2 size={13} className="animate-spin" /> : <RefreshCw size={13} />}
          </button>
        </div>

        {documents.length === 0 ? (
          <p className="text-xs text-slate-600">No documents uploaded yet.</p>
        ) : (
          <div className="space-y-2">
            {documents.slice(0, 4).map((doc) => (
              <div key={doc.id} className="flex items-start gap-2">
                <FileText size={12} className="text-indigo-400 mt-0.5 shrink-0" />
                <div className="min-w-0">
                  <p className="text-xs text-slate-300 truncate">{doc.name}</p>
                  <p className="text-xs text-slate-600">{doc.chunk_count} chunks</p>
                </div>
              </div>
            ))}
            {documents.length > 4 && (
              <p className="text-xs text-slate-600">+{documents.length - 4} more files</p>
            )}
            <div className="flex items-center gap-1.5 pt-1">
              <BarChart2 size={11} className="text-slate-500" />
              <p className="text-xs text-slate-500">{totalChunks} total chunks indexed</p>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
