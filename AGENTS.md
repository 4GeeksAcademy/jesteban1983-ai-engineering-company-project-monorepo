# AGENTS.md — Protocolo de Desarrollo TrackFlow

Este documento define las reglas de operación para cualquier agente de IA o ingeniero que trabaje en el repositorio.

## 1. Reglas de Lectura Inicial
Antes de realizar cualquier tarea, el agente debe leer:
- `memory-bank/projectbrief.md` (Contexto del negocio)
- `memory-bank/techContext.md` (Restricciones técnicas)
- `packages/logic/src/trackflow/contracts.ts` (Definiciones de datos)

## 2. Flujo Obligatorio antes de cada COMMIT
Todo cambio debe validar este flujo de 4 pasos ordenados:

1. **Paso 1 (Integridad de Tipos):** Ejecutar `npm run type-check`. Si hay errores de TS, no se puede proceder.
2. **Paso 2 (Auditoría de Contexto):** Verificar que el cambio no viole las reglas definidas en `.agents/rules/`.
3. **Paso 3 (Validación de Aceptación):** Confirmar que la tarea cumple con los criterios documentados en la *skill* aplicada.
4. **Paso 4 (Formateo y Commit):** Ejecutar `npm run lint` y realizar el commit usando formato *Conventional Commits* (ej: `feat: [Hito4] integrar lógica de inventario`).

## 3. Zonas Protegidas
El agente **no debe modificar** los siguientes archivos sin confirmación explícita:
- `.github/`
- `package.json` (raíz)
- Cualquier archivo en `memory-bank/` sin haber discutido el cambio con el humano.