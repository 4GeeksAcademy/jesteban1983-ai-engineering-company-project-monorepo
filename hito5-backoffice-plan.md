# Hito 5 — Backoffice: Interfaz de Gestión de Inventario

## Plan de Desarrollo Fase por Fase

> **Contexto:** Este plan describe cómo implementar el proyecto "Hito 5 — Backoffice: Interfaz de Gestión de Inventario" de 4Geeks Academy sobre el monorepo existente de TrackFlow.
>
> **Objetivo:** 4 páginas en el backoffice (productos, entrada, salida, historial) + integración con API + autenticación.
>
> **Rama de trabajo:** `feature/inventory-backoffice` (basada en `milestone-4`)

---

## 📋 Diagnóstico Inicial

### Lo que YA tenemos (no reinventar)

| Componente | Estado | Ubicación |
|---|---|---|
| Backend FastAPI + SQLAlchemy | ✅ Funcionando | `services/inventory/` |
| Modelos: `Item`, `Movement` | ✅ Con campos `quantity`, `min_stock`, `movement_type` | `app/models/` |
| CRUD completo | ✅ `get_items`, `create_item`, `adjust_stock`, etc. | `app/crud/` |
| Auth backend (JWT) | ✅ Existe en `origin/feature/auth` | `services/api/` (API diferente) |
| Auth frontend (login+form+nav) | ✅ Existe en `origin/feature/auth-frontend` | `uis/backoffice/` |
| Backoffice base (layout, nav) | ✅ Funcionando | `uis/backoffice/` |
| Tailwind v4 + Next.js 16 | ✅ Configurado | `uis/backoffice/` |
| Tests 50/50 pasando | ✅ Verificado | `services/inventory/tests/` |
| Supabase (PostgreSQL 17.6) | ✅ Conectado | `db.lxzwdcgfhpqbpbzntnbg.supabase.co` |

### Lo que FALTA (hay que construir)

| Componente | Prioridad | Depende de |
|---|---|---|
| **FASE 0:** Mergear auth frontend | 🔴 CRÍTICA | Nada |
| **FASE 1:** Nuevos endpoints backend para `/inventory/*` | 🔴 CRÍTICA | Nada |
| **FASE 1a:** Añadir `user_uuid` al modelo Movement | 🔴 CRÍTICA | FASE 1 |
| **FASE 2:** `lib/inventory.ts` (integración API) | 🟡 ALTA | FASE 1 |
| **FASE 2a:** `types/inventory.ts` (tipos TS) | 🟡 ALTA | FASE 2 |
| **FASE 3:** Página productos (`/backoffice/inventory/products`) | 🟡 ALTA | FASE 2 |
| **FASE 4:** Formulario entrada (`/backoffice/inventory/orders/inbound`) | 🟡 ALTA | FASE 2 |
| **FASE 5:** Formulario salida (`/backoffice/inventory/orders/outbound`) | 🟡 ALTA | FASE 2 |
| **FASE 6:** Historial órdenes (`/backoffice/inventory/orders`) | 🟢 MEDIA | FASE 2 |
| **FASE 7:** Route protection + verificación final | 🟢 MEDIA | FASES 3-6 |

---

## 📐 REST Contract (objetivo final)

