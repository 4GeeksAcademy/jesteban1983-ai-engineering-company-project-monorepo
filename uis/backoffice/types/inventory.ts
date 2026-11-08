// ============================================
// types/inventory.ts — Tipos del sistema de inventario para el backoffice
// ============================================
// Alineado con el REST contract de /inventory/* y vocabulario TrackFlow
// Proyecto: Hito 5 — Interfaz de Gestión de Inventario (4Geeks Academy)
//
// La lógica de nivel de stock (getStockLevel, getStockLabel, etc.)
// se ha movido a @trackflow/logic (packages/logic/src/trackflow/stock.ts)
// para evitar duplicación entre frontends.
// ============================================

export { getStockLevel, getStockLabel, getStockColor, getStockIcon } from "@trackflow/logic";
export type { StockLevel } from "@trackflow/logic";

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