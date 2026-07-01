import Image from "next/image";
import { filterLowStockProducts } from "@trackflow/logic";
import { ProductCatalog } from "../components/ProductCatalog";
import { Product } from "@trackflow/logic/src/trackflow/contracts";

// Mock data (en el futuro esto vendrá de un API)
const allProducts: Product[] = [
  {
    id: "1",
    sku: "A1",
    name: "Laptop",
    category: "Electronics",
    weightKg: 2.1,
    dimensions: { lengthCm: 36, widthCm: 25, heightCm: 2 },
    stockQuantity: 5,
    minStockThreshold: 10,
    unitCostUSD: 899,
    isFragile: true,
    warehouse: "Los Angeles",
    status: "Low stock",
  },
  {
    id: "2",
    sku: "A2",
    name: "Mouse",
    category: "Electronics",
    weightKg: 0.15,
    dimensions: { lengthCm: 12, widthCm: 6, heightCm: 4 },
    stockQuantity: 50,
    minStockThreshold: 10,
    unitCostUSD: 25,
    isFragile: false,
    warehouse: "Los Angeles",
    status: "Active",
  },
];

export default function Home() {
  const lowStock = filterLowStockProducts(allProducts);
  return (
    <main className="p-10">
      <h1 className="text-3xl font-bold mb-8">Dashboard TrackFlow</h1>
      
      <ProductCatalog 
        title="Alertas de Bajo Stock" 
        products={lowStock} 
      />
    </main>
  );
}