"""Esquemas Pydantic para respuestas de error estructuradas.

NUNCA contienen tracebacks, datos de conexión, rutas de archivo
ni ninguna información interna del servidor.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Respuesta de error estándar. NUNCA contiene tracebacks."""
    detail: str
    error_code: Optional[str] = None
    status_code: int = 500


class ValidationErrorDetail(BaseModel):
    """Error de validación a nivel de campo."""
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    """Error de validación con detalles por campo."""
    detail: str = "Datos inválidos. Revisa los campos marcados."
    errors: list[ValidationErrorDetail] = []
    status_code: int = 422