
import React, { useState, useRef } from "react";
import { Upload, FileText, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { uploadPDF, getDocuments } from "../services/api";

export default function UploadPDF({ onUploadSuccess }) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file || !file.name.endsWith(".pdf")) {
      setError("Please upload a valid PDF file.");
      return;
    }
    setError("");
    setResult(null);
    setUploading(true);
    setProgress(0);

    try {
      const res = await uploadPDF(file, setProgress);
      setResult(res.data);
      if (onUploadSuccess) onUploadSuccess();
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="p-4 space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
          ${dragging ? "border-indigo-400 bg-indigo-950/30" : "border-slate-700 hover:border-slate-500 bg-slate-800/30"}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <Upload size={28} className={`mx-auto mb-3 ${dragging ? "text-indigo-400" : "text-slate-500"}`} />
        <p className="text-sm text-slate-300 font-medium">Drop a PDF here</p>
        <p className="text-xs text-slate-500 mt-1">or click to browse — max 50 MB</p>
      </div>

      {/* Upload progress */}
      {uploading && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Loader2 size={14} className="animate-spin text-indigo-400" />
            <span>Processing PDF... {progress}%</span>
          </div>
          <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Success */}
      {result && (
        <div className="bg-emerald-950/40 border border-emerald-700 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={16} className="text-emerald-400" />
            <span className="text-sm font-medium text-emerald-300">Upload successful</span>
          </div>
          <div className="space-y-1 text-xs text-slate-400">
            <p><span className="text-slate-300">File:</span> {result.filename}</p>
            <p><span className="text-slate-300">Chunks created:</span> {result.chunks_created}</p>
            <p className="text-slate-500">{result.message}</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-950/40 border border-red-800 rounded-xl p-4 flex items-start gap-2">
          <XCircle size={16} className="text-red-400 mt-0.5 shrink-0" />
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      <p className="text-xs text-slate-600 leading-relaxed">
        Uploaded PDFs are chunked, embedded, and stored in ChromaDB.
        They will be used to answer future queries via RAG.
      </p>
    </div>
  );
}
