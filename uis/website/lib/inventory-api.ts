/**
 * Cliente API para conectar el website con el backend de inventario.
 * Opción A: Reemplazar datos mock con datos reales desde la API.
 */

// Usamos variable de entorno o fallback a localhost
const API_BASE_URL = process.env.NEXT_PUBLIC_INVENTORY_API_URL ?? "http://127.0.0.1:8001";

export interface ApiItem {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  quantity: number;
  price: number;
  category: string;
  warehouse: string;
  min_stock: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ApiItemsResponse {
  items: ApiItem[];
}

/**
 * Obtiene todos los items de inventario desde el backend.
 */
export async function fetchInventoryItems(): Promise<ApiItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/items/`);
  if (!res.ok) {
    throw new Error(`Error fetching inventory: ${res.status} ${res.statusText}`);
  }
  const data: ApiItemsResponse = await res.json();
  return data.items;
}

/**
 * Convierte un item de la API al formato Product que esperan los componentes.
 * Los campos específicos de logística se completan con valores por defecto.
 */
export function apiItemToProduct(
  item: ApiItem,
): {
  id: string;
  sku: string;
  name: string;
  category: string;
  weightKg: number;
  dimensions: { lengthCm: number; widthCm: number; heightCm: number };
  stockQuantity: number;
  minStockThreshold: number;
  unitCostUSD: number;
  isFragile: boolean;
  warehouse: string;
  status: string;
} {
  return {
    id: `item-${item.id}`,
    sku: item.sku,
    name: item.name,
    category: item.category,
    weightKg: 0, // No disponible en inventario
    dimensions: { lengthCm: 0, widthCm: 0, heightCm: 0 },
    stockQuantity: item.quantity,
    minStockThreshold: item.min_stock,
    unitCostUSD: item.price,
    isFragile: false,
    warehouse: item.warehouse,
    status: item.quantity < item.min_stock ? "Low stock" : "Active",
  };
}