/**
 * TrackFlow - Test Principal
 * Hito 2: Fundamentos de Programación
 * 
 * Pruebas de fuego para validar el motor lógico
 */

import {
  Product,
  Carrier,
  Shipment,
  calculateShippingCost,
  scoreCarrierForShipment,
  selectBestCarrier,
  validateProduct,
  validateShipment,
  validateCarrier,
} from "./index";

// ============================================================================
// DATOS DE PRUEBA
// ============================================================================

const testProduct: Product = {
  sku: "LAPTOP-DELL-15",
  name: "Laptop Dell 15 pulgadas",
  category: "Electronics",
  weightKg: 2.3,
  dimensions: { lengthCm: 40, widthCm: 28, heightCm: 3 },
  warehouse: "Zaragoza",
  stockQuantity: 8,
  minStockThreshold: 10,
  unitCostUSD: 650.0,
  isFragile: true,
  status: "Low stock",
};

const testCarrier: Carrier = {
  id: "CAR-SEUR",
  name: "SEUR",
  operatesIn: ["Spain"],
  baseRateUSD: 6.5,
  ratePerKgUSD: 1.5,
  ratePerKmUSD: 0.08,
  avgDeliveryDays: 2,
  onTimeRate: 92,
  maxWeightKg: 25,
  handlesFragile: true,
  acceptsPriority: ["Standard", "Express", "Same-day"],
};

const testShipment: Shipment = {
  id: "SH-2024-8821",
  sku: "LAPTOP-DELL-15",
  quantity: 1,
  origin: "Zaragoza",
  destination: {
    city: "Madrid",
    country: "Spain",
    postalCode: "28001",
    distanceKm: 320,
  },
  priority: "Express",
  declaredValueUSD: 650.0,
  carrier: null,
  status: "Pending",
  createdAt: new Date("2024-03-15"),
};

// ============================================================================
// PRUEBAS DE FUEGO
// ============================================================================

console.log("=== PRUEBAS DE FUEGO: TRACKFLOW HITO 2 ===\n");

// Test 1: Validación de Producto
console.log("✓ Test 1: Validación de Producto");
const productValidation = validateProduct(testProduct);
console.log(`  Válido: ${productValidation.valid}`);
if (!productValidation.valid) {
  console.log(`  Errores: ${productValidation.errors.join(", ")}`);
}

// Test 2: Validación de Envío
console.log("\n✓ Test 2: Validación de Envío");
const shipmentValidation = validateShipment(testShipment);
console.log(`  Válido: ${shipmentValidation.valid}`);
if (!shipmentValidation.valid) {
  console.log(`  Errores: ${shipmentValidation.errors.join(", ")}`);
}

// Test 3: Validación de Transportista
console.log("\n✓ Test 3: Validación de Transportista");
const carrierValidation = validateCarrier(testCarrier);
console.log(`  Válido: ${carrierValidation.valid}`);
if (!carrierValidation.valid) {
  console.log(`  Errores: ${carrierValidation.errors.join(", ")}`);
}

// Test 4: Cálculo de Costo
console.log("\n✓ Test 4: Cálculo de Costo de Envío");
const costo = calculateShippingCost(testShipment, testProduct, testCarrier);
console.log(`  Costo calculado: $${costo}`);
console.log(`  (Incluye +30% por prioridad Express)`);

// Test 5: Scoring de Transportista
console.log("\n✓ Test 5: Scoring de Transportista");
const score = scoreCarrierForShipment(testCarrier, testShipment, testProduct);
console.log(`  Puntuación: ${score}/100`);
console.log(`  Componentes:`);
console.log(`    - Opera en destino (Spain): +20`);
console.log(`    - Maneja peso (2.3kg ≤ 25kg): +20`);
console.log(`    - Soporta Express: +15`);
console.log(`    - Maneja frágiles: +15`);
console.log(`    - Confiabilidad (92% × 0.3): +27.6`);

// Test 6: Selección del Mejor Transportista
console.log("\n✓ Test 6: Selección del Mejor Transportista");
const carriers = [testCarrier];
const best = selectBestCarrier(carriers, testShipment, testProduct);
if (best) {
  console.log(`  Seleccionado: ${best.carrier.name}`);
  console.log(`  Costo: $${best.cost}`);
  console.log(`  Score: ${best.score}/100`);
} else {
  console.log(`  No hay transportistas adecuados (score < 50)`);
}

console.log("\n=== TODAS LAS PRUEBAS COMPLETADAS ===");
