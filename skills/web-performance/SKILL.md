# Skill: Web Performance Audit

## Descripción

Este skill define el proceso sistemático para auditar, medir y mejorar el rendimiento de aplicaciones web frontend, con foco en las Web Vitals de Google (LCP, INP, CLS, TBT, FCP).

## Cuándo usar

- Cuando se necesita auditar el rendimiento de un frontend
- Cuando hay que medir y comparar métricas de Web Vitals antes/después de cambios
- Cuando se requiere identificar cuellos de botella de rendimiento (JS pesado, render-blocking, imágenes)
- Cuando el proyecto exige cumplir el estándar de Lighthouse ≥ 90

## Herramientas

- **Lighthouse** (v12+): Auditoría automatizada de rendimiento, accesibilidad, mejores prácticas y SEO
- **Puppeteer** (v24+): Control de Chromium headless para ejecutar Lighthouse programáticamente
- **Next.js** `next/dynamic`: Lazy loading de componentes
- **font-display: swap**: Eliminación de FOIT

## Proceso recomendado

### Fase 1: Baseline (medición inicial)
1. Levantar todos los frontends (dev server)
2. Ejecutar Lighthouse en todos los perfiles (desktop + mobile)
3. Guardar resultados JSON/HTML como baseline en `audit/before/`
4. Documentar hallazgos en `AUDIT.md`

### Fase 2: Análisis de código
1. Identificar código duplicado entre los frontends
2. Detectar lógica de negocio fuera de `packages/logic/`
3. Documentar oportunidades de refactorización
4. Clasificar por severidad y prioridad

### Fase 3: Correcciones
1. **Configuración Next.js:**
   - `compress: true`
   - `poweredByHeader: false`
   - `reactStrictMode: true`
   - Security headers
   - Cache headers para assets estáticos
2. **Fuentes:**
   - `display: "swap"` para evitar FOIT
   - Preconnect a APIs
3. **Lazy loading:**
   - `next/dynamic` para componentes below-the-fold
4. **Refactorización:**
   - Mover lógica de negocio a `packages/logic/`
   - Consolidar wrappers de fetch

### Fase 4: Segunda medición (after)
1. Re-ejecutar Lighthouse en los mismos perfiles
2. Guardar en `audit/after/`
3. Comparar con baseline y documentar en `REPORT.md`

## Métricas objetivo (Core Web Vitals)

| Métrica | Bueno | Mejorable | Malo |
|---------|-------|-----------|------|
| LCP | < 1.2 s | < 2.5 s | > 2.5 s |
| INP | < 200 ms | < 500 ms | > 500 ms |
| CLS | < 0.1 | < 0.25 | > 0.25 |
| TBT | < 50 ms | < 200 ms | > 200 ms |
| FCP | < 1.8 s | < 3.0 s | > 3.0 s |

## Entregables

- `AUDIT.md` — Hallazgos, análisis de duplicación, plan de correcciones
- `REPORT.md` — Comparativa before/after, impacto de correcciones
- `audit/before/` + `audit/after/` — JSON + HTML de cada medición
- Scripts reutilizables en `scripts/`