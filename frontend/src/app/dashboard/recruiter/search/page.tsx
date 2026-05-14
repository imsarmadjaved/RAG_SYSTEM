"use client";

import { useState } from "react";
import api from "@/lib/api";
import toast from "react-hot-toast";
import { Search, Loader, Star, Mail, Briefcase, GraduationCap, X, RotateCcw, Filter } from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import Link from "next/link";

export default function RecruiterSearchPage() {
  const { user } = useAuth();
  const [query, setQuery] = useState("");
  const [skills, setSkills] = useState("");
  const [minExp, setMinExp] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch() {
    if (!query.trim() && !skills.trim()) { toast.error("Enter a query or skills"); return; }
    setLoading(true);
    setSearched(false);
    setError("");
    setResults([]);
    setTotal(0);
    
    try {
      const payload: any = { query: query || skills };
      if (skills.trim()) payload.required_skills = skills.split(",").map((s: string) => s.trim()).filter(Boolean);
      if (minExp) payload.min_experience = parseInt(minExp);
      
      const { data } = await api.post("/recruiter/search", payload);
      setResults(data.results || []);
      setTotal(data.total_results || 0);
      setSearched(true);
      
      if (data.total_results === 0) {
        toast("No candidates found. Try broadening your search.", { icon: "🔍" });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Search failed. Please try again.");
      toast.error("Search failed");
      setSearched(true);
    } finally {
      setLoading(false);
    }
  }

  function resetFilters() {
    setQuery(""); setSkills(""); setMinExp(""); setResults([]); setTotal(0); setSearched(false); setError("");
  }

  function getScoreGradient(score: number) {
    if (score >= 70) return "from-emerald-500/20 to-green-500/20 border-emerald-500/30 text-emerald-400";
    if (score >= 40) return "from-amber-500/20 to-yellow-500/20 border-amber-500/30 text-amber-400";
    return "from-red-500/20 to-orange-500/20 border-red-500/30 text-red-400";
  }

  return (
    <div className="max-w-5xl mx-auto animate-fade-in-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Search size={20} className="text-white" />
            </div>
            Search Candidates
          </h1>
          <p className="text-slate-400 mt-1 ml-13">Find the best candidates using AI-powered matching</p>
        </div>
        {searched && !loading && (
          <button onClick={resetFilters} className="flex items-center gap-2 px-4 py-2 text-sm text-slate-400 hover:text-white bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-all border border-slate-700/50">
            <RotateCcw size={16} /> Reset
          </button>
        )}
      </div>

      {/* Search Form */}
      <div className="glass-card rounded-2xl p-6 mb-6">
        <div className="grid md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="label-light block mb-1.5">
              <Filter size={14} className="inline mr-1.5" />Search Query
            </label>
            <input value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="e.g. Senior Python developer with AWS experience"
              className="input-dark w-full px-4 py-3 rounded-xl outline-none" />
          </div>
          <div>
            <label className="label-light block mb-1.5">
              <Briefcase size={14} className="inline mr-1.5" />Min Experience
            </label>
            <input type="number" value={minExp} onChange={(e) => setMinExp(e.target.value)}
              placeholder="Years (e.g. 3)"
              className="input-dark w-full px-4 py-3 rounded-xl outline-none" />
          </div>
        </div>
        <div className="mt-4">
          <label className="label-light block mb-1.5">
            <Star size={14} className="inline mr-1.5" />Required Skills
          </label>
          <input value={skills} onChange={(e) => setSkills(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            placeholder="e.g. Python, React, AWS, Docker"
            className="input-dark w-full px-4 py-3 rounded-xl outline-none" />
          <p className="text-xs text-slate-600 mt-1.5">Separate skills with commas</p>
        </div>
        <button onClick={handleSearch} disabled={loading}
          className="mt-5 w-full py-3.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 font-semibold transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-600/20">
          {loading ? (
            <>
              <Loader className="animate-spin" size={22} />
              Searching candidates...
            </>
          ) : (
            <>
              <Search size={22} />
              Search Candidates
            </>
          )}
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-16 animate-fade-in">
          <div className="relative w-16 h-16 mx-auto mb-6">
            <div className="absolute inset-0 border-3 border-purple-500/20 rounded-full" />
            <div className="absolute inset-0 border-3 border-transparent border-t-purple-500 rounded-full animate-spin" />
          </div>
          <p className="text-slate-400 text-lg font-medium">Searching candidates...</p>
          <p className="text-slate-600 text-sm mt-1">Scanning resumes for the best matches</p>
        </div>
      )}

      {/* Results */}
      {!loading && searched && total > 0 && (
        <div className="mb-4 flex items-center gap-2">
          <span className="text-sm font-medium text-slate-300">
            {total} candidate{total !== 1 ? "s" : ""} found
          </span>
          <span className="text-xs text-slate-600">Showing top results</span>
        </div>
      )}

      {!loading && searched && results.length > 0 && (
        <div className="space-y-4 stagger-children">
          {results.map((c, idx) => {
            const scoreGradient = getScoreGradient(c.match_score);
            return (
              <div key={idx} className="glass-card rounded-2xl p-6 hover:border-slate-600/50 transition-all animate-fade-in group">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-purple-500/20">
                      {c.email?.[0]?.toUpperCase() || "?"}
                    </div>
                    <div>
                      <p className="font-semibold text-white text-lg flex items-center gap-2">
                        {c.email}
                        <Mail size={14} className="text-slate-500" />
                      </p>
                      <p className="text-sm text-slate-400 mt-0.5">{c.education || "Education not specified"}</p>
                    </div>
                  </div>
                  <div className={`flex items-center gap-1.5 px-4 py-2.5 rounded-full bg-gradient-to-r border ${scoreGradient} shadow-lg`}>
                    <Star size={18} className="fill-yellow-500 text-yellow-500" />
                    <span className="font-bold text-lg">{c.match_score}%</span>
                  </div>
                </div>

                <p className="text-sm text-slate-300 mb-4 leading-relaxed">{c.summary}</p>

                <div className="flex flex-wrap gap-2 mb-4">
                  {c.skills_matched?.map((s: string) => (
                    <span key={s} className="px-3 py-1.5 bg-emerald-500/10 text-emerald-400 text-xs rounded-full border border-emerald-500/20 font-medium">
                      ✓ {s}
                    </span>
                  ))}
                  {c.skills_missing?.map((s: string) => (
                    <span key={s} className="px-3 py-1.5 bg-red-500/10 text-red-400 text-xs rounded-full border border-red-500/20 flex items-center gap-1">
                      <X size={10} /> {s}
                    </span>
                  ))}
                </div>

                <div className="flex flex-wrap gap-6 text-sm text-slate-500 pt-4 border-t border-slate-700/50">
                  <span className="flex items-center gap-1.5">
                    <Briefcase size={15} className="text-slate-600" /> 
                    <span className="text-slate-300 font-medium">{c.experience_years}</span> years experience
                  </span>
                  <span className="flex items-center gap-1.5">
                    <GraduationCap size={15} className="text-slate-600" /> 
                    <span className="text-slate-300">{c.education || "Not specified"}</span>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Mail size={15} className="text-slate-600" /> 
                    <span className="text-slate-300">{c.email}</span>
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State - Only show after search is complete */}
      {!loading && searched && results.length === 0 && !error && (
        <div className="text-center py-20 animate-fade-in">
          <div className="w-20 h-20 bg-slate-800/50 rounded-3xl flex items-center justify-center mx-auto mb-6 border border-slate-700/50">
            <Search size={36} className="text-slate-600" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">No candidates found</h3>
          <p className="text-slate-500 mb-6">Try broadening your search or adjusting the filters</p>
          <button onClick={resetFilters} className="px-5 py-2.5 bg-slate-800/50 hover:bg-slate-800 text-slate-300 rounded-xl border border-slate-700/50 transition-all font-medium text-sm">
            <RotateCcw size={14} className="inline mr-2" />Reset Filters
          </button>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="text-center py-20 animate-fade-in">
          <div className="w-20 h-20 bg-red-500/10 rounded-3xl flex items-center justify-center mx-auto mb-6 border border-red-500/20">
            <X size={36} className="text-red-400" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">Search Failed</h3>
          <p className="text-slate-500 mb-6">{error}</p>
          <button onClick={handleSearch} className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-all font-medium text-sm">
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}
