// ============================================
// components/inventory/ProductRow.tsx — Fila de producto con indicador y acciones
// ============================================
// Muestra: SKU, nombre, categoría, almacén, precio, StockBadge
// Acciones: botones "Entrada" y "Salida" que enlazan con ?product_id=X
// ============================================

import Link from "next/link";
import { StockBadge } from "./StockBadge";
import type { Product } from "@/types/inventory";

interface ProductRowProps {
  product: Product;
}

export function ProductRow({ product }: ProductRowProps) {
  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
      <td className="px-4 py-3 text-sm font-mono text-gray-500">
        {product.sku}
      </td>
      <td className="px-4 py-3 text-sm font-medium text-gray-900">
        {product.name}
      </td>
      <td className="px-4 py-3 text-sm text-gray-600">{product.category}</td>
      <td className="px-4 py-3 text-sm text-gray-600">{product.warehouse}</td>
      <td className="px-4 py-3 text-sm text-gray-700">
        ${Number(product.price).toFixed(2)} USD
      </td>
      <td className="px-4 py-3">
        <StockBadge
          currentStock={product.current_stock}
          minStock={product.min_stock}
        />
      </td>
      <td className="px-4 py-3">
        <div className="flex gap-2">
          <Link
            href={`/backoffice/inventory/orders/inbound?product_id=${product.id}`}
            className="rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 transition-colors"
          >
            Entrada
          </Link>
          <Link
            href={`/backoffice/inventory/orders/outbound?product_id=${product.id}`}
            className="rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700 transition-colors"
          >
            Salida
          </Link>
        </div>
      </td>
    </tr>
  );
}