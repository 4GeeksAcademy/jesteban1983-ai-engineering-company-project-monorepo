// ============================================
// app/backoffice/inventory/orders/page.tsx — Historial de órdenes
// ============================================
// Fase 6: Listado de movimientos de inventario (solo lectura).
// Muestra: product_name, quantity, order_type, created_at, user_uuid
// ============================================

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { listOrders } from "@/lib/inventory";
import { isAuthenticated } from "@/lib/auth-actions";
import { ErrorBanner } from "@/components/inventory/ErrorBanner";
import type { Order } from "@/types/inventory";

export default function OrdersHistoryPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  // Load orders
  useEffect(() => {
    const load = async () => {
      try {
        const data = await listOrders();
        setOrders(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar órdenes");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Historial de movimientos</h1>
        <p className="mt-1 text-sm text-gray-500">
          Todas las entradas y salidas registradas en el inventario.
        </p>
      </div>

      {/* Error */}
      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <p className="text-gray-500">Cargando historial...</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && orders.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="text-gray-500">No hay movimientos registrados.</p>
        </div>
      )}

      {/* Table */}
      {!loading && orders.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Producto
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Tipo
                </th>
                <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Cantidad
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Fecha
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Usuario
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {orders.map((order) => (
                <tr
                  key={order.id}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {order.product_name}
                  </td>
                  <td className="px-4 py-3">
                    {order.order_type === "inbound" ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-800">
                        Entrada
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-semibold text-red-800">
                        Salida
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-mono tabular-nums">
                    <span
                      className={
                        order.order_type === "inbound"
                          ? "text-green-700"
                          : "text-red-700"
                      }
                    >
                      {order.order_type === "inbound" ? "+" : "-"}
                      {order.quantity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatDate(order.created_at)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 font-mono">
                    {order.user_uuid
                      ? `${order.user_uuid.slice(0, 8)}...`
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}