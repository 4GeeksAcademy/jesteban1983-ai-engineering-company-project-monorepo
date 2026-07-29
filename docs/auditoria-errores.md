# Reporte de Auditoría — Gestión de Errores

**Proyecto:** Gestión de Errores (ai-eng-error-handling)
**Rama:** error-handling-audit
**Fecha:** 2026-07-29

## Hallazgos

| Archivo | Línea | Cat | Problema | Corrección |
|---------|-------|-----|----------|------------|
| services/api/main.py | 6-7 | 4 | `import traceback` + `traceback.print_exc()` expone stack traces en consola | Reemplazar por logger.exception() |
| services/api/main.py | 76 | 5 | `print(f"[ERROR]...{exc}")` expone detalles de excepción en stdout | Reemplazar por logger.exception() |
| services/api/main.py | 46-78 | 3 | Manejador global usa print+print_exc, no logging estructurado | Usar logger.exception + ErrorResponse schema |
| services/api/routes/incidents.py | 117 | 1 | `create_incident` sin try/except — fallo de DB expone traceback | Añadir try/except acotado |
| services/api/routes/incidents.py | 163 | 1 | `list_incidents` sin try/except — error de DB se propaga sin control | Añadir try/except acotado |
| services/api/routes/incidents.py | 210 | 1 | `get_incident` sin try/except | Añadir try/except acotado |
| services/api/routes/incidents.py | 263 | 1 | `update_incident_status` sin try/except | Añadir try/except acotado |
| services/api/routes/auth.py | 98 | 6 | `login` sin try/except en búsqueda de usuario | Añadir try/except acotado |
| services/api/routes/auth.py | 141 | 1 | `forgot-password` sin try/except en generación de token/envío email | Añadir try/except acotado |
| services/api/routes/auth.py | 176 | 1 | `reset-password` sin try/except en actualización de DB | Añadir try/except acotado |
| services/api/routes/auth.py | 223 | 1 | `change-password` sin try/except en actualización | Añadir try/except acotado |
| services/api/routes/suppliers.py | 74 | 1 | `create_supplier` sin try/except en inserción DB | Añadir try/except acotado |
| services/api/routes/suppliers.py | 100 | 1 | `list_suppliers` sin try/except en filtros | Añadir try/except acotado |
| services/api/routes/suppliers.py | 130 | 1 | `get_supplier`, `update_rate`, status, delete sin try/except | Añadir try/except acotado |
| services/api/routes/profiles.py | 35 | 1 | `get_my_profile`, `update_my_profile` sin try/except | Añadir try/except acotado |
| services/api/routes/users.py | 48 | 1 | `register_user` sin try/except en creación | Añadir try/except acotado |
| uis/backoffice/lib/api.ts | 74 | 4 | `throw { status, detail }` expone códigos HTTP al componente | Usar Error con mensaje legible |
| uis/backoffice/lib/api.ts | 100 | 4 | Mismo patrón en apiPost | Usar Error con mensaje legible |
| uis/backoffice/lib/api.ts | 127 | 4 | Mismo patrón en apiPut | Usar Error con mensaje legible |
| uis/backoffice/lib/api.ts | 154 | 4 | Mismo patrón en apiPatch | Usar Error con mensaje legible |
| uis/backoffice/components/incident-list.tsx | 90 | 6 | Manejo de error con casteo `err: any` + acceso a `.detail` | Usar mensaje legible |
| scripts/seed_incidents.py | 42 | 1 | `load_csv` sin try/except en open() | Añadir try/except con stderr |
| scripts/seed_incidents.py | 28 | 8 | Script no usa sys.exit(1) en errores críticos | Añadir sys.exit(1) |
| scripts/seed_incidents.py | 50 | 3 | `continue` silencioso en errores de fila sin stderr | Escribir errores a stderr |
| scripts/analyze.py | 96 | 1 | `_export_results` sin try/except en escritura de archivo | Añadir try/except |
| scripts/analyze.py | 118 | 3 | `print(f"Error: {exc}")` en stdout en vez de stderr | Usar stderr |
| scripts/analyze.py | 103-124 | 8 | `main()` usa `return 1` pero `SystemExit(main())` no garantiza código de salida | Usar sys.exit explícito |

## Plan de corrección

1. **Fase 2 — Backend:** Crear `schemas/error.py` + `core/errors.py`
2. **Fase 3 — Backend:** Reemplazar exception handlers en main.py con ErrorResponse
3. **Fase 4 — Backend:** Añadir try/except acotados en todos los routes
4. **Fase 5 — Frontend:** Crear `useAsync` hook + `AsyncView` component
5. **Fase 6 — Frontend:** Optional chaining (?. y ??) en componentes
6. **Fase 7 — Frontend:** finally en formularios
7. **Fase 8 — Scripts:** try/except, sys.exit(1), stderr
8. **Fase 9 — General:** Eliminar console.error/print con datos sensibles
9. **Fase 10 — Verificación:** Tests, build, arranque
10. **Fase 11 — Commit+PR**