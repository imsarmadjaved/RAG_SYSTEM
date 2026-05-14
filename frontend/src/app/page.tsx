"use client";

import Link from "next/link";
import { FileText, MessageSquare, Search, ArrowRight, Zap, Sparkles, Upload } from "lucide-react";
import { useState, useEffect } from "react";

export default function HomePage() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouse);
    return () => window.removeEventListener("mousemove", handleMouse);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-1/4 -left-20 w-96 h-96 bg-blue-600/20 rounded-full blur-8xl" />
          <div className="absolute top-1/3 right-0 w-80 h-80 bg-purple-600/20 rounded-full blur-8xl" />
          <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-cyan-600/10 rounded-full blur-8xl" />
        </div>
        {/* Grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />
      </div>

      {/* Mouse follower */}
      <div
        className="fixed w-64 h-64 rounded-full pointer-events-none transition-transform duration-1000 ease-out blur-3xl opacity-20 bg-blue-500"
        style={{
          transform: `translate(${mousePos.x - 128}px, ${mousePos.y - 128}px)`,
        }}
      />

      {/* Navbar */}
      <nav className="relative z-10 border-b border-white/10 glass-dark">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 text-xl font-bold">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
              <FileText size={18} className="text-white" />
            </div>
            RAG Resume
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/auth/login" className="px-4 py-2 text-gray-300 hover:text-white transition-colors text-sm font-medium">
              Sign In
            </Link>
            <Link href="/auth/signup" className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 font-medium text-sm transition-all shadow-lg shadow-blue-600/20 animate-glow">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 pt-24 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full text-blue-300 text-sm mb-8 animate-fade-in-up">
          <Sparkles size={16} className="animate-pulse" /> AI-Powered Resume Platform
        </div>

        <h1 className="text-6xl md:text-7xl font-black mb-6 leading-tight animate-fade-in-up" style={{ animationDelay: "0.1s" }}>
          Your Resume,
          <br />
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-gradient">
            Supercharged by AI
          </span>
        </h1>

        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          Upload your resume and chat with it intelligently. Recruiters can search across candidates with AI-powered matching and scoring.
        </p>

        <div className="flex items-center justify-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
          <Link
            href="/auth/signup"
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 font-semibold text-lg transition-all shadow-2xl shadow-blue-600/30 inline-flex items-center gap-2 animate-glow"
          >
            Get Started Free <ArrowRight size={20} />
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 pb-24">
        <div className="grid md:grid-cols-3 gap-6 stagger-children">
          <div className="glass rounded-2xl p-8 border border-white/10 hover:border-blue-500/30 transition-all hover:scale-[1.02]">
            <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-5">
              <Upload size={24} className="text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Smart Resume Upload</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Upload your PDF and our AI automatically extracts skills, experience, and education. Track real-time progress.
            </p>
          </div>

          <div className="glass rounded-2xl p-8 border border-white/10 hover:border-purple-500/30 transition-all hover:scale-[1.02]">
            <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mb-5">
              <MessageSquare size={24} className="text-purple-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Chat with Your Resume</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Ask questions and get accurate answers with source citations. Anti-hallucination AI for truthful responses.
            </p>
          </div>

          <div className="glass rounded-2xl p-8 border border-white/10 hover:border-cyan-500/30 transition-all hover:scale-[1.02]">
            <div className="w-12 h-12 bg-cyan-500/20 rounded-xl flex items-center justify-center mb-5">
              <Search size={24} className="text-cyan-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Recruiter Search</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Find the perfect candidate with AI-powered search. Filter by skills and experience with smart scoring.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-8 text-center text-sm text-gray-500">
        Built by Muhammad Sarmad Javed | RAG Resume System.
      </footer>
    </div>
  );
}
