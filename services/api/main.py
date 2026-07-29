from __future__ import annotations

import csv
import logging
from io import StringIO

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic_settings import BaseSettings, SettingsConfigDict

from analyzer import analyze_incidents, build_export_rows, parse_csv_text
from routes.suppliers import router as suppliers_router
from routes.users import router as users_router
from routes.profiles import router as profiles_router
from routes.auth import router as auth_router
from routes.incidents import router as incidents_router
from schemas.error import ErrorResponse

# ── Configurar logging estructurado ────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("trackflow")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "TrackFlow Incidents API"
    cors_origins: str = "http://localhost:3000"


settings = Settings()
app = FastAPI(title=settings.app_name)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────
# Manejadores globales de excepciones
# NUNCA se devuelven stack traces al cliente (Checklist #16)
# ─────────────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Captura errores de validación Pydantic y devuelve un 422."""
    errors = []
    for err in exc.errors():
        field = " → ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Error de validación")
        errors.append(f"{field}: {msg}" if field else msg)
    logger.warning("ValidationError en %s %s: %s", request.method, request.url.path, errors)
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            detail="Datos inválidos. Revisa los campos marcados.",
            error_code="VALIDATION_ERROR",
            status_code=422,
        ).model_dump(),
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Captura ValueError → 400."""
    logger.warning("ValueError en %s %s: %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            detail="Solicitud inválida.",
            error_code="INVALID_REQUEST",
            status_code=400,
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Re-lanza HTTPException tal cual (son intencionales)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Captura cualquier excepción no controlada y devuelve 500 sin stack trace."""
    logger.exception(
        "Excepción no capturada en %s %s", request.method, request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Error interno del servidor. Intenta de nuevo.",
            error_code="INTERNAL_ERROR",
            status_code=500,
        ).model_dump(),
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """404 genérico → JSON estructurado."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            detail="Recurso no encontrado.",
            error_code="NOT_FOUND",
            status_code=404,
        ).model_dump(),
    )

# Registrar el router de proveedores (Milestone 9)
# Todos sus endpoints quedan bajo /suppliers/
app.include_router(suppliers_router)

# Registrar routers de autenticación (Feature Auth)
app.include_router(users_router)
app.include_router(profiles_router)
app.include_router(auth_router)

# Registrar router de incidencias (Centralized Incident Manager)
app.include_router(incidents_router)


_last_analysis: dict | None = None


@app.get("/")
def root() -> dict:
    return {
        "app": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "suppliers": "/suppliers/",
            "incidents_analyze": "/api/incidents/analyze",
            "incidents_export": "/api/incidents/results/export",
        },
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/incidents/analyze")
async def analyze_uploaded_incidents(file: UploadFile = File(...)) -> dict:
    global _last_analysis

    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded") from exc

    if not content.strip():
        raise HTTPException(status_code=400, detail="Uploaded file has no content")

    try:
        rows = parse_csv_text(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not rows:
        raise HTTPException(status_code=400, detail="CSV has no data rows")

    _last_analysis = analyze_incidents(rows)
    return _last_analysis


@app.get("/api/incidents/results/export")
def export_last_results() -> PlainTextResponse:
    if _last_analysis is None:
        raise HTTPException(status_code=404, detail="No analysis found. Run /api/incidents/analyze first")

    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(build_export_rows(_last_analysis))
    payload = output.getvalue()

    headers = {"Content-Disposition": 'attachment; filename="results.csv"'}
    return PlainTextResponse(content=payload, media_type="text/csv", headers=headers)
