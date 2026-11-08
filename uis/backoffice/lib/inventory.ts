// ============================================
// lib/inventory.ts — Módulo central de llamadas a la API de inventario
// ============================================
// Proyecto: Hito 5 — Interfaz de Gestión de Inventario (4Geeks Academy)
//
// Este módulo CENTRALIZA todas las llamadas fetch a la API de inventario.
// NINGÚN componente debe hacer fetch directamente — siempre usar estas funciones.
// Incluye fallback interactivo a memoria para demostración fluida en Vercel.
// ============================================

import { getToken } from "./auth-actions";
import {
  getDemoProducts,
  getDemoProduct,
  getDemoOrders,
  createDemoOrder,
} from "./demo-fallback";
import type {
  Product,
  Order,
  InboundOrderInput,
  OutboundOrderInput,
  ApiError,
} from "@/types/inventory";

const API_BASE = (
  process.env.NEXT_PUBLIC_INVENTORY_API_URL || "http://localhost:8000"
).replace(/\/$/, "");

/**
 * Función genérica de fetch con autenticación Bearer y fallback de demo.
 */
async function inventoryFetch<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const token = getToken();

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init?.headers,
      },
    });

    if (!res.ok) {
      // Si el microservicio de inventario no está corriendo (despliegue estático en Vercel)
      if ([404, 500, 502, 503, 504].includes(res.status)) {
        return fallbackInventoryHandler<T>(path, init);
      }

      let message = res.statusText;
      try {
        const body = (await res.json()) as ApiError;
        message = body.detail ?? body.message ?? message;
      } catch {
        // Si no se puede parsear el JSON, usar statusText
      }

      if (res.status === 401) {
        throw new Error("No autorizado. Por favor, inicia sesión de nuevo.");
      }
      throw new Error(message);
    }

    if (res.status === 204) return undefined as T;
    return res.json() as Promise<T>;
  } catch (err: unknown) {
    const errObj = err as Error;
    if (errObj?.message?.includes("No autorizado")) {
      throw err;
    }
    return fallbackInventoryHandler<T>(path, init);
  }
}

function fallbackInventoryHandler<T>(path: string, init?: RequestInit): T {
  if (path === "/inventory/products") {
    return getDemoProducts() as unknown as T;
  }
  const productMatch = path.match(/^\/inventory\/products\/(\d+)$/);
  if (productMatch) {
    return getDemoProduct(Number(productMatch[1])) as unknown as T;
  }
  if (path === "/inventory/orders/inbound" && init?.method === "POST") {
    const body = init.body ? JSON.parse(String(init.body)) : {};
    return createDemoOrder("inbound", body) as unknown as T;
  }
  if (path === "/inventory/orders/outbound" && init?.method === "POST") {
    const body = init.body ? JSON.parse(String(init.body)) : {};
    return createDemoOrder("outbound", body) as unknown as T;
  }
  if (path === "/inventory/orders") {
    return getDemoOrders() as unknown as T;
  }
  return [] as unknown as T;
}

// ============================================
// Productos
// ============================================

/** Obtiene la lista de todos los productos del inventario. */
export const listProducts = () =>
  inventoryFetch<Product[]>("/inventory/products");

/** Obtiene un producto por su ID. */
export const getProduct = (id: number) =>
  inventoryFetch<Product>(`/inventory/products/${id}`);

// ============================================
// Órdenes (Entradas y Salidas)
// ============================================

/** Registra una entrada de mercancía (inbound). */
export const createInboundOrder = (body: InboundOrderInput) =>
  inventoryFetch<Order>("/inventory/orders/inbound", {
    method: "POST",
    body: JSON.stringify(body),
  });

/** Registra una salida/venta (outbound). */
export const createOutboundOrder = (body: OutboundOrderInput) =>
  inventoryFetch<Order>("/inventory/orders/outbound", {
    method: "POST",
    body: JSON.stringify(body),
  });

/** Obtiene el historial de todas las órdenes. */
export const listOrders = () =>
  inventoryFetch<Order[]>("/inventory/orders");
