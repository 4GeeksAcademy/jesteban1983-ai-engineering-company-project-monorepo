// packages/logic/src/trackflow/contracts.ts

export type WarehouseLocation = "Los Angeles" | "Zaragoza";
export type ProductStatus = "Active" | "Low stock" | "Out of stock";
export type ProductCategory = "Fashion" | "Electronics" | "Cosmetics" | "Home" | "Other";

export interface Product {
  id: string;
  sku: string;
  name: string;
  category: string;
  stockQuantity: number;
  minStockThreshold: number;
  warehouse: WarehouseLocation;
  status: ProductStatus;
}

export interface Carrier {
  id: string;
  name: string;
  onTimeRate: number;
}