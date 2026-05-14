"use client";

import { useAuth } from "@/lib/AuthContext";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { LogOut, FileText, MessageSquare, Search, Menu, X, Home, Upload, LayoutDashboard, ChevronRight, Sparkles } from "lucide-react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.push("/auth/login");
  }, [user, loading, router]);

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-12 h-12 mx-auto mb-4">
            <div className="absolute inset-0 border-3 border-indigo-500/20 rounded-full" />
            <div className="absolute inset-0 border-3 border-transparent border-t-indigo-500 rounded-full animate-spin" />
          </div>
          <p className="text-slate-400 text-sm">Loading...</p>
        </div>
      </div>
    );
  }

  const isCandidate = user.user_type === "candidate";

  const navItems = isCandidate
    ? [
        { href: "/dashboard", label: "Upload Resume", icon: Upload },
        { href: "/dashboard/chat", label: "Chat with Resume", icon: MessageSquare },
      ]
    : [
        { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
        { href: "/dashboard/recruiter/search", label: "Search Candidates", icon: Search },
      ];

  const segments = pathname.split("/").filter(Boolean);

  return (
    <div className="min-h-screen bg-slate-950 relative overflow-hidden">
      {/* ANIMATED BACKGROUND ORBS - Fixed */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-1/4 -left-32 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] orb-1" />
        <div className="absolute top-1/2 -right-32 w-[400px] h-[400px] bg-purple-600/8 rounded-full blur-[100px] orb-2" />
        <div className="absolute -bottom-20 left-1/3 w-[450px] h-[450px] bg-blue-600/8 rounded-full blur-[110px] orb-3" />
        <div className="absolute top-10 right-1/4 w-[300px] h-[300px] bg-cyan-600/6 rounded-full blur-[80px] orb-4" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.015)_1px,transparent_1px)] bg-[size:64px_64px]" />
      </div>

      {/* Mobile header - Fixed */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-30 flex items-center justify-between px-4 py-3 bg-slate-900/95 backdrop-blur-xl border-b border-slate-800">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-white">
          <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Sparkles size={14} className="text-white" />
          </div>
          RAG
        </Link>
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 text-slate-400 hover:text-white rounded-lg">
          {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile spacer */}
      <div className="lg:hidden h-[57px]" />

      <div className="flex relative z-10">
        {/* Sidebar - Fixed on desktop, slide on mobile */}
        <aside className={`fixed lg:fixed top-0 lg:top-0 left-0 z-40 w-64 h-full lg:h-screen border-r border-slate-800 bg-slate-900/95 backdrop-blur-xl transform transition-transform duration-300 overflow-y-auto ${sidebarOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 flex flex-col`}>
          <div className="p-6 border-b border-slate-800 flex-shrink-0">
            <Link href="/dashboard" className="flex items-center gap-2.5 text-xl font-bold text-white">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <Sparkles size={16} className="text-white" />
              </div>
              RAG Resume
            </Link>
            <span className="inline-block mt-2 px-2.5 py-1 bg-slate-800 text-slate-300 rounded-lg text-xs font-medium capitalize border border-slate-700">
              {user.user_type}
            </span>
          </div>

          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all text-sm font-medium ${
                    isActive
                      ? "bg-gradient-to-r from-indigo-600/20 to-purple-600/20 text-white border border-indigo-500/20"
                      : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                  }`}
                >
                  <item.icon size={20} className={isActive ? "text-indigo-400" : ""} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t border-slate-800 flex-shrink-0">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-sm shadow-lg">
                {user.full_name?.[0]?.toUpperCase() || "U"}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white truncate">{user.full_name}</p>
                <p className="text-xs text-slate-400 truncate">{user.email}</p>
              </div>
            </div>
            <button onClick={logout}
              className="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm text-red-400 rounded-xl hover:bg-red-500/10 transition-colors font-medium">
              <LogOut size={16} /> Sign Out
            </button>
          </div>
        </aside>

        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div className="fixed inset-0 bg-black/60 z-30 lg:hidden backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        )}

        {/* Main content - with left margin on desktop */}
        <main className="flex-1 min-h-screen relative z-10 lg:ml-64">
          {segments.length > 1 && (
            <div className="px-6 lg:px-8 pt-6">
              <div className="flex items-center gap-1.5 text-sm text-slate-500">
                <Link href="/dashboard" className="hover:text-slate-300"><Home size={15} /></Link>
                {segments.map((seg, i) => (
                  <span key={seg} className="flex items-center gap-1.5">
                    <ChevronRight size={14} />
                    {i === segments.length - 1 ? (
                      <span className="text-slate-300 font-medium capitalize">{seg.replace(/-/g, " ")}</span>
                    ) : (
                      <Link href={"/" + segments.slice(0, i + 1).join("/")} className="hover:text-slate-300 capitalize">{seg.replace(/-/g, " ")}</Link>
                    )}
                  </span>
                ))}
              </div>
            </div>
          )}
          <div className="p-6 lg:p-8">{children}</div>
        </main>
      </div>
    </div>
  );
}
