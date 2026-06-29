/**
 * TrackFlow - Operaciones de Búsqueda
 * Hito 2: Fundamentos de Programación
 * 
 * Implementa búsqueda lineal y búsqueda binaria para encontrar
 * productos y envíos en las colecciones de TrackFlow.
 */

import {
  Product,
  Shipment,
} from "../../../../temp-repo/Jesteban1983-TrackFlow/src/types";

// ============================================================================
// BÚSQUEDA LINEAL
// ============================================================================

/**
 * Busca un producto por SKU (búsqueda lineal, case-insensitive)
 * 
 * Recorre el array hasta encontrar un producto cuyo SKU coincida
 * (sin considerar mayúsculas/minúsculas).
 * 
 * Complejidad: O(n) - peor caso debe recorrer todo el array
 * 
 * @param products - Array de productos donde buscar
 * @param sku - SKU del producto a buscar (case-insensitive)
 * @returns Producto si se encuentra, null en caso contrario
 * 
 * @example
 * // Buscar exactamente
 * findProductBySKU(products, "SHOE-BLK-42")
 * // { sku: "SHOE-BLK-42", ... }
 * 
 * // También funciona con diferente caso
 * findProductBySKU(products, "shoe-blk-42")
 * // { sku: "SHOE-BLK-42", ... }
 * 
 * // SKU que no existe
 * findProductBySKU(products, "NONEXISTENT")
 * // null
 */
export function findProductBySKU(
  products: Product[],
  sku: string
): Product | null {
  for (const product of products) {
    if (product.sku.toUpperCase() === sku.toUpperCase()) {
      return product;
    }
  }
  return null;
}

/**
 * Busca un envío por ID (búsqueda lineal)
 * 
 * Recorre el array hasta encontrar un envío con el ID especificado.
 * 
 * Complejidad: O(n) - peor caso debe recorrer todo el array
 * 
 * @param shipments - Array de envíos donde buscar
 * @param id - ID del envío a buscar (ej: "SH-2024-8821")
 * @returns Envío si se encuentra, null en caso contrario
 * 
 * @example
 * // Buscar envío existente
 * findShipmentById(shipments, "SH-2024-8821")
 * // { id: "SH-2024-8821", sku: "LAPTOP-DELL-15", ... }
 * 
 * // ID que no existe
 * findShipmentById(shipments, "SH-INVALID")
 * // null
 */
export function findShipmentById(
  shipments: Shipment[],
  id: string
): Shipment | null {
  for (const shipment of shipments) {
    if (shipment.id === id) {
      return shipment;
    }
  }
  return null;
}

// ============================================================================
// BÚSQUEDA BINARIA
// ============================================================================

/**
 * Busca un producto por peso usando búsqueda binaria
 * 
 * **PRECONDICIÓN**: El array debe estar previamente ordenado por
 * peso en orden ascendente (weightKg).
 * 
 * Busca exactamente un producto con el peso objetivo.
 * 
 * Complejidad: O(log n) - mucho más rápido que búsqueda lineal
 * para arrays grandes
 * 
 * **Nota**: Si hay múltiples productos con el mismo peso, puede
 * retornar cualquiera de ellos.
 * 
 * @param sortedProducts - Array de productos ordenado por peso (ascendente)
 * @param targetWeight - Peso exacto a buscar en kg
 * @returns Índice del producto si se encuentra, -1 en caso contrario
 * 
 * @example
 * // Array ya ordenado: [0.3kg, 0.8kg, 2.3kg, ...]
 * const products = [
 *   { sku: "PERFUME", weightKg: 0.3, ... },
 *   { sku: "SHOE", weightKg: 0.8, ... },
 *   { sku: "LAPTOP", weightKg: 2.3, ... }
 * ];
 * 
 * // Buscar un producto de 0.8kg
 * binarySearchProductByWeight(products, 0.8)
 * // 1 (índice del SHOE)
 * 
 * // Peso que no existe
 * binarySearchProductByWeight(products, 1.5)
 * // -1
 * 
 * // Peso exacto al inicio
 * binarySearchProductByWeight(products, 0.3)
 * // 0
 */
export function binarySearchProductByWeight(
  sortedProducts: Product[],
  targetWeight: number
): number {
  let left = 0;
  let right = sortedProducts.length - 1;
  
  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const midWeight = sortedProducts[mid].weightKg;
    
    if (midWeight === targetWeight) {
      return mid; // Peso encontrado
    } else if (midWeight < targetWeight) {
      left = mid + 1; // Buscar en la mitad derecha
    } else {
      right = mid - 1; // Buscar en la mitad izquierda
    }
  }
  
  return -1; // Peso no encontrado
}
