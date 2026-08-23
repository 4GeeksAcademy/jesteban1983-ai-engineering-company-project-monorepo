// components/navbar-auth.tsx — Barra de navegación con autenticación
//
// Propósito: Renderiza la navegación del backoffice incluyendo
// enlaces a las páginas de gestión de inventario y botón de
// login/logout según el estado de autenticación.
//
// Comportamiento:
// - Si el usuario está autenticado: muestra enlaces de inventario + Cerrar sesión
// - Si NO está autenticado: muestra solo enlaces públicos + Iniciar sesión
//
// NOTA: Este componente es "use client" porque necesita acceder a
// localStorage para verificar el token y manejar logout.

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { isAuthenticated, logoutUser } from "@/lib/auth-actions";

export default function NavbarAuth() {
  const [authenticated, setAuthenticated] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setAuthenticated(isAuthenticated());
  }, [pathname]);

  const handleLogout = () => {
    logoutUser();
  };

  return (
    <header className="border-b border-indigo-100 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex w-full max-w-6xl items-center justify-between px-5 py-3 md:px-8">
        <Link href="/" className="text-sm font-bold tracking-wide text-indigo-900">
          TrackFlow Backoffice
        </Link>
        <div className="flex items-center gap-3 text-sm font-medium text-slate-700">
          <Link className="rounded-lg px-3 py-2 transition hover:bg-indigo-50" href="/">
            Inicio
          </Link>
          <Link
            className="rounded-lg px-3 py-2 transition hover:bg-indigo-50"
            href="/incidents"
          >
            Incidencias
          </Link>

          {authenticated && (
            <>
              <Link
                className="rounded-lg px-3 py-2 transition hover:bg-indigo-50"
                href="/backoffice/inventory/products"
              >
                Productos
              </Link>
              <Link
                className="rounded-lg px-3 py-2 transition hover:bg-indigo-50"
                href="/backoffice/inventory/orders/inbound"
              >
                Entrada
              </Link>
              <Link
                className="rounded-lg px-3 py-2 transition hover:bg-indigo-50"
                href="/backoffice/inventory/orders/outbound"
              >
                Salida
              </Link>
              <Link
                className="rounded-lg px-3 py-2 transition hover:bg-indigo-50"
                href="/backoffice/inventory/orders"
              >
                Historial
              </Link>
            </>
          )}

          {authenticated ? (
            <button
              onClick={handleLogout}
              className="rounded-lg border border-red-200 px-3 py-2 text-red-600 transition hover:bg-red-50"
            >
              Cerrar sesión
            </button>
          ) : (
            <Link
              className="rounded-lg bg-indigo-600 px-4 py-2 text-white shadow hover:bg-indigo-700 transition"
              href="/login"
            >
              Iniciar sesión
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}