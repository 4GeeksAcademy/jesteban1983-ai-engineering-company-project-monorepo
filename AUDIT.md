# AUDIT.md — Auditoría de Rendimiento Frontend

## Proyecto: TrackFlow — Performance Web Vitals

---

## 1. Resumen de la Auditoría

| Aspecto | Detalle |
|---------|---------|
| **Fecha** | 2026-08-24 |
| **Rama** | `feature/performance-web-vitals` |
| **Frontends auditados** | Website (`:3000`), Backoffice (`:3002`) |
| **Herramientas** | Lighthouse 12.x, Puppeteer, Node.js |
| **Perfiles** | Desktop + Mobile (4 ejecuciones) |

---

## 2. Resultados Baseline (Antes)

### 2.1 Website — Home Page

| Métrica | Desktop | Mobile |
|---------|---------|--------|
| **Performance** | 100 | 98 |
| **Accessibility** | 100 | 100 |
| **Best Practices** | 100 | 100 |
| **SEO** | 100 | 100 |
| **LCP** | — | 2.3 s |
| **TBT** | — | 100 ms |
| **CLS** | — | 0 |
| **INP** | — | 150 ms |
| **TTFB** | — | 10 ms |

### 2.2 Backoffice — Dashboard

| Métrica | Desktop | Mobile |
|---------|---------|--------|
| **Performance** | 100 | 97 |
| **Accessibility** | 100 | 100 |
| **Best Practices** | 100 | 100 |
| **SEO** | 100 | 100 |
| **LCP** | — | 2.6 s |
| **TBT** | — | 40 ms |
| **CLS** | — | 0 |
| **INP** | — | 140 ms |
| **TTFB** | — | 0 ms |

### 2.3 Oportunidades detectadas por Lighthouse

| Oportunidad | Impacto | Afecta a |
|-------------|---------|----------|
| Reduce unused JavaScript | Alto | Website + Backoffice (Mobile) |
| Legacy JavaScript (polyfills) | Medio | Website + Backoffice |
| Render-blocking requests | Alto | Website + Backoffice |
| Mejorar LCP (2.3–2.6 s) | Medio | Ambos en Mobile |
| Mejorar INP (140–150 ms) | Medio | Ambos en Mobile |

---

## 3. Análisis de Código Duplicado

### 3.1 🔴 Caso 1: Lógica de Nivel de Stock (Stock Level Logic)

**Archivos involucrados:**
- `uis/backoffice/types/inventory.ts` — funciones `getStockLevel()`, `getStockLabel()`, `getStockColor()`, `getStockIcon()` + tipo `StockLevel`
- `uis/backoffice/components/inventory/StockBadge.tsx` — componente que usa estas funciones
- `uis/website/components/ProductCatalog.tsx` — renderiza productos pero NO tiene lógica de stock, la duplicaría si la necesitara

**Root cause:**
La lógica de negocio para determinar niveles de stock (umbrales basados en `min_stock`) está implementada directamente en un archivo de tipos del backoffice (`types/inventory.ts`). No existe en un lugar compartido. El website no tiene esta lógica porque usa campos diferentes (`stockQuantity`, `minStockThreshold` del paquete `@trackflow/logic`), pero si en el futuro necesitara mostrar badges de stock, tendría que reimplementarla.

**Solución:**
Mover las funciones `getStockLevel()`, `getStockLabel()`, `getStockColor()` y el tipo `StockLevel` al paquete `@trackflow/logic` como lógica de dominio reutilizable. El `StockBadge` puede mantenerse en cada app como componente UI, pero importando la lógica desde el paquete compartido.

### 3.2 🟡 Caso 2: Modelo de Producto Triplicado

**Archivos involucrados:**
- `packages/logic/src/trackflow/contracts.ts` — interface `Product` (con `stockQuantity`, `minStockThreshold`, `unitCostUSD`)
- `uis/backoffice/types/inventory.ts` — interface `Product` (con `current_stock`, `min_stock`, `price`)
- `uis/website/lib/inventory-api.ts` — interface `ApiItem` (con `quantity`, `min_stock`, `price`)

