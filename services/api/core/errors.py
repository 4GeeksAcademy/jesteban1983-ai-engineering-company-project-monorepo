"""Utilidades para gestión de errores en FastAPI.

Proporciona helpers para lanzar errores HTTP con mensajes seguros
(sin tracebacks, sin datos sensibles) y registrar en servidor.

Uso:
    raise safe_error(404, "Proveedor no encontrado.")
    raise log_and_raise(500, "Error interno.", exc_info=exc)
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException

from schemas.error import ErrorResponse

logger = logging.getLogger("trackflow")


def safe_error(status_code: int, message: str, error_code: str = None) -> HTTPException:
    """Crea un HTTPException con mensaje seguro (sin tracebacks).

    Args:
        status_code: Código HTTP (400, 404, 409, 422, 500, etc.)
        message: Mensaje legible para el cliente.
        error_code: Código interno opcional para depuración.

    Returns:
        HTTPException con body JSON estructurado.
    """
    detail = ErrorResponse(
        detail=message,
        error_code=error_code,
        status_code=status_code,
    ).model_dump()
    return HTTPException(status_code=status_code, detail=detail)


def log_and_raise(
    status_code: int,
    user_message: str,
    error_code: str = None,
    exc_info: Exception = None,
) -> HTTPException:
    """Registra el error en el servidor y lanza excepción segura al cliente.

    Args:
        status_code: Código HTTP.
        user_message: Mensaje legible para el usuario final.
        error_code: Código interno para identificación.
        exc_info: Excepción original (se logea, no se expone).

    Returns:
        HTTPException (siempre lanza, nunca retorna normalmente).
    """
    if exc_info:
        logger.exception(
            "Error %s (%s): %s", status_code, error_code or "unk", user_message,
            exc_info=exc_info,
        )
    else:
        logger.error(
            "Error %s (%s): %s", status_code, error_code or "unk", user_message,
        )
    raise safe_error(status_code, user_message, error_code)