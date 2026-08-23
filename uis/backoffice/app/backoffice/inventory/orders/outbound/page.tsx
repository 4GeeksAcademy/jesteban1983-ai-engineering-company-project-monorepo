// ============================================
// app/backoffice/inventory/orders/outbound/page.tsx — Formulario de salida
// ============================================
// Fase 5: Registro de salida de mercancía.
// Product selector con pre-selección desde ?product_id=X
// Stock reactivo + warning si cantidad > stock
// ============================================

"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { OrderForm } from "@/components/inventory/OrderForm";

function OutboundForm() {
  const searchParams = useSearchParams();
  const productIdParam = searchParams.get("product_id");
  const preSelectedProductId = productIdParam
    ? parseInt(productIdParam, 10)
    : null;

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Salida de mercancía</h1>
        <p className="mt-1 text-sm text-gray-500">
          Registra una salida de productos del inventario.
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <OrderForm
          type="outbound"
          preSelectedProductId={preSelectedProductId}
        />
      </div>
    </div>
  );
}

export default function OutboundPage() {
  return (
    <Suspense fallback={
      <div className="mx-auto max-w-2xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Salida de mercancía</h1>
          <p className="mt-1 text-sm text-gray-500">Cargando...</p>
        </div>
      </div>
    }>
      <OutboundForm />
    </Suspense>
  );
}