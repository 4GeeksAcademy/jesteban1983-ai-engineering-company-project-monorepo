import {
  calculateAverageShipmentDistance,
  calculateTotalInventoryValue,
  filterLowStockProducts,
  findTopCarriers,
  Product,
  Shipment,
} from "@trackflow/logic";
import { CtaSection } from "../components/CtaSection";
import { HeroSection } from "../components/HeroSection";
import { KpiBand } from "../components/KpiBand";
import { OperationsFlow } from "../components/OperationsFlow";
import { ProductCatalog } from "../components/ProductCatalog";
import { ServiceGrid } from "../components/ServiceGrid";
import { TestimonialsSection } from "../components/TestimonialsSection";

const products: Product[] = [
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
  {
    id: "prd-002",
    sku: "HOM-ASP-ROBO",
    name: "Aspiradora robot",
    category: "Home",
    weightKg: 3.2,
    dimensions: { lengthCm: 34, widthCm: 34, heightCm: 10 },
    stockQuantity: 6,
    minStockThreshold: 8,
    unitCostUSD: 420,
    isFragile: true,
    warehouse: "Los Angeles",
    status: "Low stock",
  },
  {
    id: "prd-003",
    sku: "COS-SKIN-SET",
    name: "Skin care kit",
    category: "Cosmetics",
    weightKg: 0.7,
    dimensions: { lengthCm: 22, widthCm: 16, heightCm: 8 },
    stockQuantity: 60,
    minStockThreshold: 20,
    unitCostUSD: 48,
    isFragile: false,
    warehouse: "Zaragoza",
    status: "Active",
  },
  {
    id: "prd-004",
    sku: "FAS-SNE-URB",
    name: "Urban sneakers",
    category: "Fashion",
    weightKg: 0.9,
    dimensions: { lengthCm: 30, widthCm: 20, heightCm: 12 },
    stockQuantity: 34,
    minStockThreshold: 15,
    unitCostUSD: 79,
    isFragile: false,
    warehouse: "Los Angeles",
    status: "Active",
  },
];

const shipments: Shipment[] = [
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
  {
    id: "sh-1002",
    sku: "HOM-ASP-ROBO",
    quantity: 1,
    origin: "Los Angeles",
    destination: { city: "Monterrey", country: "Mexico", postalCode: "64000", distanceKm: 220 },
    priority: "Standard",
    declaredValueUSD: 420,
    carrier: "DHL",
    status: "Delivered",
    createdAt: new Date("2026-06-03T12:00:00.000Z"),
  },
  {
    id: "sh-1003",
    sku: "COS-SKIN-SET",
    quantity: 2,
    origin: "Zaragoza",
    destination: { city: "Valencia", country: "Spain", postalCode: "46001", distanceKm: 352 },
    priority: "Same-day",
    declaredValueUSD: 96,
    carrier: "SEUR",
    status: "Assigned",
    createdAt: new Date("2026-06-04T07:30:00.000Z"),
  },
];

export default function Home() {
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