// ============================================
// components/inventory/OrderForm.tsx — Formulario genérico de órdenes
// ============================================
// Renderiza un formulario de entrada o salida de mercancía.
//
// Props:
// - type: "inbound" | "outbound" — define el comportamiento
// - preSelectedProductId: ID del producto pre-seleccionado (desde URL)
//
// Para outbound:
//   - Muestra stock actual al seleccionar producto
//   - Warning si cantidad > stock disponible
// ============================================

"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { listProducts, getProduct, createInboundOrder, createOutboundOrder } from "@/lib/inventory";
import { isAuthenticated } from "@/lib/auth-actions";
import { ErrorBanner } from "./ErrorBanner";
import type { Product } from "@/types/inventory";

interface OrderFormProps {
  type: "inbound" | "outbound";
  preSelectedProductId?: number | null;
}

export function OrderForm({ type, preSelectedProductId }: OrderFormProps) {
  const router = useRouter();
  const isInbound = type === "inbound";

  const [products, setProducts] = useState<Product[]>([]);
  const [productId, setProductId] = useState<number | "">(preSelectedProductId ?? "");
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [currentStock, setCurrentStock] = useState<number | null>(null);
  const [stockWarning, setStockWarning] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
    }
  }, [router]);

  // Load products
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await listProducts();
        setProducts(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar productos");
      } finally {
        setFetching(false);
      }
    };
    loadProducts();
  }, []);

  // Load stock for selected product (outbound only)
  useEffect(() => {
    if (!isInbound && productId) {
      const loadStock = async () => {
        try {
          const product = await getProduct(Number(productId));
          setCurrentStock(product.current_stock);
        } catch {
          setCurrentStock(null);
        }
      };
      loadStock();
    } else {
      setCurrentStock(null);
    }
  }, [productId, isInbound]);

  // Client-side stock warning (outbound only)
  useEffect(() => {
    if (!isInbound && currentStock !== null && quantity) {
      const qty = parseInt(quantity, 10);
      if (!isNaN(qty) && qty > currentStock) {
        setStockWarning(
          `⚠️ La cantidad solicitada (${qty}) supera el stock disponible (${currentStock}).`
        );
      } else {
        setStockWarning(null);
      }
    } else {
      setStockWarning(null);
    }
  }, [quantity, currentStock, isInbound]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!productId) {
      setError("Selecciona un producto.");
      return;
    }
    const qty = parseInt(quantity, 10);
    if (isNaN(qty) || qty <= 0) {
      setError("La cantidad debe ser un número entero positivo.");
      return;
    }

    setLoading(true);
    try {
      if (isInbound) {
        await createInboundOrder({
          product_id: Number(productId),
          quantity: qty,
          reason: reason || undefined,
        });
      } else {
        await createOutboundOrder({
          product_id: Number(productId),
          quantity: qty,
          reason: reason || undefined,
        });
      }

      // Success
      setSuccess(
        isInbound
          ? `✅ Entrada registrada: ${qty} unidades.`
          : `✅ Salida registrada: ${qty} unidades.`
      );
      setQuantity("");
      setReason("");

      // Refresh stock after outbound
      if (!isInbound && productId) {
        const updated = await getProduct(Number(productId));
        setCurrentStock(updated.current_stock);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al procesar la orden");
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-gray-500">Cargando productos...</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Error banner */}
      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {/* Success banner */}
      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <p className="text-sm font-medium text-green-800">{success}</p>
        </div>
      )}

      {/* Product selector */}
      <div>
        <label
          htmlFor="product"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Producto
        </label>
        <select
          id="product"
          value={productId}
          onChange={(e) => setProductId(e.target.value ? Number(e.target.value) : "")}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          required
        >
          <option value="">Selecciona un producto...</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.sku} — {p.name}
            </option>
          ))}
        </select>
      </div>

      {/* Current stock display (outbound only) */}
      {!isInbound && currentStock !== null && (
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-3">
          <p className="text-sm text-blue-800">
            <span className="font-medium">Stock actual:</span>{" "}
            {currentStock} unidades
          </p>
        </div>
      )}

      {/* Quantity */}
      <div>
        <label
          htmlFor="quantity"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Cantidad
        </label>
        <input
          id="quantity"
          type="number"
          min="1"
          step="1"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          className={`w-full rounded-lg border px-3 py-2 text-sm focus:ring-1 focus:ring-blue-500 ${
            stockWarning
              ? "border-amber-400 focus:border-amber-500"
              : "border-gray-300 focus:border-blue-500"
          }`}
          placeholder="Ej: 10"
          required
        />
        {stockWarning && (
          <p className="mt-1 text-sm text-amber-700">{stockWarning}</p>
        )}
      </div>

      {/* Reason (optional) */}
      <div>
        <label
          htmlFor="reason"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Motivo <span className="text-gray-400">(opcional)</span>
        </label>
        <input
          id="reason"
          type="text"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          placeholder={
            isInbound
              ? "Ej: Reposición de stock"
              : "Ej: Venta al cliente"
          }
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className={`w-full rounded-lg px-4 py-2.5 text-sm font-medium text-white transition-colors ${
          isInbound
            ? "bg-green-600 hover:bg-green-700 disabled:bg-green-400"
            : "bg-red-600 hover:bg-red-700 disabled:bg-red-400"
        }`}
      >
        {loading
          ? "Procesando..."
          : isInbound
          ? "Registrar entrada"
          : "Registrar salida"}
      </button>
    </form>
  );
}