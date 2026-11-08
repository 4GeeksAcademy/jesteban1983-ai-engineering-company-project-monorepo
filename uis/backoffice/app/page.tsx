import Link from "next/link";
import { buildTrackflowSmokeReport } from "@trackflow/logic";
import { SmokeChecksPanel } from "../components/SmokeChecksPanel";
import PageTracker from "@/components/PageTracker";

export default function Home() {
  const report = buildTrackflowSmokeReport();

  const modules = [
    {
      title: "Inventario y Stock",
      tag: "Almacén",
      tagColor: "bg-emerald-100 text-emerald-800 border-emerald-200",
      description:
        "Control de catálogo de productos, órdenes de entrada/salida y niveles de stock sincronizados entre almacenes Los Ángeles y Zaragoza.",
      href: "/backoffice/inventory/products",
      actionText: "Ver Inventario",
      sublinks: [
        { label: "Catálogo", href: "/backoffice/inventory/products" },
        { label: "Órdenes", href: "/backoffice/inventory/orders" },
        { label: "Entradas", href: "/backoffice/inventory/orders/inbound" },
        { label: "Salidas", href: "/backoffice/inventory/orders/outbound" },
      ],
      icon: (
        <svg className="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
      ),
    },
    {
      title: "Gestión de Proveedores",
      tag: "Suministro",
      tagColor: "bg-blue-100 text-blue-800 border-blue-200",
      description:
        "Directorio centralizado de proveedores logísticos, estado de homologación, SLAs de entrega y evaluación de cumplimiento.",
      href: "/suppliers",
      actionText: "Directorio Proveedores",
      icon: (
        <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
    },
    {
      title: "Centro de Incidencias",
      tag: "Operaciones",
      tagColor: "bg-amber-100 text-amber-800 border-amber-200",
      description:
        "Triaje operativo, seguimiento de disrupciones en ruta, auditoría de fallos y resolución asistida en cadena logística.",
      href: "/incidents",
      actionText: "Ver Incidencias",
      sublinks: [
        { label: "Todas las incidencias", href: "/incidents" },
        { label: "Reportar nueva", href: "/incidents/new" },
      ],
      icon: (
        <svg className="w-6 h-6 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
    },
    {
      title: "Pipeline ETL & Tareas",
      tag: "Integración",
      tagColor: "bg-cyan-100 text-cyan-800 border-cyan-200",
      description:
        "Orquestación Celery/Redis, extracción y sincronización programada de albaranes de proveedores y exportaciones nocturnas.",
      href: "/pipeline",
      actionText: "Ejecutar Pipeline",
      icon: (
        <svg className="w-6 h-6 text-cyan-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      ),
    },
    {
      title: "Telemetría & Observabilidad",
      tag: "Analítica Pandas",
      tagColor: "bg-purple-100 text-purple-800 border-purple-200",
      description:
        "Métricas en tiempo real, latencias P95/P99, embudo de conversión, distribución de endpoints y log de eventos del sistema.",
      href: "/telemetry",
      actionText: "Dashboard Telemetría",
      icon: (
        <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      title: "RAG & Base de Conocimiento",
      tag: "Recuperación Vectorial",
      tagColor: "bg-indigo-100 text-indigo-800 border-indigo-200",
      description:
        "Búsqueda semántica con embeddings y base vectorial Qdrant sobre manuales de logística, normativas y protocolos de almacén.",
      href: "/knowledge",
      actionText: "Consultar Knowledge",
      icon: (
        <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      ),
    },
    {
      title: "Asistente Almacén (Chat IA)",
      tag: "WebSocket Streaming",
      tagColor: "bg-teal-100 text-teal-800 border-teal-200",
      description:
        "Streaming bidireccional en tiempo real, persistencia SQLite de memoria conversacional y fallback a LangGraph Multi-Agent.",
      href: "/chat",
      actionText: "Abrir Asistente IA",
      icon: (
        <svg className="w-6 h-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
    },
    {
      title: "Seguridad y Guardrails IA",
      tag: "NIST CSF 2.0 & HITL",
      tagColor: "bg-rose-100 text-rose-800 border-rose-200",
      description:
        "Gobernanza defensiva: detector de Prompt Injection, redactor de PII, control de cuota de tokens y autorización humana (HITL).",
      href: "/security",
      actionText: "Consola de Seguridad",
      icon: (
        <svg className="w-6 h-6 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
    },
  ];

  return (
    <>
      <PageTracker page="/" />
      <main className="mx-auto w-full max-w-7xl px-5 py-8 md:px-8 md:py-10">
        {/* Banner Superior Principal */}
        <section className="rounded-3xl border border-indigo-200 bg-gradient-to-r from-indigo-50 via-white to-cyan-50 px-6 py-10 shadow-sm md:px-10">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="inline-block rounded-full border border-indigo-200 bg-indigo-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-indigo-900">
                Backoffice Interno &middot; TrackFlow Global
              </p>
              <h1 className="mt-3 text-3xl font-bold text-slate-900 md:text-4xl">
                Centro de Control Operativo
              </h1>
              <p className="mt-2 max-w-3xl text-slate-700">
                Plataforma unificada para gestión de logística transfronteriza (Los Ángeles - Zaragoza).
                Navega por todos los subsistemas integrados en el monorepo sin necesidad de introducir URLs manuales.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="flex h-3 w-3 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-medium text-emerald-800 bg-emerald-50 border border-emerald-200 rounded-lg px-2.5 py-1">
                8 Módulos Conectados
              </span>
            </div>
          </div>
        </section>

        {/* Cuadrícula de Módulos (Feature Hub) */}
        <section className="mt-10">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-slate-900">Módulos del Sistema</h2>
              <p className="text-xs text-slate-500 mt-1">Acceso directo con navegación interactiva a cada servicio</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {modules.map((mod) => (
              <div
                key={mod.title}
                className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-xs transition hover:border-indigo-300 hover:shadow-md"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                      {mod.icon}
                    </div>
                    <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${mod.tagColor}`}>
                      {mod.tag}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900">
                    <Link href={mod.href} className="hover:text-indigo-600 transition">
                      {mod.title}
                    </Link>
                  </h3>
                  <p className="mt-2 text-xs leading-relaxed text-slate-600">
                    {mod.description}
                  </p>

                  {mod.sublinks && mod.sublinks.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-1.5">
                      {mod.sublinks.map((sub) => (
                        <Link
                          key={sub.label}
                          href={sub.href}
                          className="text-[11px] font-medium text-slate-500 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 px-2 py-0.5 rounded transition"
                        >
                          {sub.label}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mt-5 pt-3">
                  <Link
                    href={mod.href}
                    className="flex w-full items-center justify-center gap-1.5 rounded-xl bg-slate-900 px-3.5 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-600"
                  >
                    <span>{mod.actionText}</span>
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Panel de Smoke Checks de Integridad Compartida */}
        <section className="mt-12">
          <div className="mb-4">
            <h2 className="text-lg font-bold text-slate-900">
              Verificación de Integridad de Lógica Compartida
            </h2>
            <p className="text-xs text-slate-500">
              Pruebas de humo de la librería interna <code className="text-indigo-600">@trackflow/logic</code>
            </p>
          </div>
          <SmokeChecksPanel report={report} />
        </section>
      </main>
    </>
  );
}
