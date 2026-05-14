"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/AuthContext";
import Link from "next/link";
import api from "@/lib/api";
import toast from "react-hot-toast";
import { Upload, FileText, CheckCircle, XCircle, Loader, Search, ArrowRight, MessageSquare, Cloud, Trash2 } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [task, setTask] = useState<any>(null);
  const [documents, setDocuments] = useState<any[]>([]);
  const [dragOver, setDragOver] = useState(false);

  const isCandidate = user?.user_type === "candidate";

  useEffect(() => { if (isCandidate) loadDocuments(); }, [isCandidate]);

  async function loadDocuments() {
    try { const { data } = await api.get("/documents/list"); setDocuments(data.documents || []); } catch {}
  }

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith(".pdf")) { toast.error("Only PDF files"); return; }
    if (file.size > 10 * 1024 * 1024) { toast.error("Max 10MB"); return; }
    setUploading(true); setTask(null);
    const fd = new FormData(); fd.append("file", file);
    try {
      const { data } = await api.post("/documents/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      toast.success("Processing started!"); poll(data.task_id);
    } catch (err: any) { toast.error(err.response?.data?.detail || "Upload failed"); setUploading(false); }
  }

  function poll(taskId: string) {
    const interval = setInterval(async () => {
      try {
        const { data } = await api.get("/documents/status/" + taskId); setTask(data);
        if (data.status === "completed") { clearInterval(interval); setUploading(false); toast.success("Ready!"); loadDocuments(); }
        else if (data.status === "failed") { clearInterval(interval); setUploading(false); toast.error("Failed"); }
      } catch { clearInterval(interval); setUploading(false); }
    }, 2000);
  }

  async function deleteDoc(id: string) {
    try { await api.delete("/documents/" + id); toast.success("Deleted"); loadDocuments(); } catch { toast.error("Delete failed"); }
  }

  if (!isCandidate) {
    return (
      <div className="animate-fade-in-up max-w-lg mx-auto text-center py-16">
        <div className="w-20 h-20 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-purple-500/20">
          <Search size={36} className="text-purple-400" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-3">Welcome, {user?.full_name}</h2>
        <p className="text-slate-400 mb-2">Recruiter Account</p>
        <p className="text-slate-500 text-sm mb-8">Search candidates with AI-powered matching</p>
        <Link href="/dashboard/recruiter/search" className="inline-flex items-center gap-2 px-6 py-3.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 font-semibold transition-all shadow-xl shadow-purple-600/20">
          <Search size={20} /> Search Candidates <ArrowRight size={18} />
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto animate-fade-in-up space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Upload Your Resume</h1>
        <p className="text-slate-400 mt-1">Upload your PDF to analyze it with AI and chat with it</p>
      </div>

      {/* Upload Zone */}
      <div onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files?.[0]; if (f) handleFile(f); }}
        className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
          dragOver ? "border-indigo-500 bg-indigo-500/10 scale-[1.02]" : "border-slate-700 hover:border-indigo-500/50 hover:bg-slate-800/50"
        }`}>
        <input ref={fileInputRef} type="file" accept=".pdf" onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} className="hidden" />
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 transition-colors ${dragOver ? "bg-indigo-500/30" : "bg-indigo-500/10"}`}>
          <Cloud size={30} className={dragOver ? "text-indigo-300" : "text-indigo-400"} />
        </div>
        <p className="text-lg font-semibold text-slate-200">Drop your PDF here</p>
        <p className="text-slate-500 text-sm mt-1">or click to browse</p>
        <p className="text-slate-600 text-xs mt-3">PDF only, up to 10MB</p>
      </div>

      {/* Progress */}
      {task && task.status === "processing" && (
        <div className="glass-card rounded-2xl p-6 animate-fade-in">
          <div className="flex items-center gap-4 mb-4">
            <Loader className="animate-spin text-indigo-400" size={24} />
            <div>
              <p className="font-semibold text-white capitalize">{task.current_stage}</p>
              <p className="text-sm text-slate-400">{task.message}</p>
            </div>
          </div>
          <div className="w-full bg-slate-700/50 rounded-full h-2.5 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2.5 rounded-full transition-all duration-700" style={{ width: task.progress + "%" }} />
          </div>
          <p className="text-right text-xs text-slate-500 mt-2">{task.progress}%</p>
        </div>
      )}

      {task && task.status === "completed" && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-5 flex items-center gap-4 animate-fade-in">
          <CheckCircle size={22} className="text-emerald-400" />
          <div className="flex-1">
            <p className="font-semibold text-emerald-400">Ready!</p>
            <p className="text-sm text-emerald-500/80">Your resume is ready to chat with</p>
          </div>
          <Link href="/dashboard/chat" className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium text-sm transition-colors">
            <MessageSquare size={16} /> Chat
          </Link>
        </div>
      )}

      {task && task.status === "failed" && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-5 flex items-center gap-4 animate-fade-in">
          <XCircle size={22} className="text-red-400" />
          <span className="text-red-400 font-medium">Processing failed. Please try again.</span>
        </div>
      )}

      {/* Documents */}
      {documents.length > 0 && (
        <div className="glass-card rounded-2xl p-6">
          <h3 className="font-semibold text-white mb-4 text-lg">Your Documents</h3>
          <div className="space-y-3">
            {documents.map((doc: any) => (
              <div key={doc._id} className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl hover:bg-slate-800 transition-colors group border border-slate-700/50">
                <div className="w-10 h-10 bg-indigo-500/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText size={20} className="text-indigo-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-slate-200 text-sm truncate">{doc.filename}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      doc.status === "completed" ? "bg-emerald-500/20 text-emerald-400" : 
                      doc.status === "failed" ? "bg-red-500/20 text-red-400" : "bg-amber-500/20 text-amber-400"
                    }`}>{doc.status}</span>
                    {doc.total_chunks > 0 && <span className="text-xs text-slate-500">{doc.total_chunks} chunks</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {doc.status === "completed" && (
                    <Link href="/dashboard/chat" className="p-2 text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-colors">
                      <MessageSquare size={18} />
                    </Link>
                  )}
                  <button onClick={() => deleteDoc(doc._id)} className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
