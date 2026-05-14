"use client";

import { useState, useRef, useEffect } from "react";
import api from "@/lib/api";
import toast from "react-hot-toast";
import {
  Send,
  Loader,
  User,
  Bot,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Zap,
  MessageSquare,
} from "lucide-react";
import Link from "next/link";

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  async function sendMessage() {
    const q = input.trim();
    if (!q) return;
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setInput("");
    setLoading(true);

    try {
      const { data } = await api.post("/chat/query", {
        query: q,
        session_id: sessionId,
      });
      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          confidence: data.confidence_level,
          sources: data.sources,
        },
      ]);
    } catch (err: any) {
      if (err.response?.status === 404)
        toast.error("Please upload your resume first");
      else toast.error("Failed to get response");
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  const confidenceStyles = (level: string) => {
    if (level === "high")
      return "bg-green-500/15 text-green-400 border-green-500/30";
    if (level === "medium")
      return "bg-yellow-500/15 text-yellow-400 border-yellow-500/30";
    return "bg-red-500/15 text-red-400 border-red-500/30";
  };

  const suggestions = [
    { text: "What skills do I have?", icon: "" },
    { text: "Where did I work?", icon: "" },
    { text: "What is my education?", icon: "" },
    { text: "Summarize my resume", icon: "" },
  ];

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-140px)] flex flex-col animate-fade-in-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Sparkles size={20} className="text-white" />
            </div>
            Chat with Resume
          </h1>
          <p className="text-gray-400 mt-1 ml-13">
            AI-powered Q&A based on your resume data
          </p>
        </div>
        {sessionId && (
          <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm text-green-400 font-medium">
              Connected
            </span>
          </div>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-6 mb-6 pr-2 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            {/* Animated orb */}
            <div className="relative mb-8">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-3xl flex items-center justify-center border border-blue-500/20 animate-float">
                <MessageSquare size={40} className="text-blue-400" />
              </div>
              <div className="absolute -top-2 -right-2 w-8 h-8 bg-purple-500/20 rounded-full animate-pulse" />
            </div>

            <h2 className="text-2xl font-bold text-white mb-2">
              Ask Anything About Your Resume
            </h2>
            <p className="text-gray-400 mb-8 max-w-md">
              I can tell you about your skills, experience, education, or
              summarize your entire resume.
            </p>

            {/* Suggestion chips */}
            <div className="grid grid-cols-2 gap-3 max-w-lg w-full">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => {
                    setInput(s.text);
                    setTimeout(sendMessage, 100);
                  }}
                  className="flex items-center gap-3 px-4 py-3.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-left transition-all hover:border-blue-500/30 hover:scale-[1.02] group"
                >
                  <span className="text-xl">{s.icon}</span>
                  <span className="text-sm text-gray-300 group-hover:text-white">
                    {s.text}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => {
          const isUser = msg.role === "user";
          return (
            <div
              key={idx}
              className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"} animate-fade-in`}
            >
              {/* Bot Avatar */}
              {!isUser && (
                <div className="w-9 h-9 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl flex items-center justify-center flex-shrink-0 mt-1 border border-blue-500/20">
                  <Bot size={18} className="text-blue-400" />
                </div>
              )}

              <div className={`max-w-[75%] ${isUser ? "order-1" : ""}`}>
                {/* Message Bubble */}
                <div
                  className={`rounded-2xl px-5 py-3.5 ${
                    isUser
                      ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-br-md shadow-lg shadow-blue-600/20"
                      : "glass border border-white/10 text-gray-200 rounded-bl-md"
                  }`}
                >
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">
                    {msg.content}
                  </p>
                </div>

                {/* Confidence + Sources */}
                {msg.confidence && (
                  <div className="flex items-center gap-2 mt-2 px-1">
                    <span
                      className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${confidenceStyles(msg.confidence)}`}
                    >
                      <Zap size={10} />
                      {msg.confidence === "high"
                        ? "High confidence"
                        : msg.confidence === "medium"
                          ? "Medium confidence"
                          : "Low confidence"}
                    </span>
                    {msg.sources?.length > 0 && (
                      <button
                        onClick={() =>
                          setExpandedSources(
                            expandedSources === idx ? null : idx,
                          )
                        }
                        className="text-xs text-gray-500 hover:text-gray-300 flex items-center gap-1 transition-colors font-medium"
                      >
                        {msg.sources.length} source
                        {msg.sources.length > 1 ? "s" : ""}
                        {expandedSources === idx ? (
                          <ChevronUp size={12} />
                        ) : (
                          <ChevronDown size={12} />
                        )}
                      </button>
                    )}
                  </div>
                )}

                {/* Source Details */}
                {expandedSources === idx && msg.sources && (
                  <div className="mt-2 space-y-1.5">
                    {msg.sources.map((s: any, i: number) => (
                      <div
                        key={i}
                        className="bg-white/5 border border-white/10 rounded-xl px-4 py-2.5"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                            {s.chunk_type}
                          </span>
                          <span className="text-[10px] text-gray-600">
                            Relevance: {(s.relevance_score * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 leading-relaxed">
                          {s.chunk_text?.substring(0, 200)}...
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* User Avatar */}
              {isUser && (
                <div className="w-9 h-9 bg-white/10 rounded-xl flex items-center justify-center flex-shrink-0 mt-1">
                  <User size={18} className="text-gray-400" />
                </div>
              )}
            </div>
          );
        })}

        {/* Typing Indicator */}
        {loading && (
          <div className="flex gap-3 animate-fade-in">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-xl flex items-center justify-center border border-blue-500/20">
              <Bot size={18} className="text-blue-400" />
            </div>
            <div className="glass border border-white/10 rounded-2xl rounded-bl-md px-5 py-4">
              <div className="flex items-center gap-1.5">
                <span
                  className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <span
                  className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <span
                  className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="flex-shrink-0 glass rounded-2xl p-2 border border-white/10 focus-within:border-blue-500/50 focus-within:shadow-lg focus-within:shadow-blue-500/10 transition-all duration-300">
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your resume..."
            disabled={loading}
            className="flex-1 px-4 py-3.5 bg-transparent outline-none text-gray-200 placeholder-gray-500 text-sm"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-5 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-30 disabled:cursor-not-allowed transition-all flex-shrink-0 shadow-lg shadow-blue-600/20 font-medium flex items-center gap-2"
          >
            {loading ? (
              <Loader className="animate-spin" size={18} />
            ) : (
              <>
                <Send size={18} />{" "}
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
