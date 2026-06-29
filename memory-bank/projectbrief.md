# Project Brief: TrackFlow Monorepo

## Objetivo del Negocio
Transformar manualmente la gestión logística de TrackFlow (Los Ángeles/Zaragoza) en un sistema digitalizado y automatizado para procesar >2,000 envíos/semana.

## Estado del Proyecto
Hito 4: Migración a estructura de monorepo, centralización de lógica de negocio y despliegue de interfaces duales (Website/Backoffice).

## Restricciones Técnicas
- **Stack:** Next.js 16+, TypeScript 5.1+, Tailwind CSS.
- **Arquitectura:** Feature-Sliced Design. La lógica vive en `packages/logic/`.
- **Integridad:** Prohibido duplicar lógica de negocio entre `website` y `backoffice`.