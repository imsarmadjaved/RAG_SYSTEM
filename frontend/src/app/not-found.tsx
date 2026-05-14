"use client";

import Link from "next/link";
import { Home, ArrowLeft, FileText } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }} />
      </div>

      <div className="relative z-10 text-center">
        <div className="animate-float mb-8">
          <div className="w-32 h-32 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto shadow-2xl">
            <FileText size={64} className="text-white" />
          </div>
        </div>

        <h1 className="text-8xl font-black text-white mb-4 animate-fade-in-up">404</h1>
        <p className="text-2xl text-blue-200 mb-2 animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
          Page not found
        </p>
        <p className="text-gray-400 mb-8 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
          The page you are looking for does not exist or has been moved.
        </p>

        <div className="flex items-center justify-center gap-4 animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
          <Link
            href="/"
            className="flex items-center gap-2 px-6 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-all border border-white/20 backdrop-blur-sm"
          >
            <Home size={18} /> Go Home
          </Link>
          <button
            onClick={() => window.history.back()}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/30"
          >
            <ArrowLeft size={18} /> Go Back
          </button>
        </div>
      </div>
    </div>
  );
}
