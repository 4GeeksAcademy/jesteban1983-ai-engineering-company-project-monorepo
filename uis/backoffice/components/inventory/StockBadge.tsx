// ============================================
// components/inventory/StockBadge.tsx — Badge de nivel de stock
// ============================================
// Indicador visual del nivel de existencias de un producto.
//
// Thresholds (según especificación del proyecto):
//   - Sin stock:  quantity <= 0      → ⚪ gris
//   - Stock bajo: quantity <= 5      → 🔴 rojo
//   - Stock medio: quantity <= 15    → 🟡 ámbar
//   - En stock:   quantity > 15      → 🟢 verde
// ============================================

import { getStockIcon, getStockLabel, getStockColor } from "@/types/inventory";

interface StockBadgeProps {
  currentStock: number;
  minStock?: number;
}

export function StockBadge({ currentStock, minStock = 10 }: StockBadgeProps) {
  const icon = getStockIcon(currentStock, minStock);
  const label = getStockLabel(currentStock, minStock);
  const color = getStockColor(currentStock, minStock);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${color}`}
    >
      <span aria-hidden="true">{icon}</span>
      <span>{label}</span>
      {currentStock > 0 && (
        <span className="font-semibold">{currentStock}</span>
      )}
    </span>
  );
}