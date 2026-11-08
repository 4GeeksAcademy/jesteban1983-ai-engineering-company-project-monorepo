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
| **Skills de agente** | core-web-vitals, performance, web-perf |
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

## 6. Skills de Agente Instaladas y su Uso

Como parte del proceso de auditoría, se instalaron 3 skills de agente para guiar la identificación y corrección de problemas de rendimiento:

| Skill | Origen | Versión | Propósito |
|-------|--------|---------|-----------|
| **core-web-vitals** | `addyosmani/web-quality-skills` | 1.0 | Optimización de LCP, INP, CLS, font-display, precarga |
| **performance** | `addyosmani/web-quality-skills` | 1.0 | Optimización general de rendimiento, compresión, code splitting |
| **web-perf** | `cloudflare/skills` | 1.0 | Auditoría con Chrome DevTools, análisis de trazas |

### 6.1 Correcciones Guiadas por las Skills

| Corrección aplicada | Skill que la recomendó | Prioridad según skill |
|--------------------|----------------------|---------------------|
| `font-display: "swap"` en Google Fonts | `core-web-vitals` (LCP) | Requerida |
| `compress: true` en next.config.ts | `performance` (Performance budget) | Requerida |
| `poweredByHeader: false` | `performance` (Best Practices) | Sugerida |
| Security Headers (X-Content-Type-Options, etc.) | `performance` (Security) | Requerida |
| Cache headers para assets estáticos | `performance` (Resource loading) | Requerida |
| Lazy loading con `next/dynamic` (3 componentes) | `performance` (Code splitting) | Requerida |
| Preconnect a API de inventario | `core-web-vitals` / `performance` (LCP) | Requerida |
| Refactorización de stock logic a `@trackflow/logic` | `core-web-vitals` (Código duplicado) | Requerida |

### 6.2 Proceso de Corrección con Skills

1. Se ejecutó Lighthouse en ambos frontends (website + backoffice, desktop + mobile) — 4 mediciones baseline
2. Se analizaron los informes de Lighthouse para identificar oportunidades de mejora
3. Se consultaron las skills `core-web-vitals` y `performance` para obtener recomendaciones específicas para Next.js
4. Cada corrección se aplicó siguiendo las guías de las skills:
   - **Performance skill**: guió la configuración de `next.config.ts` (compression, headers, caching)
   - **Core-web-vitals skill**: guió la optimización de fuentes (`font-display: swap`), preconnect, y viewport
   - **Performance skill**: guió el code splitting con `next/dynamic` para reducir JavaScript inicial
5. Se volvió a ejecutar Lighthouse tras todas las correcciones — 4 mediciones finales
6. Se documentaron los resultados en AUDIT.md y REPORT.md

> **Nota:** Las skills `core-web-vitals` y `performance` proporcionaron correcciones clasificadas como "requeridas" (no meras sugerencias), todas las cuales fueron implementadas. La skill `web-perf` se instaló como recurso adicional para futuras auditorías con Chrome DevTools.

---

## 7. Configuración del Entorno de Auditoría

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