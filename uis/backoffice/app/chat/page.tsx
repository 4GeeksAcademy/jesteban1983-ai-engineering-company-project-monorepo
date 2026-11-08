"use client";

import { useEffect, useRef, useState, FormEvent } from "react";
import PageTracker from "@/components/PageTracker";

interface Message {
  id: string;
  sender: "user" | "assistant" | "system";
  text: string;
  timestamp: string;
  trace?: any;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "system",
      text: "Bienvenido al asistente agéntico de operaciones en tiempo real de TrackFlow. Puedes consultar inventario, incidencias, transportistas y políticas de entrega.",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [sessionId] = useState(() => "session_" + Math.random().toString(36).substring(2, 9));
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Intentar conexión WebSocket
  useEffect(() => {
    let ws: WebSocket | null = null;
    try {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = window.location.hostname;
      // Conectar directamente al puerto de API (8000/8001) o vía ws
      const wsUrl = `${protocol}//${host}:8000/ws/chat/${sessionId}`;
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "chat_chunk") {
            setMessages((prev) => {
              const last = prev[prev.length - 1];
              if (last && last.sender === "assistant" && last.id === data.message_id) {
                return [
                  ...prev.slice(0, -1),
                  { ...last, text: last.text + data.payload.chunk },
                ];
              } else {
                return [
                  ...prev,
                  {
                    id: data.message_id,
                    sender: "assistant",
                    text: data.payload.chunk,
                    timestamp: new Date().toLocaleTimeString(),
                  },
                ];
              }
            });
          } else if (data.type === "chat_complete") {
            setLoading(false);
          } else if (data.type === "error") {
            setMessages((prev) => [
              ...prev,
              {
                id: "err_" + Date.now(),
                sender: "system",
                text: "Aviso: " + (data.payload?.message || "Error en streaming"),
                timestamp: new Date().toLocaleTimeString(),
              },
            ]);
            setLoading(false);
          }
        } catch {
          // Si no es JSON, texto plano
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
      };

      ws.onerror = () => {
        setWsConnected(false);
      };

      wsRef.current = ws;
    } catch {
      setWsConnected(false);
    }

