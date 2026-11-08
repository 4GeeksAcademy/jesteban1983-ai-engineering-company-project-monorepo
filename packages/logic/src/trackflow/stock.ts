// ============================================
// trackflow/stock.ts — Lógica de nivel de stock
// ============================================
// Thresholds de nivel de stock (basados en min_stock del producto):
//   - currentStock <= 0               → "out"  (Sin stock)
//   - currentStock <= minStock / 2    → "low"  (Stock bajo)
//   - currentStock <= minStock * 1.5  → "medium" (Stock medio)
//   - currentStock > minStock * 1.5   → "high"  (En stock)
// ============================================

export type StockLevel = "high" | "medium" | "low" | "out";

export function getStockLevel(currentStock: number, minStock: number): StockLevel {
  if (currentStock <= 0) return "out";
  if (currentStock <= minStock / 2) return "low";
  if (currentStock <= minStock * 1.5) return "medium";
  return "high";
}

export function getStockLabel(currentStock: number, minStock: number): string {
  const level = getStockLevel(currentStock, minStock);
  const labels: Record<StockLevel, string> = {
    high: "En stock",
    medium: "Stock medio",
    low: "Stock bajo",
    out: "Sin stock",
  };
  return labels[level];
}

export function getStockColor(currentStock: number, minStock: number): string {
  const level = getStockLevel(currentStock, minStock);
  const colors: Record<StockLevel, string> = {
    high: "bg-green-100 text-green-800 border-green-300",
    medium: "bg-amber-100 text-amber-800 border-amber-300",
    low: "bg-red-100 text-red-800 border-red-300",
    out: "bg-gray-100 text-gray-800 border-gray-300",
  };
  return colors[level];
}

export function getStockIcon(currentStock: number, minStock: number): string {
  const level = getStockLevel(currentStock, minStock);
  const icons: Record<StockLevel, string> = {
    high: "🟢",
    medium: "🟡",
    low: "🔴",
    out: "⚪",
  };
  return icons[level];
}