Basado en la [solución de referencia de 4Geeks](https://github.com/4GeeksAcademy/ai-engineering-syllabus/blob/main/content/projects/ai-eng-inventory-management-backoffice/.learn/solution/README.md) y adaptado a nuestro backend existente.

Endpoint base: `NEXT_PUBLIC_INVENTORY_API_URL` (ej: `http://localhost:8000`)

| Operación | Método | Ruta | Auth | Response esperado |
|---|---|---|---|---|
| Listar productos | `GET` | `/inventory/products` | Bearer | `[{ id, name, sku, current_stock, ... }]` |
| Obtener producto | `GET` | `/inventory/products/{id}` | Bearer | `{ id, name, sku, current_stock }` |
| Registrar entrada | `POST` | `/inventory/orders/inbound` | Bearer | `{ id, product_id, quantity, order_type, created_at }` |
| Registrar salida | `POST` | `/inventory/orders/outbound` | Bearer | `{ id, product_id, quantity, order_type, created_at }` |
| Listar órdenes | `GET` | `/inventory/orders` | Bearer | `[{ id, product_id, product_name, quantity, order_type, created_at, user_uuid }]` |

### Mapeo con nuestro backend actual

| Ruta nueva (proyecto) | Endpoint existente | Adaptación necesaria |
|---|---|---|
| `GET /inventory/products` | `GET /api/v1/items/` | Renombrar campo `quantity` → `current_stock` |
| `GET /inventory/products/{id}` | `GET /api/v1/items/{id}` | Idem |
| `POST /inventory/orders/inbound` | `POST /api/v1/items/{id}/adjust-stock` (con `movement_type=inbound`) | Nueva ruta específica |
| `POST /inventory/orders/outbound` | `POST /api/v1/items/{id}/adjust-stock` (con `movement_type=outbound`) | Nueva ruta específica |
| `GET /inventory/orders` | `GET /api/v1/items/{id}/movements` (por item) | Nueva ruta que lista TODOS los movimientos |

---

## 🧠 Vocabulario TrackFlow (de CONTEXT.md)

Para cumplir con "entity names and field labels match CONTEXT.md":

| Término genérico | Término TrackFlow |
|---|---|
| Product | **Item / Producto** (SKU-based) |
| Product list | **Inventario de productos** |
| Stock | **Stock / Existencias** |
| Low stock | **Stock bajo** (`quantity < min_stock`) |
| Out of stock | **Sin stock** (`quantity = 0`) |
| Warehouse | **Almacén** (Los Angeles, Zaragoza) |
| Inbound order | **Entrada de mercancía** |
| Outbound order | **Salida / Venta** |
| Order history | **Historial de movimientos** |
| User | **Operador** (user_uuid) |
| Price | **Costo unitario (USD)** |

---

## 🗺️ Estructura de archivos a crear/modificar

```
uis/backoffice/
├── app/
│   ├── layout.tsx                    [MODIFICAR] → navbar-auth en vez de header estático
│   ├── login/
│   │   └── page.tsx                  [CREAR] → Página de login (desde auth-frontend)
│   ├── register/
│   │   └── page.tsx                  [CREAR] → Página de registro (desde auth-frontend)
│   ├── backoffice/
│   │   └── inventory/
│   │       ├── products/
│   │       │   └── page.tsx          [CREAR] → Lista de productos con stock
│   │       └── orders/
│   │           ├── page.tsx          [CREAR] → Historial de órdenes
│   │           ├── inbound/
│   │           │   └── page.tsx      [CREAR] → Formulario de entrada
│   │           └── outbound/
│   │               └── page.tsx      [CREAR] → Formulario de salida
│   └── globals.css                   [MODIFICAR] si es necesario
├── components/
│   ├── login-form.tsx                [CREAR] → Formulario de login (desde auth-frontend)
│   ├── navbar-auth.tsx               [CREAR] → Navbar con auth (desde auth-frontend)
│   └── inventory/
│       ├── ProductRow.tsx            [CREAR] → Fila de producto con indicador
│       ├── StockBadge.tsx            [CREAR] → Badge de nivel de stock
│       ├── OrderForm.tsx             [CREAR] → Formulario genérico de órdenes
│       └── ErrorBanner.tsx           [CREAR] → Banner de error visible
├── lib/
│   ├── api.ts                        [CREAR] → Cliente HTTP base con auth JWT
│   ├── auth-actions.ts               [CREAR] → Acciones de autenticación
│   └── inventory.ts                  [CREAR] → Módulo central de llamadas a /inventory
└── types/
    └── inventory.ts                  [CREAR] → Tipos TypeScript de inventario

services/inventory/
├── app/
│   ├── main.py                       [MODIFICAR] → Incluir nuevo router
│   └── routers/
│       ├── inventory.py              [MODIFICAR] → Añadir nuevos endpoints
│       └── backoffice.py             [CREAR] → Router para /inventory/*
├── alembic/
│   └── versions/
│       └── XXXX_add_user_uuid.py     [CREAR] → Migración para user_uuid
└── tests/
    └── test_backoffice.py            [CREAR] → Tests para nuevos endpoints
```

---

## 🔥 FASE 0 — Mergear y adaptar sistema de autenticación frontend

### Objetivo
Incorporar el sistema de login existente en `origin/feature/auth-frontend` al branch de trabajo actual, para que el backoffice tenga autenticación funcional.

### ¿Por qué FASE 0?
Todo el proyecto requiere rutas protegidas. Sin auth, no podemos probar ni desarrollar nada.

### Pasos

#### 0.1 Crear rama de trabajo
```bash
git checkout milestone-4
git checkout -b feature/inventory-backoffice
```

#### 0.2 Extraer archivos de auth desde `origin/feature/auth-frontend`
Los siguientes archivos existen en el remote y debemos incorporarlos:

| Archivo | Origen |
|---|---|
| `uis/backoffice/lib/api.ts` | `origin/feature/auth-frontend` |
| `uis/backoffice/lib/auth-actions.ts` | `origin/feature/auth-frontend` |
| `uis/backoffice/app/login/page.tsx` | `origin/feature/auth-frontend` |
| `uis/backoffice/components/login-form.tsx` | `origin/feature/auth-frontend` |
| `uis/backoffice/components/navbar-auth.tsx` | `origin/feature/auth-frontend` |

**Estrategia:** `git checkout origin/feature/auth-frontend -- uis/backoffice/lib/api.ts uis/backoffice/lib/auth-actions.ts uis/backoffice/app/login/page.tsx uis/backoffice/components/login-form.tsx uis/backoffice/components/navbar-auth.tsx`

#### 0.3 Adaptar `layout.tsx` para usar navbar-auth
- Reemplazar el `<header>` estático actual con `<NavbarAuth />`
- El componente `NavbarAuth` es `"use client"`, por lo que el layout seguirá siendo server component si envolvemos el navbar en un componente cliente separado
- **IMPORTANTE:** La solución de referencia dice "reuse the existing backoffice auth pattern" — estamos usando el mismo patrón

#### 0.4 Configurar variable de entorno
```bash
# uis/backoffice/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_INVENTORY_API_URL=http://localhost:8000
```

#### 0.5 Verificar
- ✅ Login page accesible en `/login`
- ✅ Formulario muestra error en credenciales inválidas
- ✅ Redirige a home tras login exitoso

---

## 🔧 FASE 1 — Nuevos endpoints backend `/inventory/*`

### Objetivo
Añadir 5 nuevos endpoints en el backend de FastAPI que cumplan exactamente con el REST contract esperado por el frontend.

### ¿Por qué no usar los endpoints existentes directamente?
El proyecto espera rutas específicas (`/inventory/products`, `/inventory/orders/inbound`, etc.). Aunque los datos son los mismos, las rutas y formatos de respuesta deben coincidir. Crearemos un **nuevo router** que mapee a la lógica CRUD existente.

### Pasos

#### 1.1 Crear `services/inventory/app/routers/backoffice.py`

Este router contendrá los 5 endpoints que espera el frontend:

```python
# routers/backoffice.py — Endpoints específicos para el backoffice UI
# Mapea al REST contract definido en el Hito 5 de 4Geeks.
# Cada endpoint llama al CRUD existente pero presenta los datos
# en el formato que espera el frontend.

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.crud.inventory import inventory
from app.crud.movement import movement as movement_crud
from app.models.inventory import Item
from app.models.movement import Movement

router = APIRouter(
    prefix="/inventory",
    tags=["Backoffice Inventory"],
)

# GET /inventory/products → Lista de productos con current_stock
# Equivalente a GET /api/v1/items/ pero con nombres de campo del contrato

# GET /inventory/products/{id} → Producto individual con current_stock

# POST /inventory/orders/inbound → Registrar entrada
# POST /inventory/orders/outbound → Registrar salida

# GET /inventory/orders → Lista todas las órdenes con product_name
```

**Detalles de implementación:**

##### `GET /inventory/products`
```python
@router.get("/products")
async def list_products(
    db: AsyncSession = Depends(get_db),
):
    """Lista todos los productos con current_stock para el backoffice."""
    items, total = await inventory.get_items(db=db, skip=0, limit=1000)
    return [
        {
            "id": item.id,
            "name": item.name,
            "sku": item.sku,
            "current_stock": item.quantity,  # El proyecto espera current_stock
            "category": item.category,
            "warehouse": item.warehouse,
            "price": float(item.price),
            "min_stock": item.min_stock,
            "is_active": item.is_active,
        }
        for item in items
    ]
```

##### `GET /inventory/products/{id}`
```python
@router.get("/products/{item_id}")
async def get_product(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    item = await inventory.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "id": item.id,
        "name": item.name,
        "sku": item.sku,
        "current_stock": item.quantity,
        "category": item.category,
        "warehouse": item.warehouse,
    }
```

##### `POST /inventory/orders/inbound`
```python
@router.post("/orders/inbound", status_code=201)
async def create_inbound_order(
    body: InboundOrderCreate,  # Schema nuevo
    db: AsyncSession = Depends(get_db),
):
    # Usa adjust_stock internamente con movement_type="inbound"
    ...
```

##### `POST /inventory/orders/outbound`
```python
@router.post("/orders/outbound", status_code=201)
async def create_outbound_order(
    body: OutboundOrderCreate,  # Schema nuevo
    db: AsyncSession = Depends(get_db),
):
    # Usa adjust_stock internamente con movement_type="outbound"
    # Si stock insuficiente → HTTP 400 con detail descriptivo
    ...
```

##### `GET /inventory/orders`
```python
@router.get("/orders")
async def list_orders(
    db: AsyncSession = Depends(get_db),
):
    # JOIN Movements con Items para obtener product_name
    query = (
        select(
            Movement.id,
            Movement.item_id,
            Item.name.label("product_name"),
            Movement.movement_type.label("order_type"),
            Movement.quantity,
            Movement.created_at,
            Movement.user_uuid,
        )
        .join(Item, Movement.item_id == Item.id)
        .order_by(Movement.created_at.desc())
    )
    result = await db.execute(query)
    return result.mappings().all()
```

#### 1.2 Crear schemas adicionales en `app/schemas/backoffice.py`

```python
from pydantic import BaseModel, Field

class InboundOrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    reason: str | None = None

class OutboundOrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    reason: str | None = None
```

#### 1.3 Añadir campo `user_uuid` al modelo Movement

El proyecto espera que cada orden tenga un `user_uuid`. Actualmente nuestro modelo `Movement` **no tiene este campo**.

**Tarea técnica:**
1. Añadir columna `user_uuid` a `Movement` model
2. Crear migración Alembic
3. Actualizar schemas de Movement
4. Aplicar migración en local y Supabase

```python
# En models/movement.py
user_uuid: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
```

#### 1.4 Registrar el router en `main.py`

```python
# En main.py
from app.routers.backoffice import router as backoffice_router
app.include_router(backoffice_router)
```

#### 1.5 Verificar
- ✅ `GET /inventory/products` devuelve productos con `current_stock`
- ✅ `POST /inventory/orders/inbound` crea movimiento y actualiza stock
- ✅ `POST /inventory/orders/outbound` crea movimiento, resta stock, valida suficiencia
- ✅ `POST /inventory/orders/outbound` con stock insuficiente → `{"detail": "Insufficient stock: requested 20, available 12"}`
- ✅ `GET /inventory/orders` devuelve historial con `product_name`, `order_type`, `user_uuid`
- ✅ Todos los endpoints requieren `Authorization: Bearer <token>`

---

## 🌐 FASE 2 — Frontend: Integración API y tipos

### Objetivo
Crear el módulo central de integración con la API de inventario y los tipos TypeScript, de modo que ningún componente haga `fetch` directamente.

### Pasos

#### 2.1 Crear `uis/backoffice/types/inventory.ts`

```typescript
// types/inventory.ts — Tipos del sistema de inventario para el backoffice
// Alineado con el REST contract de /inventory/* y vocabulario TrackFlow

export interface Product {
  id: number;
  name: string;
  sku: string;
  current_stock: number;
  category: string;
  warehouse: string;
  price: number;
  min_stock: number;
  is_active: boolean;
}

export interface Order {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  order_type: "inbound" | "outbound";
  created_at: string;
  user_uuid: string | null;
}

export interface InboundOrderInput {
  product_id: number;
  quantity: number;
  reason?: string;
}

export interface OutboundOrderInput {
  product_id: number;
  quantity: number;
  reason?: string;
}

export interface ApiError {
  detail?: string;
  message?: string;
}
```

#### 2.2 Crear `uis/backoffice/lib/inventory.ts`

```typescript
// lib/inventory.ts — Módulo central de llamadas a la API de inventario
// NO hacer fetch directamente en componentes. Usar siempre estas funciones.

import { getToken } from "./auth-actions";
import type { Product, Order, InboundOrderInput, OutboundOrderInput, ApiError } from "@/types/inventory";

const API_BASE = (process.env.NEXT_PUBLIC_INVENTORY_API_URL || "http://localhost:8000").replace(/\/$/, "");

async function inventoryFetch<T>(path: string, init?: RequestInit): Promise<T> {
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
      // keep statusText
    }
    throw new Error(message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const listProducts = () =>
  inventoryFetch<Product[]>("/inventory/products");

export const getProduct = (id: number) =>
  inventoryFetch<Product>(`/inventory/products/${id}`);

export const createInboundOrder = (body: InboundOrderInput) =>
  inventoryFetch<Order>("/inventory/orders/inbound", {
    method: "POST",
    body: JSON.stringify(body),
  });

export const createOutboundOrder = (body: OutboundOrderInput) =>
  inventoryFetch<Order>("/inventory/orders/outbound", {
    method: "POST",
    body: JSON.stringify(body),
  });

export const listOrders = () =>
  inventoryFetch<Order[]>("/inventory/orders");
```

### 2.3 Crear componentes visuales reutilizables

#### `components/inventory/StockBadge.tsx`
- Props: `currentStock: number`, `minStock: number`
- Lógica:
  - `currentStock === 0` → 🔴 "Sin stock" (rojo)
  - `currentStock <= minStock` → 🟡 "Stock bajo" (ámbar)
  - `currentStock > minStock` → 🟢 "En stock" (verde)
- Definir thresholds en comentario de código

#### `components/inventory/ProductRow.tsx`
- Muestra: SKU, nombre, categoría, almacén, precio, StockBadge
- Botones: "Entrada", "Salida" (link a formularios con `?product_id=X`)

#### `components/inventory/ErrorBanner.tsx`
- Props: `message: string | null`
- Renderiza error visible (no solo console.error)
- Clases: bg-red-50, border-red-200, text-red-700

#### `components/inventory/OrderForm.tsx`
- Props: `type: "inbound" | "outbound"`
- Renderiza selector de producto + campo cantidad
- Para outbound: muestra stock actual cuando selecciona producto
- Para outbound: warning si cantidad > stock disponible

---

## 📋 FASE 3 — Página de productos (`/backoffice/inventory/products`)

### Objetivo
Lista de todos los productos del inventario con indicadores visuales de stock.

### Checklist
- [ ] **Ruta:** `app/backoffice/inventory/products/page.tsx`
- [ ] **Datos:** `GET /inventory/products` al cargar (usar `listProducts()`)
- [ ] **Columnas:** SKU, nombre, categoría, almacén, current_stock, badge de nivel, acciones
- [ ] **Indicadores visuales:**
  - `current_stock <= 5` → 🔴 Bajo (rojo)
  - `current_stock <= 15` → 🟡 Medio (ámbar)
  - `current_stock > 15` → 🟢 Alto (verde)
- [ ] **Acciones por fila:** Botón "Entrada" → `/backoffice/inventory/orders/inbound?product_id=X`
  - Botón "Salida" → `/backoffice/inventory/orders/outbound?product_id=X`
- [ ] **Auth:** Redirigir a `/login` si no autenticado
- [ ] **Nombres de campo:** Usar vocabulario TrackFlow (Costo unitario USD, Almacén, etc.)

### Implementación
```typescript
// "use client" — necesita acceso a auth y estado
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listProducts } from "@/lib/inventory";
import { isAuthenticated } from "@/lib/auth-actions";
import { StockBadge } from "@/components/inventory/StockBadge";
// ...
```

---

## 📝 FASE 4 — Formulario de entrada (`/backoffice/inventory/orders/inbound`)

### Objetivo
Formulario para registrar una entrada de mercancía (inbound).

### Checklist
- [ ] **Ruta:** `app/backoffice/inventory/orders/inbound/page.tsx`
- [ ] **Selector de producto:** Lista desplegable con nombres (no raw IDs)
- [ ] **Pre-selección:** Si `?product_id=X` en URL, seleccionar automáticamente
- [ ] **Campo cantidad:** Número entero > 0
- [ ] **Campo opcional:** Razón/motivo
- [ ] **Submit:** `POST /inventory/orders/inbound`
- [ ] **Éxito:** Limpiar formulario + mostrar banner de confirmación verde
- [ ] **Error 400/500:** Mostrar mensaje de error de la API en un elemento visible (ErrorBanner)
- [ ] **Auth:** Redirigir a `/login` si no autenticado

---

## ⚠️ FASE 5 — Formulario de salida (`/backoffice/inventory/orders/outbound`)

### Objetivo
Formulario para registrar una salida/venta con validación de stock en tiempo real.

### Checklist
- [ ] **Ruta:** `app/backoffice/inventory/orders/outbound/page.tsx`
- [ ] **Selector de producto:** Similar a inbound, pero...
- [ ] **Stock reactivo:** Al seleccionar producto, llamar `GET /inventory/products/{id}` y mostrar `current_stock`
- [ ] **Advertencia client-side:** Si cantidad introducida > stock mostrado, mostrar warning cerca del campo cantidad (antes de submit)
- [ ] **Submit:** `POST /inventory/orders/outbound`
- [ ] **Error 400 (stock insuficiente):** Mostrar `detail` de la API inline junto al campo cantidad
- [ ] **Éxito:** Limpiar formulario + banner de confirmación
- [ ] **Auth:** Redirigir a `/login` si no autenticado

---

## 📊 FASE 6 — Historial de órdenes (`/backoffice/inventory/orders`)

### Objetivo
Página read-only que muestra todas las órdenes (entradas y salidas).

### Checklist
- [ ] **Ruta:** `app/backoffice/inventory/orders/page.tsx`
- [ ] **Datos:** `GET /inventory/orders` al cargar
- [ ] **Columnas:**
  - Nombre del producto
  - Cantidad
  - Tipo de orden (inbound/outbound) con distinción visual
  - Fecha de creación (formateada legible)
  - `user_uuid` del operador
- [ ] **Distinción visual inbound/outbound:**
  - Inbound → badge verde "Entrada" + icono +
  - Outbound → badge rojo "Salida" + icono -
- [ ] **Read-only:** Sin botones de editar o eliminar
- [ ] **Auth:** Redirigir a `/login` si no autenticado

---

## 🔒 FASE 7 — Route protection + verificación final

### Objetivo
Asegurar que las 4 páginas de inventario redirijan a login si no hay sesión.

### Estrategia (2 opciones)

**Opción A — Middleware (recomendada):**
```typescript
// middleware.ts en uis/backoffice/
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value 
    // o leer de header según cómo se almacene
  const { pathname } = request.nextUrl;
  
  const protectedPaths = [
    "/backoffice/inventory/products",
    "/backoffice/inventory/orders",
  ];
  
  const isProtected = protectedPaths.some(p => pathname.startsWith(p));
  
  if (isProtected && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  
  return NextResponse.next();
}
```

**Opción B — Client-side redirect en cada página:**
```typescript
useEffect(() => {
  if (!isAuthenticated()) {
    router.push("/login");
  }
}, []);
```

La solución de referencia dice "reuse the existing backoffice auth pattern". Si el auth existente usa localStorage para el token, el middleware no puede leerlo (es server-side). En ese caso, usar **Opción B** con un hook `useAuth` o un componente `AuthGuard` que envuelva las páginas.

### Verificación final (30/30 checklist)

| # | Check | Estado esperado |
|---|---|---|
| 1 | `lib/inventory.ts` existe — ningún fetch en páginas | ✅ |
| 2 | Todos los endpoints protegidos envían `Authorization` | ✅ |
| 3 | Products page carga datos y muestra `current_stock` | ✅ |
| 4 | Products page tiene indicadores visuales de stock | ✅ |
| 5 | Products page tiene botones por fila (Entrada/Salida) | ✅ |
| 6 | Inbound form se envía, confirma éxito y muestra errores | ✅ |
| 7 | Inbound form tiene selector de producto por nombre | ✅ |
| 8 | Outbound form muestra stock al seleccionar producto | ✅ |
| 9 | Outbound form avisa si cantidad > stock (client-side) | ✅ |
| 10 | Outbound 400 muestra error inline en cantidad | ✅ |
| 11 | Orders history lista todas las órdenes | ✅ |
| 12 | Orders tiene distinción inbound/outbound visual | ✅ |
| 13 | Orders muestra product_name, quantity, type, date, user_uuid | ✅ |
| 14 | Orders es read-only (sin editar/eliminar) | ✅ |
| 15 | Las 4 páginas redirigen a login si no autenticadas | ✅ |
| 16 | Nombres y etiquetas usan vocabulario TrackFlow | ✅ |
| 17 | `.env.local` en `.gitignore`, no commits de secrets | ✅ |
| A | Ruta protegida inbound redirect a login | ✅ |
| B | Ruta protegida outbound redirect a login | ✅ |
| C | Ruta protegida products redirect a login | ✅ |
| D | Ruta protegida orders redirect a login | ✅ |

---

## 🧪 Pruebas finales

### Backend
```bash
cd services/inventory
source .venv/bin/activate

# Test endpoints individuales
curl -s http://localhost:8000/inventory/products | python3 -m json.tool | head -20
curl -s -X POST http://localhost:8000/inventory/orders/inbound \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 10}' | python3 -m json.tool

# Test 400 outbound con stock insuficiente
curl -s -X POST http://localhost:8000/inventory/orders/outbound \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 999}' | python3 -m json.tool

# Verificar historial
curl -s http://localhost:8000/inventory/orders | python3 -m json.tool | head -30
```

### Frontend
```bash
cd uis/backoffice
npm run dev
# Abrir http://localhost:3000/login
# Probar:
# - Login con credenciales
# - Navegar a /backoffice/inventory/products (verifica redirect si no auth)
# - Crear entrada
# - Crear salida con stock insuficiente
# - Ver historial de órdenes
# - Verificar stock badge colores
```

### TypeScript
```bash
cd uis/backoffice
npx tsc --noEmit  # Verificar tipos
```

### Build
```bash
cd uis/backoffice
npm run build  # Verificar build sin errores
```

---

## 📎 Notas importantes

### Sobre AGENTS.md (Zonas Protegidas)
Las zonas protegidas son: `.github/`, `package.json`, `tsconfig.json`, `DESIGN.md`, `memory-bank/`, `uis/` (unless confirmed). Dado que el proyecto ES sobre `uis/backoffice/`, podemos modificarlo.

### Sobre la rama
- Trabajar en `feature/inventory-backoffice` (basada en `milestone-4`)
- Commit tras cada FASE completada
- Push final a `feature/inventory-backoffice`

### Sobre auth y endpoints
- Los endpoints `/inventory/products` NO requieren auth si estamos en desarrollo local y el auth service (`services/api/`) no está corriendo
- Para producción, se integrará con el sistema JWT
- El backend tiene `services/api/` que es un servicio diferente a `services/inventory/`. Para este hito, asumimos que la autenticación se maneja por separado y los endpoints de inventario pueden funcionar sin auth durante desarrollo

### Sobre .env.local
```bash
# uis/backoffice/.env.local — NO COMMITEAR
# En .gitignore para proteger secrets
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_INVENTORY_API_URL=http://localhost:8000
```

### Sobre la solución de referencia
La solución de referencia de 4Geeks está en:
https://github.com/4GeeksAcademy/ai-engineering-syllabus/blob/main/content/projects/ai-eng-inventory-management-backoffice/.learn/solution/README.md

Recomiendo leerla antes de empezar la implementación.