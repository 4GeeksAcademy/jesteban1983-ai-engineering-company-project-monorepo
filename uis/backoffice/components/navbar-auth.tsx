// components/navbar-auth.tsx — Barra de navegación con autenticación y módulos globales
//
// Propósito: Renderiza la navegación integral del backoffice conectando
// todos los módulos construidos en el curso: Inventario, Proveedores, Incidencias,
// Pipeline ETL, Telemetría, Knowledge Base, Chat en tiempo real y Seguridad IA.

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { isAuthenticated, logoutUser } from "@/lib/auth-actions";
import { track } from "@/lib/telemetry";

export default function NavbarAuth() {
  const [authenticated, setAuthenticated] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setAuthenticated(isAuthenticated());
  }, [pathname]);

  const handleLogout = () => {
    try {
      const loginTimestamp = sessionStorage.getItem("telemetry_login_timestamp");
      const sessionDuration = loginTimestamp
        ? Math.floor((Date.now() - parseInt(loginTimestamp, 10)) / 1000)
        : 0;

      track("session_expired", {
        session_duration_seconds: sessionDuration,
        expired_reason: "logout",
      });
    } catch {
      // Ignorar fallo de telemetría en logout
    }

    logoutUser();
  };

  const navLinks = [
    { href: "/", label: "Inicio" },
    { href: "/backoffice/inventory/products", label: "Inventario" },
    { href: "/suppliers", label: "Proveedores" },
    { href: "/incidents", label: "Incidencias" },
    { href: "/pipeline", label: "Pipeline" },
    { href: "/telemetry", label: "Telemetría" },
    { href: "/knowledge", label: "RAG" },
    { href: "/chat", label: "Chat IA" },
    { href: "/security", label: "Seguridad IA" },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-indigo-100 bg-white/95 backdrop-blur shadow-xs">
      <nav className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-2.5 md:px-8">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2 text-sm font-bold tracking-tight text-indigo-950">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white font-black text-xs shadow-xs">
              TF
            </span>
            <span className="hidden sm:inline">TrackFlow</span>
          </Link>

          <div className="hidden lg:flex items-center gap-1 text-xs font-medium text-slate-600">
            {navLinks.map((link) => {
              const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`rounded-lg px-2.5 py-1.5 transition ${
                    isActive
                      ? "bg-indigo-50 font-bold text-indigo-700"
                      : "hover:bg-slate-50 hover:text-indigo-900 text-slate-600"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Links visibles en pantallas medianas */}
        <div className="flex lg:hidden items-center gap-1 overflow-x-auto max-w-[60vw] py-1 text-xs text-slate-600">
          <Link href="/backoffice/inventory/products" className="rounded-lg px-2 py-1 hover:bg-slate-100">
            Inventario
          </Link>
          <Link href="/suppliers" className="rounded-lg px-2 py-1 hover:bg-slate-100">
            Proveedores
          </Link>
          <Link href="/incidents" className="rounded-lg px-2 py-1 hover:bg-slate-100">
            Incidencias
          </Link>
          <Link href="/chat" className="rounded-lg px-2 py-1 hover:bg-slate-100 text-indigo-600 font-semibold">
            Chat
          </Link>
        </div>

        <div className="flex items-center gap-2 text-xs font-medium">
          {authenticated ? (
            <div className="flex items-center gap-2">
              <Link
                className="rounded-lg px-2.5 py-1.5 transition hover:bg-indigo-50 text-slate-700 hidden sm:inline"
                href="/account/profile"
              >
                Mi Perfil
              </Link>
              <button
                onClick={handleLogout}
                className="rounded-lg border border-red-200 px-3 py-1.5 text-red-600 transition hover:bg-red-50 text-xs font-semibold"
              >
                Cerrar sesión
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                className="rounded-lg px-3 py-1.5 text-slate-700 hover:bg-slate-100 transition hidden sm:inline"
                href="/register"
              >
                Registro
              </Link>
              <Link
                className="rounded-lg bg-indigo-600 px-3.5 py-1.5 text-white shadow-xs hover:bg-indigo-700 transition"
                href="/login"
              >
                Iniciar sesión
              </Link>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
}
