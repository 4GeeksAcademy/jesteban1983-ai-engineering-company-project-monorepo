import {
  calculateAverageShipmentDistance,
  calculateTotalInventoryValue,
  filterLowStockProducts,
  findTopCarriers,
} from "@trackflow/logic";
import { CtaSection } from "../components/CtaSection";
import { HeroSection } from "../components/HeroSection";
import { KpiBand } from "../components/KpiBand";
import { OperationsFlow } from "../components/OperationsFlow";
import { ProductCatalog } from "../components/ProductCatalog";
import { ServiceGrid } from "../components/ServiceGrid";
import { TestimonialsSection } from "../components/TestimonialsSection";
import { fetchInventoryItems, apiItemToProduct } from "../lib/inventory-api";

import type { Product, Shipment } from "@trackflow/logic";

const fallbackProducts: Product[] = [
  {
    id: "prd-001",
    sku: "ELEC-LAP-15",
    name: "Laptop 15 pulgadas",
    category: "Electronics",
    weightKg: 2.3,
    dimensions: { lengthCm: 38, widthCm: 25, heightCm: 3 },
    stockQuantity: 8,
    minStockThreshold: 10,
    unitCostUSD: 670,
    isFragile: true,
    warehouse: "Zaragoza",
    status: "Low stock",
  },
];

const fallbackShipments: Shipment[] = [
  {
    id: "sh-1001",
    sku: "ELEC-LAP-15",
    quantity: 1,
    origin: "Zaragoza",
    destination: { city: "Madrid", country: "Spain", postalCode: "28001", distanceKm: 320 },
    priority: "Express",
    declaredValueUSD: 670,
    carrier: "SEUR",
    status: "In transit",
    createdAt: new Date("2026-06-02T10:00:00.000Z"),
  },
];

async function getInventoryData() {
  try {
    const items = await fetchInventoryItems();
    const products: Product[] = items.map(apiItemToProduct) as Product[];
    return { products, shipments: fallbackShipments };
  } catch {
    console.warn("API de inventario no disponible, usando datos mock como fallback");
    return { products: fallbackProducts, shipments: fallbackShipments };
  }
}

export default async function Home() {
  const { products, shipments } = await getInventoryData();
  const lowStockProducts = filterLowStockProducts(products);
  const inventoryValue = calculateTotalInventoryValue(products);
  const avgDistance = calculateAverageShipmentDistance(shipments);
  const topCarriers = findTopCarriers(shipments, 1);
  const topCarrier = topCarriers[0];

  return (
    <main className="mx-auto w-full max-w-6xl px-5 py-8 md:px-8 md:py-10">
      <HeroSection lowStockCount={lowStockProducts.length} inventoryValueUSD={inventoryValue} />
      <ServiceGrid />
      <KpiBand
        avgDistance={avgDistance}
        topCarrierName={topCarrier?.carrier ?? "Sin datos"}
        topCarrierUsage={topCarrier?.count ?? 0}
      />
      <OperationsFlow />
      <ProductCatalog title="Catalogo con alertas de bajo stock" products={lowStockProducts} />
      <TestimonialsSection />
      <CtaSection />
    </main>
  );
}