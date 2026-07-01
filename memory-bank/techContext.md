# Tech Context

**Stack:**
- Monorepo: NPM Workspaces.
- Frontend: Next.js 15 (App Router) + TypeScript + Tailwind CSS.
- Core Logic: Paquete privado `@trackflow/logic` (TypeScript puro).
- Alias: `@trackflow/logic/*` apunta a `packages/logic/src/*`.

**Reglas de Arquitectura:**
- La lógica de negocio vive exclusivamente en `packages/logic/`.
- La UI (Next.js) es solo una capa de presentación.
- No se permiten importaciones circulares.