// ============================================
// lib/inventory.ts — Módulo central de llamadas a la API de inventario
// ============================================
// Proyecto: Hito 5 — Interfaz de Gestión de Inventario (4Geeks Academy)
//
// Este módulo CENTRALIZA todas las llamadas fetch a la API de inventario.
// NINGÚN componente debe hacer fetch directamente — siempre usar estas funciones.
//
// Requisitos del proyecto:
// - Authorization: Bearer <token> en todos los endpoints protegidos
// - Manejo explícito de errores con mensajes legibles para el usuario
// - Vocabulario TrackFlow en nombres de campo
// ============================================

import { getToken } from "./auth-actions";
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
 * Función genérica de fetch con autenticación Bearer.
 * Centraliza headers, manejo de errores y parseo de respuestas.
 */
async function inventoryFetch<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const token = getToken();

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });

  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = (await res.json()) as ApiError;
      message = body.detail ?? body.message ?? message;
    } catch {
      // Si no se puede parsear el JSON, usar statusText
    }

    // Mensajes de error legibles para el usuario
    if (res.status === 400) {
      throw new Error(message || "Solicitud inválida");
    }
    if (res.status === 401) {
      throw new Error("No autorizado. Por favor, inicia sesión de nuevo.");
    }
    if (res.status === 404) {
      throw new Error(message || "Recurso no encontrado");
    }
    if (res.status >= 500) {
      throw new Error(
        "Error del servidor. Intenta de nuevo más tarde."
      );
    }
    throw new Error(message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
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