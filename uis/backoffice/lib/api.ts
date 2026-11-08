// lib/api.ts — Helper de fetch con autenticación JWT y fallback interactivo para Vercel
//
// Propósito: Proveer funciones reutilizables para llamar a la API
// con el token JWT adjunto automáticamente en el header Authorization.
// En despliegues como Vercel donde los contenedores locales (puerto 8000)
// no están presentes, recurre transparentemente a la capa de demo en memoria.

import { handleDemoApiRequest } from "./demo-fallback";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

/**
 * Obtiene los headers de autenticación desde localStorage.
 * 
 * Si el usuario tiene un token JWT almacenado, lo incluye
 * en el header Authorization: Bearer <token>.
 * Solo se ejecuta en el navegador (localStorage no existe en SSR).
 */
export function authHeaders(): HeadersInit {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  return headers;
}

/**
 * Realiza una petición GET a la API.
 */
export async function apiGet<T = unknown>(path: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "GET",
      headers: authHeaders(),
    });

    if (!response.ok) {
      if ([404, 500, 502, 503, 504].includes(response.status)) {
        return handleDemoApiRequest<T>("GET", path);
      }
      throw { status: response.status, detail: await response.json().catch(() => ({})) };
    }

    return response.json();
  } catch (err: unknown) {
    const errorObj = err as { status?: number };
    if (errorObj?.status === 401) {
      throw err;
    }
    return handleDemoApiRequest<T>("GET", path);
  }
}

/**
 * Realiza una petición POST a la API.
 */
export async function apiPost<T = unknown>(
  path: string,
  body: Record<string, unknown>
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      if ([404, 500, 502, 503, 504].includes(response.status)) {
        return handleDemoApiRequest<T>("POST", path, body);
      }
      throw { status: response.status, detail: await response.json().catch(() => ({})) };
    }

    return response.json();
  } catch (err: unknown) {
    const errorObj = err as { status?: number };
    if (errorObj?.status === 401) {
      throw err;
    }
    return handleDemoApiRequest<T>("POST", path, body);
  }
}

/**
 * Realiza una petición PUT a la API.
 */
export async function apiPut<T = unknown>(
  path: string,
  body: Record<string, unknown>
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      if ([404, 500, 502, 503, 504].includes(response.status)) {
        return handleDemoApiRequest<T>("PUT", path, body);
      }
      throw { status: response.status, detail: await response.json().catch(() => ({})) };
    }

    return response.json();
  } catch (err: unknown) {
    const errorObj = err as { status?: number };
    if (errorObj?.status === 401) {
      throw err;
    }
    return handleDemoApiRequest<T>("PUT", path, body);
  }
}

/**
 * Realiza una petición PATCH a la API.
 */
export async function apiPatch<T = unknown>(
  path: string,
  body: Record<string, unknown>
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "PATCH",
      headers: authHeaders(),
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      if ([404, 500, 502, 503, 504].includes(response.status)) {
        return handleDemoApiRequest<T>("PATCH", path, body);
      }
      throw { status: response.status, detail: await response.json().catch(() => ({})) };
    }

    return response.json();
  } catch (err: unknown) {
    const errorObj = err as { status?: number };
    if (errorObj?.status === 401) {
      throw err;
    }
    return handleDemoApiRequest<T>("PATCH", path, body);
  }
}
