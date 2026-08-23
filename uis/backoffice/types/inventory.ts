// ============================================
// types/inventory.ts — Tipos del sistema de inventario para el backoffice
// ============================================
// Alineado con el REST contract de /inventory/* y vocabulario TrackFlow
// Proyecto: Hito 5 — Interfaz de Gestión de Inventario (4Geeks Academy)
// ============================================

export interface Product {
  id: number;
  name: string;
  sku: string;
  current_stock: number;
  category: string;
  warehouse: string;
  price: number;
  min_stock: number;
  is_active: boolean;
}

export interface Order {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  order_type: "inbound" | "outbound";
  created_at: string;
  user_uuid: string | null;
}

export interface InboundOrderInput {
  product_id: number;
  quantity: number;
  reason?: string;
}

export interface OutboundOrderInput {
  product_id: number;
  quantity: number;
  reason?: string;
}

export interface ApiError {
  detail?: string;
  message?: string;
}

export type StockLevel = "high" | "medium" | "low" | "out";

export function getStockLevel(currentStock: number, minStock: number): StockLevel {
  if (currentStock <= 0) return "out";
  if (currentStock <= 5) return "low";
  if (currentStock <= 15) return "medium";
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