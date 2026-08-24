# Progress

- [x] Setup: Monorepo, Workspaces y configuracion TypeScript.
- [x] Logic: modulo `@trackflow/logic` centralizado en `packages/logic`.
- [x] Protocol: `AGENTS.md` con flujo obligatorio pre-commit y zonas protegidas.
- [x] Contexto: `CONTEXT.md` y `CONTEXT.es.md` alineados con TrackFlow.
- [x] Infra de agentes: `.agents/rules` y `.agents/skills` creados con alcance e inputs claros.
- [x] Website: ruta `/` migrada a web corporativa en componentes TypeScript reutilizables.
- [x] Backoffice: app interna con layout propio y vista inicial operativa.
- [x] Integracion Hito 2: script de pruebas de fuego reutilizable importado desde `packages/logic` y visible en UI.
- [x] Verificacion tecnica: `npm run type-check` y builds de `uis/website` + `uis/backoffice` sin errores.
- [x] Hito 4 incidencias: script Python CLI, API FastAPI y UI de backoffice para analisis y exportacion CSV con metricas validadas (100/95/5 y satisfaccion 3.06).
- [x] **[Performance Web Vitals]** Rama `feature/performance-web-vitals` creada y completada:
  - [x] Auditoría Lighthouse baseline (before): 4 mediciones (website/backoffice, desktop/mobile)
  - [x] Análisis de código duplicado (4 casos documentados en AUDIT.md)
  - [x] Refactorización: lógica de stock movida a `@trackflow/logic` (packages/logic/src/trackflow/stock.ts)
  - [x] Correcciones de rendimiento aplicadas: next.config.ts (compress, headers, cache), font-display swap, lazy loading (3 componentes), viewport, preconnect
  - [x] Segunda medición Lighthouse (after) con comparativa en REPORT.md
  - [x] Skills de agente instaladas (3): `core-web-vitals` (addyosmani), `performance` (addyosmani), `web-perf` (cloudflare/skills) — vía skills.sh
  - [x] Evidencia de uso de skills documentada en AUDIT.md (sección 6) y REPORT.md (sección 2.0)
  - [x] Resultados: Website Desktop 100, Website Mobile 97, Backoffice Desktop 100, Backoffice Mobile 98 - Mejoras en LCP (-0.2s), INP (-10ms), TBT (-10ms)

