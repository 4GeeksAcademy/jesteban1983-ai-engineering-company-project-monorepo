
 
> **Proyecto 4Geeks:** Gestión de Errores / Error Handling
> **Slug:** `ai-eng-error-handling`
> **Asset ID:** `3573`
> **Módulo:** Error handling, debugging and testing
> **Empresa:** TrackFlow (monorepo fork)
> **Rama:** `error-handling-audit`
>
> ⚠️ **Este documento es la especificación ejecutable para el agente.**
> El agente NO debe tomar decisiones propias. NO debe alucinar archivos, funciones, imports o rutas que no existan en el monorepo.
> Cada bloque YAML y JSON es un mandato exacto. Si algo no está especificado → PREGUNTAR.

---

## 📋 Índice

1. [Reglas absolutas del agente](#1-reglas-absolutas-del-agente)
2. [Contexto del proyecto](#2-contexto-del-proyecto)
3. [Stack técnico exacto](#3-stack-técnico-exacto)
4. [Auditoría inicial con IA](#4-auditoría-inicial-con-ia)
5. [Estructura del monorepo](#5-estructura-del-monorepo)
6. [Fase 0 — Preparación](#6-fase-0--preparación)
7. [Fase 1 — Auditoría automatizada con el agente](#7-fase-1--auditoría-automatizada-con-el-agente)
8. [Fase 2 — Backend: Errores estructurados en FastAPI](#8-fase-2--backend-errores-estructurados-en-fastapi)
9. [Fase 3 — Backend: Manejador global de excepciones](#9-fase-3--backend-manejador-global-de-excepciones)
10. [Fase 4 — Backend: Endpoints individuales con errores acotados](#10-fase-4--backend-endpoints-individuales-con-errores-acotados)
11. [Fase 5 — Frontend: Patrón de tres estados (loading/success/error)](#11-fase-5--frontend-patrón-de-tres-estados-loadingsuccesserror)
12. [Fase 6 — Frontend: Optional chaining y fallbacks](#12-fase-6--frontend-optional-chaining-y-fallbacks)
13. [Fase 7 — Frontend: Formularios con finally y estados seguros](#13-fase-7--frontend-formularios-con-finally-y-estados-seguros)
14. [Fase 8 — Scripts: Manejo de errores en I/O y sys.exit](#14-fase-8--scripts-manejo-de-errores-en-io-y-sysexit)
15. [Fase 9 — General: console.error y datos sensibles](#15-fase-9--general-consoleerror-y-datos-sensibles)
16. [Fase 10 — Verificación y validación](#16-fase-10--verificación-y-validación)
17. [Fase 11 — Commit, push y PR](#17-fase-11--commit-push-y-pr)
18. [Checklist de evaluación 4Geeks](#18-checklist-de-evaluación-4geeks)
19. [Orden de ejecución](#19-orden-de-ejecución)

---

## 1. Reglas absolutas del agente

```yaml
reglas:
  - id: R01; texto: "NO tomar decisiones propias."
  - id: R02; texto: "NO introducir nuevas funcionalidades. Solo gestión de errores."
  - id: R03; texto: "NO refactorizar código no relacionado con errores."
  - id: R04; texto: "NO inventar archivos, funciones o rutas. Leer los reales."
  - id: R05; texto: "Trabajar DENTRO del monorepo, rama error-handling-audit."
  - id: R06; texto: "Cada operación asíncrona en frontend: 3 estados (loading/success/error)."
  - id: R07; texto: "NUNCA exponer stack traces, códigos HTTP o parseo JSON al usuario."
  - id: R08; texto: "Cada error DEBE incluir llamada a la acción (reintentar/volver/soporte)."
  - id: R09; texto: "try/catch acotados a operaciones específicas, NO envolver funciones."
  - id: R10; texto: "finally DEBE limpiar estado de carga (isLoading = false)."
  - id: R11; texto: "Scripts: sys.exit(1) en error crítico, mensajes en stderr."
  - id: R12; texto: "NO exponer datos sensibles (conexiones, rutas, secretos) en errores."
  - id: R13; texto: "Usar optional chaining (?.) y fallbacks (??) en propiedades anidadas."
  - id: R14; texto: "Manejador global de excepciones: JSON estructurado, NUNCA traceback."
  - id: R15; texto: "REVISAR console.error/print con datos sensibles y ELIMINARLOS."
  - id: R16; texto: "logger.exception en servidor; mensaje genérico al cliente."
```

## 2. Contexto del proyecto

```yaml
situacion:
  que_paso: "El sistema no tiene estrategia coherente de gestión de errores"
  impacto: "APIs fallan en silencio, faltan estados de carga, usuarios ven mensajes crudos, scripts se rompen sin rastro"
  consecuencia: "Tech lead exige corrección transversal antes del siguiente hito"

requisitos_tech_lead:
  - "Ningún error debe romper la app ni dejar al usuario en estado indefinido"
  - "Toda operación asíncrona del frontend: 3 estados (cargando, éxito, error)"
  - "Mensajes de error legibles — nunca stack trace, código HTTP o parseo JSON"
  - "Todo error debe ofrecer salida: reintentar, volver a inicio, o contactar soporte"
  - "Excepciones capturadas en ámbito correcto — no un único try/catch gigante"
  - "Nunca exponer datos sensibles en errores al cliente"

capas:
  frontend:
    tecnologia: "Next.js 14+ / TypeScript"
    directorio: "uis/backoffice/"
    problemas: ["FALTAN try/catch", "FALTAN estados loading/error", "MENSAJES CRUDOS", "SIN salida al usuario", "SIN optional chaining", "SIN finally"]
  backend:
    tecnologia: "Python 3.10+ / FastAPI"
    directorio: "services/api/"
    problemas: ["try/except DEMASIADO AMPLIO", "Stack traces crudos en HTTP", "DATOS SENSIBLES expuestos", "Falta manejo APIs externas"]
  scripts:
    tecnologia: "Python"
    directorio: "scripts/ o packages/"
    problemas: ["FALTAN try/except en I/O", "SIN sys.exit(1)", "Errores en stdout en vez de stderr"]
```

## 3. Stack técnico exacto

```yaml
frontend:
  framework: "Next.js 14+ (App Router)"
  lenguaje: "TypeScript"
  ui: "Tailwind CSS + componentes React"
  directorio: "uis/backoffice/"
  auth: "localStorage (access_token) + middleware.ts"

backend:
  framework: "FastAPI 0.111+"
  lenguaje: "Python 3.10+"
  base_datos: "TinyDB"
  auth: "python-jose[cryptography] + passlib[bcrypt]"
  directorio: "services/api/"

scripts:
  lenguaje: "Python 3.10+"
  directorio: "scripts/ o packages/"

gestor_dependencias: "uv (para backend)"

comandos_base:
  ejecutar_backend: "cd services/api && uvicorn app.main:app --reload"
  ejecutar_frontend: "cd uis/backoffice && npm run dev"
  tests: "cd services/api && uv run pytest"
```

## 4. Auditoría inicial con IA — Prompt para el agente

> **CRÍTICO:** Antes de modificar cualquier archivo, el agente DEBE escanear todo el monorepo.

```
Eres un ingeniero de software senior auditando un repositorio en busca de
problemas en la gestión de errores.

Analiza TODO el repositorio.
Por cada archivo, identifica y reporta:

1. TRY/CATCH AUSENTE — operaciones asíncronas sin manejo de errores.
2. CATCH DEMASIADO AMPLIO — try/catch envolviendo funciones enteras.
3. FALLOS SILENCIOSOS — catch vacío, except: pass.
4. EXPOSICIÓN DE ERRORES CRUDOS — stack traces, códigos HTTP al usuario.
5. FILTRACIÓN DE DATOS SENSIBLES — secretos, rutas, conexiones en errores.
6. ESTADOS DE CARGA/ERROR AUSENTES EN UI — componentes que se rompen al fallar.
7. SIN LLAMADA A LA ACCIÓN — error sin reintentar/volver/soporte.
8. SIN sys.exit EN FALLOS DE SCRIPT — scripts que fallan pero salen con código 0.

Por cada hallazgo:
- Ruta del archivo y línea
- Categoría (1-8)
- Descripción del problema
- Corrección sugerida

Prioriza: CRÍTICO > ALTO > MEDIO > BAJO.
```


## 5. Estructura del monorepo

> El agente DEBE verificar con `ls` y `find` los archivos reales antes de modificarlos.

```yaml
directorios_esperados:
  frontend: "uis/backoffice/"
  backend: "services/api/"
  scripts: "scripts/ o packages/"
  docs: "docs/"
```

## 6. Fase 0 — Preparacion

```bash
# Crear rama
git checkout -b error-handling-audit

# Explorar estructura
find uis/ -name "*.ts" -o -name "*.tsx"
find services/api/ -name "*.py"
find scripts/ -name "*.py"
find packages/ -name "*.py" 2>/dev/null

# Leer archivos clave
cat services/api/app/main.py
cat services/api/app/routes/auth.py
cat services/api/app/core/security.py
cat uis/backoffice/lib/api.ts
cat uis/backoffice/lib/auth-actions.ts
cat uis/backoffice/middleware.ts
ls scripts/
```

## 7. Fase 1 — Auditoria automatizada

> NO modificar archivos. Solo generar el reporte.

### 7.1 Ejecutar el prompt de auditoria (seccion 4) en el agente

### 7.2 Guardar reporte en docs/auditoria-errores.md

```bash
cat > docs/auditoria-errores.md << 'EOF'
# Reporte de Auditoria - Gestion de Errores

Proyecto: Gestion de Errores (ai-eng-error-handling)
Rama: error-handling-audit

## Hallazgos

| Archivo | Linea | Cat | Problema | Correccion |
|---------|-------|-----|----------|------------|
| (rellenar tras escaneo) | ... | ... | ... | ... |

## Plan de correccion
1. Backend: errores estructurados
2. Frontend: tres estados + mensajes legibles
3. Scripts: sys.exit + stderr
EOF
```

## 8. Fase 2 — Backend: Esquemas de error Pydantic

### 8.1 Crear services/api/app/schemas/error.py

```python
"""Esquemas Pydantic para respuestas de error estructuradas."""

from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Respuesta de error estandar. NUNCA contiene tracebacks."""
    detail: str
    error_code: Optional[str] = None
    status_code: int = 500


class ValidationErrorDetail(BaseModel):
    """Error de validacion a nivel de campo."""
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    """Error de validacion con detalles por campo."""
    detail: str = "Datos invalidos. Revisa los campos marcados."
    errors: list[ValidationErrorDetail] = []
    status_code: int = 422
```

### 8.2 Crear services/api/app/core/errors.py

```python
"""Utilidades para gestion de errores en FastAPI."""

import logging
from fastapi import HTTPException
from app.schemas.error import ErrorResponse

logger = logging.getLogger("trackflow")


def safe_error(status_code: int, message: str, error_code: str = None) -> HTTPException:
    """HTTPException con mensaje seguro (sin tracebacks)."""
    detail = ErrorResponse(
        detail=message,
        error_code=error_code,
        status_code=status_code,
    ).model_dump()
    return HTTPException(status_code=status_code, detail=detail)


def log_and_raise(
    status_code: int, user_message: str,
    error_code: str = None, exc_info: Exception = None,
) -> HTTPException:
    """Registra error en servidor y lanza excepcion segura al cliente."""
    if exc_info:
        logger.exception("Error %s (%s): %s", status_code, error_code or "unk", user_message, exc_info=exc_info)
    else:
        logger.error("Error %s (%s): %s", status_code, error_code or "unk", user_message)
    return safe_error(status_code, user_message, error_code)
```

## 9. Fase 3 — Backend: Manejador global de excepciones

### Modificar services/api/app/main.py

ANADIR al final, antes de if __name__:

```python
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.schemas.error import ErrorResponse

logger = logging.getLogger("trackflow")

# Configurar logging (cerca del inicio)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura cualquier excepcion no manejada. Devuelve JSON seguro."""
    logger.exception("Excepcion no capturada en %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Error interno del servidor. Intenta de nuevo.", error_code="INTERNAL_ERROR", status_code=500).model_dump(),
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """ValueError -> 400."""
    logger.warning("ValueError en %s %s: %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(detail="Solicitud invalida.", error_code="INVALID_REQUEST", status_code=400).model_dump(),
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """404 -> JSON."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(detail="Recurso no encontrado.", error_code="NOT_FOUND", status_code=404).model_dump(),
    )
```

## 10. Fase 4 — Backend: Endpoints con errores acotados

### 10.1 Patron para cada endpoint

```python
# try/except ACOTADO a la operacion especifica
@router.get("/suppliers/{supplier_id}")
def get_supplier(supplier_id: str, db=Depends(get_db)):
    if not supplier_id or not supplier_id.strip():
        raise safe_error(400, "ID de proveedor obligatorio.")
    try:
        supplier = supplier_service.get_by_id(db, supplier_id)
    except DatabaseUnavailable:
        raise safe_error(503, "Servicio temporalmente no disponible.")
    except Exception as exc:
        logger.exception("Error al buscar proveedor %s", supplier_id)
        raise safe_error(500, "Error interno. Intenta de nuevo.")
    if supplier is None:
        raise safe_error(404, "Proveedor no encontrado.")
    return supplier
```

### 10.2 Endpoints de autenticacion

APLICAR el mismo patron a routes/auth.py:

- register: try/except separados para busqueda de duplicado y creacion
- login: try/except especifico para busqueda, mensaje generico "Credenciales invalidas"
- profile/me: validar current_user, si None -> 401
- forgot-password: try/except para busqueda, SIEMPRE 200
- reset-password: try/except para busqueda de usuario y actualizacion
- change-password: try/except para verificacion y actualizacion

## 11. Fase 5 — Frontend: Patron de tres estados

### 11.1 Hook useAsync

Crear `uis/backoffice/lib/use-async.ts`:

```typescript
import { useState, useCallback } from "react";

type AsyncState<T> = { data: T | null; isLoading: boolean; error: string | null };
type UseAsyncReturn<T> = AsyncState<T> & { execute: (...args: unknown[]) => Promise<T | undefined> };

export function useAsync<T>(asyncFn: (...args: unknown[]) => Promise<T>): UseAsyncReturn<T> {
  const [state, setState] = useState<AsyncState<T>>({ data: null, isLoading: false, error: null });

  const execute = useCallback(async (...args: unknown[]): Promise<T | undefined> => {
    setState({ data: null, isLoading: true, error: null });
    try {
      const result = await asyncFn(...args);
      setState({ data: result, isLoading: false, error: null });
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Algo salio mal. Intenta de nuevo.";
      setState({ data: null, isLoading: false, error: message });
      return undefined;
    }
  }, [asyncFn]);

  return { ...state, execute };
}
```

### 11.2 Componente AsyncView

Crear `uis/backoffice/components/AsyncView.tsx`:

```typescript
// Renderiza automaticamente: cargando, error, datos o vacio

interface AsyncViewProps<T> {
  isLoading: boolean;
  error: string | null;
  data: T | null;
  onRetry?: () => void;
  loadingMessage?: string;
  children: (data: T) => React.ReactNode;
}

export function AsyncView<T>({
  isLoading, error, data, onRetry,
  loadingMessage = "Cargando...", children,
}: AsyncViewProps<T>) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-gray-500">{loadingMessage}</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-800 font-medium mb-2">Algo salio mal</p>
        <p className="text-red-600 text-sm mb-4">{error}</p>
        {onRetry && (
          <button onClick={onRetry} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition">
            Intentar de nuevo
          </button>
        )}
        <a href="/" className="text-blue-600 text-sm hover:underline block mt-2">Volver al inicio</a>
      </div>
    );
  }
  if (!data) {
    return <div className="text-center p-8 text-gray-400">No hay datos disponibles.</div>;
  }
  return <>{children(data)}</>;
}
```

### 11.3 Aplicar a componentes existentes

Para CADA componente/pagina que hace fetch:

- Importar `useAsync` y `AsyncView`
- Reemplazar `useState + useEffect` por `useAsync`
- Reemplazar render por `<AsyncView isLoading error data onRetry={execute}>`
- Anadir finally: setLoading(false) (ya lo maneja useAsync internamente)

## 12. Fase 6 — Frontend: Optional chaining y fallbacks

Para CADA componente que renderiza datos de API:

```typescript
// ANTES (se rompe si propiedad es undefined)
{recipe.ingredients.map(i => <li>{i}</li>)}

// DESPUES (seguro)
{recipe.ingredients?.map(i => <li>{i}</li>) ?? <p>Sin ingredientes</p>}
```

Reglas:
- Usar `?.` al acceder a arrays anidados: `data?.suppliers?.map(...)`
- Usar `??` para valores por defecto: `data?.name ?? "Sin nombre"`
- Usar `||` para strings: `data?.description || "Descripcion no disponible"`

## 13. Fase 7 — Frontend: Formularios con finally

Para CADA formulario que envia datos:

```typescript
const [isLoading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

async function handleSubmit(e: React.FormEvent) {
  e.preventDefault();
  setLoading(true);
  setError(null);
  try {
    const response = await fetch("/api/endpoint", { method: "POST", body: formData });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: "Error del servidor." }));
      throw new Error(err.detail || "Error al enviar el formulario.");
    }
    // Exito: limpiar form, mostrar mensaje
  } catch (err) {
    setError(err instanceof Error ? err.message : "Error inesperado.");
  } finally {
    setLoading(false); // SIEMPRE se ejecuta
  }
}
```

## 14. Fase 8 — Scripts: Manejo de errores y sys.exit

Para CADA script en `scripts/`:

```python
import sys
import csv

def main() -> None:
    path = "data.csv"

    # Defensivo: verificar que el archivo existe antes de abrir
    if not os.path.exists(path):
        print(f"Error: archivo no encontrado: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: archivo no encontrado: {path}", file=sys.stderr)
        sys.exit(1)
    except csv.Error as exc:
        print(f"Error: formato CSV invalido: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error inesperado al leer {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    # Defensivo: verificar datos antes de procesar
    if not rows:
        print("Advertencia: el archivo esta vacio.", file=sys.stderr)
        sys.exit(0)  # No es error critico

    # Procesar
    errores = 0
    for i, row in enumerate(rows):
        try:
            if not row.get("email"):
                print(f"Error: fila {i+1} sin email, omitida.", file=sys.stderr)
                errores += 1
                continue
            procesar_fila(row)
        except Exception as exc:
            print(f"Error procesando fila {i+1}: {exc}", file=sys.stderr)
            errores += 1

    if errores > 0:
        print(f"Procesamiento completado con {errores} errores.", file=sys.stderr)

if __name__ == "__main__":
    main()
```

## 15. Fase 9 — General: console.error y datos sensibles

Buscar en TODO el repositorio:

```bash
# Buscar console.error o print que expongan datos sensibles
grep -rn "console\.error" uis/ --include="*.ts" --include="*.tsx"
grep -rn "console\.log" uis/ --include="*.ts" --include="*.tsx"
grep -rn "print(" services/api/ --include="*.py"
grep -rn "DB_URL\|DATABASE\|SECRET_KEY\|API_KEY" uis/ --include="*.ts"

# Por cada hallazgo:
# - Si expone datos sensibles -> ELIMINAR o reemplazar por logger (backend)
# - Si expone errores tecnicos -> reemplazar por mensaje legible
# - Si no es necesario -> ELIMINAR
```

## 16. Fase 10 — Verificacion y validacion

```bash
# 1. Verificar que el backend arranca sin errores
cd services/api
uv run uvicorn app.main:app &
curl -s http://localhost:8000/docs | head -5
kill %1 2>/dev/null
cd ../..

# 2. Verificar que el frontend compila
cd uis/backoffice
npm run build 2>&1 | tail -10
cd ../..

# 3. Verificar que los tests del backend pasan
cd services/api
uv run pytest -v 2>&1 | tail -20
cd ../..

# 4. Verificar que los scripts se ejecutan sin errores
python3 scripts/*.py 2>&1 | head -5

# 5. Verificar que no hay console.error con datos sensibles
grep -rn "console\.error" uis/ --include="*.ts" --include="*.tsx"
grep -rn "print(" services/api/ --include="*.py"
```

## 17. Fase 11 — Commit, push y PR

```bash
# Stage todos los cambios
git add -A

# Commit
git commit -m "fix: error handling audit across all layers (ai-eng-error-handling)

Apply consistent error handling strategy across frontend, backend, and scripts:

Backend:
- Add Pydantic schemas for structured error responses (ErrorResponse, ValidationErrorResponse)
- Add core/errors.py with safe_error() and log_and_raise() utilities
- Add global exception handlers in main.py (Exception, ValueError, 404)
- Narrow try/except blocks in route handlers to specific operations
- Never expose Python tracebacks, DB connection strings, or internal paths

Frontend:
- Add useAsync hook for three-state pattern (loading/success/error)
- Add AsyncView component with spinner, error message, retry button
- Add optional chaining (?.) and fallbacks (??) for nullable nested properties
- Add finally blocks to all form submissions to clear loading state
- Replace raw error messages with human-readable text and call-to-action

Scripts:
- Wrap file I/O and CSV parsing in try/except with stderr messages
- Add sys.exit(1) on critical failures
- Add defensive checks for missing or malformed input data

General:
- Remove console.error and print statements that expose sensitive information

Branch: error-handling-audit"

# Push
git push origin error-handling-audit

# PR
gh pr create   --title "Error Handling Audit - Cross-cutting resilience improvements"   --body "## Resumen

Auditoria y correccion transversal de gestion de errores en todo el monorepo.

### Backend
- Esquemas Pydantic para errores estructurados
- Manejador global de excepciones (sin tracebacks al cliente)
- Try/except acotados en cada endpoint

### Frontend
- Hook useAsync + componente AsyncView (3 estados)
- Optional chaining y fallbacks en renderizado
- Finally en formularios

### Scripts
- Try/except en I/O con mensajes en stderr
- sys.exit(1) en fallos criticos
- Validacion defensiva de entrada

### General
- Eliminacion de console.error y print con datos sensibles

### Ejecucion
\`\`\`bash
cd services/api && uv run pytest
cd uis/backoffice && npm run build
\`\`\`"
```

## 18. Checklist de evaluacion 4Geeks

```
CHECKLIST - Gestion de Errores (ai-eng-error-handling)
======================================================================

FRONTEND
[ ] 01. Todas las llamadas fetch tienen try/catch acotados
[ ] 02. Toda operacion asincrona tiene 3 estados: loading / success / error
[ ] 03. Mensajes de error legibles (no stack traces, codigos HTTP ni JSON parse)
[ ] 04. Cada error ofrece salida: reintentar, volver a inicio, o soporte
[ ] 05. Optional chaining (?.) en propiedades anidadas
[ ] 06. Fallbacks (??) para valores null/undefined
[ ] 07. Bloques finally limpian estado de carga
[ ] 08. Boton de submit se deshabilita durante envio

BACKEND
[ ] 09. try/except acotados a operaciones especificas (no funciones enteras)
[ ] 10. Respuestas HTTP con codigos correctos (400/404/422/500)
[ ] 11. Cuerpo JSON limpio y estructurado en errores
[ ] 12. Sin tracebacks de Python en respuestas al cliente
[ ] 13. Sin datos sensibles en errores (conexiones, rutas, secretos)
[ ] 14. Llamadas a APIs externas con manejo de errores
[ ] 15. Manejador global de excepciones
[ ] 16. Logger configurado (logging.basicConfig o similar)

SCRIPTS
[ ] 17. try/except en lectura/escritura de archivos
[ ] 18. try/except en parseo CSV/JSON
[ ] 19. Mensajes de error en stderr (no stdout)
[ ] 20. sys.exit(1) en error critico
[ ] 21. sys.exit(0) en exito
[ ] 22. Comprobaciones defensivas antes de procesar

GENERAL
[ ] 23. Sin console.error ni print con datos sensibles
[ ] 24. Sin console.log en produccion (frontend)
[ ] 25. Ramas correctas (error-handling-audit)

EXTRA
[ ] 26. Reporte de auditoria en docs/auditoria-errores.md
[ ] 27. PR description completa con resumen de cambios
[ ] 28. Commits agrupados por capa (fix(web):, fix(api):, fix(scripts):)
[ ] 29. No hay nuevas funcionalidades en la rama
[ ] 30. Tests del backend pasan (uv run pytest)
```

## 19. Orden de ejecucion

```yaml
orden:
  fase_0: "Rama error-handling-audit, explorar estructura, leer archivos clave"
  fase_1: "Auditoria automatizada con IA -> docs/auditoria-errores.md (NO MODIFICAR)"
  fase_2: "Backend: schemas/error.py + core/errors.py"
  fase_3: "Backend: global exception handlers en main.py"
  fase_4: "Backend: try/except acotados en routes/*.py"
  fase_5: "Frontend: use-async.ts + AsyncView.tsx"
  fase_6: "Frontend: optional chaining (?.) y fallbacks (??)"
  fase_7: "Frontend: formularios con finally"
  fase_8: "Scripts: try/except, sys.exit, stderr, defensivo"
  fase_9: "General: console.error / print con datos sensibles"
  fase_10: "Verificacion: backend arranca, frontend compila, tests pasan"
  fase_11: "Commit, push y PR"

reglas:
  - "NO pasar a la siguiente fase hasta que la anterior este COMPLETADA"
  - "Fase 10 obligatoria: verificar que todo funcione antes de commit"
  - "NO introducir nuevas funcionalidades o refactor no relacionado"
  - "Si un fix revela un bug en logica de negocio -> REPORTAR, NO CORREGIR"
  - "Documentar en TESTING.md existente cualquier cambio relevante"
```