**Root cause:**
Cada capa del sistema modela el mismo concepto (producto de inventario) con una interfaz diferente:
- El paquete de lógica usa vocabulario de dominio (`stockQuantity`, `minStockThreshold`)
- La API de inventario devuelve snake_case (`current_stock`, `min_stock`)
- El website tiene un adaptador `apiItemToProduct()` que convierte entre ambos

**Solución:**
Crear un adaptador unificado en `@trackflow/logic` que todas las apps puedan usar, y consolidar las interfaces con tipos utilitarios (`Pick`, `Omit`) para vistas específicas.

### 3.3 🟡 Caso 3: Wrappers de Fetch Duplicados (Backoffice)

**Archivos involucrados:**
- `uis/backoffice/lib/api.ts` — `authHeaders()`, `apiGet()`, `apiPost()`, `apiPut()`
- `uis/backoffice/lib/inventory.ts` — `inventoryFetch<T>()` (hace lo mismo que api.ts)

**Root cause:**
Dos implementaciones independientes de fetch con autenticación Bearer token en el mismo proyecto. `api.ts` se usa para auth/general, mientras que `inventory.ts` tiene su propio wrapper para inventario. Hacen exactamente lo mismo (leer token de localStorage, añadir header, fetch, manejar errores).

**Solución:**
Consolidar en un solo wrapper genérico en `lib/api.ts` y reutilizarlo desde `lib/inventory.ts`.

### 3.4 🟢 Caso 4: Configuración Next.js Duplicada

**Archivos involucrados:**
- `uis/website/next.config.ts` y `uis/backoffice/next.config.ts` — idénticos

**Root cause:**
Boilerplate generado por `create-next-app` sin personalización.

**Solución:**
Mantener así por ahora, pero documentar para futura consolidación.

---

## 4. Métricas de Código Duplicado

| Caso | Líneas duplicadas | Severidad | Solución propuesta |
|------|-------------------|-----------|-------------------|
| Stock logic | ~40 líneas | 🔴 Alta | Mover a `@trackflow/logic` |
| Product model | ~60 líneas | 🟡 Media | Consolidar interfaces |
| Fetch wrappers | ~35 líneas | 🟡 Media | Unificar en `lib/api.ts` |
| next.config.ts | ~15 líneas | 🟢 Baja | Mantener |

---

## 5. Plan de Correcciones

### Priorización (basada en impacto real en KPIs)

| Prioridad | Corrección | KPI objetivo | Esfuerzo |
|-----------|-----------|-------------|----------|
| 1 | Mover lógica de stock a `@trackflow/logic` | — (refactor) | Bajo |
| 2 | Extraer componente StockBadge reutilizable | — (refactor) | Bajo |
| 3 | Reducir JavaScript no usado (code splitting) | LCP, TBT | Medio |
| 4 | Eliminar polyfills legacy (moderno-browser target) | TBT, INP | Bajo |
| 5 | Mejorar LCP (precarga, optimización imágenes) | LCP | Medio |
| 6 | Desbloquear render-blocking CSS | LCP, FCP | Bajo |
| 7 | Consolidar Product model en `@trackflow/logic` | — (refactor) | Alto |

---

## 6. Configuración del Entorno de Auditoría

```bash
# Herramientas instaladas
lighthouse@^12.x          # CLI y API Node.js
puppeteer@^24.x           # Chromium headless automation

# Script de auditoría
scripts/run-lighthouse.js  # Script Node.js que une Puppeteer + Lighthouse
```

### Ejecución de mediciones

```bash
# Website
node scripts/run-lighthouse.js http://localhost:3000 desktop website-home-desktop
node scripts/run-lighthouse.js http://localhost:3000 mobile website-home-mobile

# Backoffice
node scripts/run-lighthouse.js http://localhost:3002 desktop backoffice-dashboard-desktop
node scripts/run-lighthouse.js http://localhost:3002 mobile backoffice-dashboard-mobile
```

---

*Auditoría generada como parte del proyecto "Auditoría de Rendimiento Frontend" — 4Geeks Academy, Módulo Architecture Optimization.*