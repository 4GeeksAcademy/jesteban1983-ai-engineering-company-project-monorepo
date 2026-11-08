// ============================================
// app/backoffice/inventory/products/page.tsx — Listado de productos
// ============================================
// Fase 3: Página principal de inventario.
// Muestra tabla con SKU, nombre, categoría, almacén, precio, StockBadge.
// Botones de acción: Entrada / Salida con ?product_id=X
// ============================================

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { listProducts } from "@/lib/inventory";
import { isAuthenticated } from "@/lib/auth-actions";
import { ProductRow } from "@/components/inventory/ProductRow";
import { ErrorBanner } from "@/components/inventory/ErrorBanner";
import type { Product } from "@/types/inventory";

export default function ProductsPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  // Load products
  useEffect(() => {
    const load = async () => {
      try {
        const data = await listProducts();
        setProducts(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar productos");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Productos</h1>
        <p className="mt-1 text-sm text-gray-500">
          Gestión de inventario — TrackFlow
        </p>
      </div>

      {/* Error */}
      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-16">
          <p className="text-gray-500">Cargando productos...</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && products.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <p className="text-gray-500">No hay productos registrados.</p>
        </div>
      )}

      {/* Table */}
      {!loading && products.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  SKU
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Nombre
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Categoría
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Almacén
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Costo unitario (USD)
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Stock
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {products.map((product) => (
                <ProductRow key={product.id} product={product} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}