    return () => {
      if (ws) ws.close();
    };
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userText = input.trim();
    const userMsg: Message = {
      id: "user_" + Date.now(),
      sender: "user",
      text: userText,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    // Si WebSocket está conectado, enviar por WS
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "chat_message",
          payload: { message: userText },
        })
      );
      return;
    }

    // Fallback: usar endpoint HTTP del Agente LangGraph o SafeChat
    try {
      const res = await fetch("/agent/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userText }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            id: "agent_" + Date.now(),
            sender: "assistant",
            text: data.answer || "No se obtuvo respuesta.",
            timestamp: new Date().toLocaleTimeString(),
            trace: data.trace,
          },
        ]);
      } else {
        // Fallback a SafeChat
        const fallbackRes = await fetch("/api/ai-security/safe-chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userText, session_id: sessionId }),
        });
        if (fallbackRes.ok) {
          const safeData = await fallbackRes.json();
          setMessages((prev) => [
            ...prev,
            {
              id: "safe_" + Date.now(),
              sender: "assistant",
              text: safeData.response || safeData.message || "Respuesta procesada con guardrails.",
              timestamp: new Date().toLocaleTimeString(),
            },
          ]);
        } else {
          throw new Error("No se pudo comunicar con el agente.");
        }
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: "err_" + Date.now(),
          sender: "system",
          text: `Error de conexión: ${err.message || "No se pudo obtener respuesta del backend"}`,
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuestion = (q: string) => {
    setInput(q);
  };

  return (
    <>
      <PageTracker page="/chat" />
      <main className="mx-auto flex h-[calc(100vh-5rem)] max-w-5xl flex-col px-4 py-6 md:px-8">
        {/* Cabecera */}
        <div className="flex items-center justify-between border-b border-indigo-100 bg-white/80 p-4 backdrop-blur rounded-t-2xl shadow-sm">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl">🤖</span>
              <h1 className="text-lg font-bold text-slate-900">Asistente Operativo TrackFlow</h1>
              <span
                className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  wsConnected
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-blue-100 text-blue-800"
                }`}
              >
                <span
                  className={`mr-1.5 h-2 w-2 rounded-full ${
                    wsConnected ? "bg-emerald-500 animate-pulse" : "bg-blue-500"
                  }`}
                />
                {wsConnected ? "WebSocket Streaming" : "HTTP Agent REST"}
              </span>
            </div>
            <p className="mt-0.5 text-xs text-slate-500">
              Conexión directa con agentes autónomos, RAG corporativo y memoria de sesión.
            </p>
          </div>
          <div className="text-right text-xs text-slate-400">
            Sesión: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">{sessionId}</code>
          </div>
        </div>

        {/* Zona de Mensajes */}
        <div className="flex-1 overflow-y-auto bg-slate-50/50 p-4 space-y-4 border-x border-indigo-50">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex flex-col ${
                m.sender === "user"
                  ? "items-end"
                  : m.sender === "system"
                  ? "items-center"
                  : "items-start"
              }`}
            >
              {m.sender === "system" ? (
                <div className="max-w-md rounded-xl bg-slate-200/70 px-4 py-2 text-center text-xs text-slate-600">
                  {m.text}
                </div>
              ) : (
                <div
                  className={`max-w-2xl rounded-2xl px-5 py-3 shadow-sm ${
                    m.sender === "user"
                      ? "bg-indigo-600 text-white rounded-br-none"
                      : "bg-white text-slate-800 border border-slate-200/80 rounded-bl-none"
                  }`}
                >
                  <div className="flex items-center justify-between gap-4 mb-1">
                    <span className="text-[10px] font-semibold uppercase tracking-wider opacity-75">
                      {m.sender === "user" ? "Tú" : "TrackFlow Agent"}
                    </span>
                    <span className="text-[10px] opacity-60">{m.timestamp}</span>
                  </div>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{m.text}</p>

                  {m.trace && m.trace.nodes && (
                    <details className="mt-3 border-t border-slate-100 pt-2 text-[11px] text-slate-500">
                      <summary className="cursor-pointer font-medium text-indigo-600 hover:text-indigo-800">
                        Ver traza de ejecución LangGraph ({m.trace.nodes.length} nodos)
                      </summary>
                      <div className="mt-2 space-y-1 bg-slate-50 p-2 rounded">
                        {m.trace.nodes.map((node: any, idx: number) => (
                          <div key={idx} className="flex items-center gap-2">
                            <span className="font-mono text-indigo-500">➔ {node.node}</span>
                            <span className="text-slate-400">({node.timestamp})</span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-slate-500 text-sm italic py-2">
              <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-indigo-500" />
              <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-indigo-500 [animation-delay:0.2s]" />
              <span className="inline-block h-2 w-2 animate-bounce rounded-full bg-indigo-500 [animation-delay:0.4s]" />
              El agente está procesando tu consulta con herramientas y RAG...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Sugerencias Rápidas */}
        <div className="border-t border-x border-indigo-50 bg-white px-4 py-2">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400">Consultas rápidas:</span>
            <button
              onClick={() => handleQuickQuestion("¿Cuál es el stock disponible en el almacén de Zaragoza?")}
              className="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 transition"
            >
              📦 Stock Zaragoza
            </button>
            <button
              onClick={() => handleQuickQuestion("¿Cuál es el SLA y política de devoluciones para pedidos frágiles?")}
              className="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 transition"
            >
              📋 SLA & Devoluciones
            </button>
            <button
              onClick={() => handleQuickQuestion("¿Cuáles son los proveedores y tarifas disponibles para envíos a Madrid?")}
              className="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200 transition"
            >
              🚚 Tarifas Transportistas
            </button>
          </div>
        </div>

        {/* Input Formulario */}
        <form
          onSubmit={handleSend}
          className="flex gap-2 rounded-b-2xl border border-t-0 border-indigo-100 bg-white p-3 shadow-sm"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Pregunta sobre stock, transportistas, incidencias o políticas..."
            disabled={loading}
            className="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm text-slate-900 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-700 disabled:opacity-50 transition"
          >
            Enviar
          </button>
        </form>
      </main>
    </>
  );
}

