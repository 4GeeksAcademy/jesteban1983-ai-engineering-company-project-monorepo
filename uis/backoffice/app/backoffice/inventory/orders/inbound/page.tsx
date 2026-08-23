// ============================================
// app/backoffice/inventory/orders/inbound/page.tsx — Formulario de entrada
// ============================================
// Fase 4: Registro de entrada de mercancía.
// Product selector con pre-selección desde ?product_id=X
// ============================================

"use client";

import { useSearchParams } from "next/navigation";
import { OrderForm } from "@/components/inventory/OrderForm";

export default function InboundPage() {
  const searchParams = useSearchParams();
  const productIdParam = searchParams.get("product_id");
  const preSelectedProductId = productIdParam
    ? parseInt(productIdParam, 10)
    : null;

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Entrada de mercancía</h1>
        <p className="mt-1 text-sm text-gray-500">
          Registra una entrada de productos al inventario.
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <OrderForm
          type="inbound"
          preSelectedProductId={preSelectedProductId}
        />
      </div>
    </div>
  );
}