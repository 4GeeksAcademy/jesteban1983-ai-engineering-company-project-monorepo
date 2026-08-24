# Skill: Core Web Vitals

## Descripción

Habilidad especializada en las métricas core de rendimiento web que Google considera esenciales para la experiencia del usuario: **LCP** (Largest Contentful Paint), **INP** (Interaction to Next Paint) y **CLS** (Cumulative Layout Shift).

## Cuándo usar

- Al auditar rendimiento de frontends con Lighthouse
- Al interpretar los resultados de cada categoría de rendimiento
- Al decidir qué optimización tiene mayor impacto en el score

## Métricas Core

### LCP — Largest Contentful Paint
- **Qué mide:** Tiempo hasta que el elemento más grande de la página (imagen, título, hero) se renderiza.
- **Thresholds:** Bueno < 1.2s | Mejorable < 2.5s | Malo > 2.5s
- **Optimizaciones:**
  - `font-display: swap`
  - Preconnect a orígenes críticos
  - Lazy loading solo para below-the-fold
  - Compresión (gzip/brotli)
  - Cache headers `immutable`
  - Optimizar/redimensionar imágenes del hero

### INP — Interaction to Next Paint
- **Qué mide:** Latencia máxima de las interacciones del usuario (clicks, taps, teclado).
- **Thresholds:** Bueno < 200ms | Mejorable < 500ms | Malo > 500ms
- **Optimizaciones:**
  - Reducir JavaScript en bundle inicial (code splitting)
  - Evitar main-thread blocking time
  - Eliminar polyfills legacy
  - Minimizar hidratación pesada de React

### CLS — Cumulative Layout Shift
- **Qué mide:** Cantidad de desplazamiento inesperado de elementos durante la carga.
- **Thresholds:** Bueno < 0.1 | Mejorable < 0.25 | Malo > 0.25
- **Optimizaciones:**
  - Reservar espacio para imágenes (`width`/`height` o `aspect-ratio`)
  - No inyectar contenido dinámico sobre elementos existentes
  - Usar skeletons con dimensiones fijas en lazy loading

## Métricas secundarias

| Métrica | Significado | Bueno |
|---------|-------------|-------|
| FCP | First Contentful Paint | < 1.8 s |
| TBT | Total Blocking Time | < 50 ms |
| TTI | Time to Interactive | < 2.5 s |
| Speed Index | Percepción de carga visual | < 3.4 s |

## Interpretación de scores de Lighthouse

| Score | Estado |
|-------|--------|
| 90-100 | Verde — Excelente |
| 50-89 | Naranja — Mejorable |
| 0-49 | Rojo — Pobre |

## Ejemplo de workflow

```bash
# 1. Medición baseline
node scripts/run-lighthouse.js http://localhost:3000 desktop website-desktop before

# 2. Después de optimizaciones
node scripts/run-lighthouse.js http://localhost:3000 desktop website-desktop after

# 3. Comparar métricas core en ambos JSONs
node scripts/extract-metrics.js
```