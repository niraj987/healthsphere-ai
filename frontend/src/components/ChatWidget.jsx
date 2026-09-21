import { useEffect, useRef, useState } from "react";
import { AlertTriangle, MessageCircle, Send, X } from "lucide-react";
import gsap from "gsap";
import { sendChatMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function ChatWidget() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I'm the HealthSphere Assistant. Ask me how to use the app, or general health questions. " +
        "If you describe symptoms or need a clinician, I'll connect you with a human right away.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const panelRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (open && panelRef.current) {
      gsap.fromTo(
        panelRef.current,
        { opacity: 0, y: 24, scale: 0.96 },
        { opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "power3.out" }
      );
    }
  }, [open]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, open]);

  const handleSend = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending || !user) return;

    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setSending(true);

    try {
      const res = await sendChatMessage({ user_id: user.id, session_id: sessionId, message: text });
      setSessionId(res.session_id);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.reply, escalated: res.escalated, ticketId: res.ticket_id },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "I'm having trouble reaching the assistant service right now. Please try again shortly, or use the escalation queue if this is urgent.",
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {open && (
        <div
          ref={panelRef}
          className="mb-4 flex h-[26rem] w-80 flex-col overflow-hidden rounded-2xl border border-ink-100 bg-white shadow-soft sm:w-96"
        >
          <div className="flex items-center justify-between bg-brand-600 px-4 py-3 text-white">
            <div>
              <p className="text-sm font-semibold">HealthSphere Assistant</p>
              <p className="text-xs text-brand-100">RAG-powered · escalates to a human when needed</p>
            </div>
            <button onClick={() => setOpen(false)} aria-label="Close chat">
              <X size={18} />
            </button>
          </div>

          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
                    m.role === "user" ? "bg-brand-600 text-white" : "bg-ink-50 text-ink-800"
                  }`}
                >
                  {m.content}
                  {m.escalated && (
                    <div className="mt-2 flex items-center gap-1.5 rounded-lg bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-700">
                      <AlertTriangle size={12} /> Routed to our team {m.ticketId ? `· Ticket #${m.ticketId}` : ""}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {sending && <p className="text-xs text-ink-400">Assistant is typing…</p>}
          </div>

          <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-ink-100 px-3 py-3">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={user ? "Ask a question…" : "Sign in to chat"}
              disabled={!user}
              className="input flex-1 py-2 text-sm"
            />
            <button type="submit" disabled={!user || sending} className="btn-primary !px-3 !py-2">
              <Send size={16} />
            </button>
          </form>
        </div>
      )}

      <button
        onClick={() => setOpen((o) => !o)}
        className="flex h-14 w-14 items-center justify-center rounded-full bg-accent-500 text-white shadow-soft transition hover:bg-accent-600"
        aria-label="Open chat"
      >
        {open ? <X size={22} /> : <MessageCircle size={22} />}
      </button>
    </div>
  );
}
