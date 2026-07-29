"""
routes/profiles.py — Endpoints CRUD para Profile

TODOS los endpoints están PROTEGIDOS.

Rutas:
- GET  /profiles/me    → Obtener mi perfil (PROTEGIDO)
- PUT  /profiles/me    → Actualizar mi perfil (PROTEGIDO)

Protección:
- get_current_user inyecta el usuario autenticado
- Solo el owner del perfil puede ver/modificar su perfil
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies.auth_deps import get_current_user
from models.profile_models import ProfileResponse, ProfileUpdate
from services.user_service import get_profile_by_user_id, update_profile
from core.errors import safe_error, log_and_raise

router = APIRouter(prefix="/profiles", tags=["profiles"])

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# GET /profiles/me — OBTENER MI PERFIL (PROTEGIDO)
# ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=ProfileResponse)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario autenticado.

    PROTEGIDO — requiere token JWT válido.

    Args:
        current_user: Usuario autenticado (inyectado por get_current_user).

    Retorna:
        ProfileResponse con los datos del perfil.

    Raises:
        404: Si el perfil no existe.
    """
    try:
        profile = get_profile_by_user_id(current_user["id"])
    except Exception as exc:
        logger.exception("Error al obtener perfil del usuario %s", current_user.get("id"))
        raise safe_error(500, "Error interno. Intenta de nuevo.")

    if profile is None:
        raise safe_error(404, "Perfil no encontrado.")

    return profile


# ─────────────────────────────────────────────────────────────
# PUT /profiles/me — ACTUALIZAR MI PERFIL (PROTEGIDO)
# ─────────────────────────────────────────────────────────────

@router.put("/me", response_model=ProfileResponse)
def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Actualiza el perfil del usuario autenticado.

    PROTEGIDO — requiere token JWT válido.
    Solo el owner del perfil puede modificarlo.

    Args:
        profile_data: Campos a actualizar (name, phone, address — opcionales).
        current_user: Usuario autenticado.

    Retorna:
        ProfileResponse con los datos actualizados.

    Raises:
        404: Si el perfil no existe.
    """
    try:
        profile = update_profile(current_user["id"], profile_data)
    except Exception as exc:
        logger.exception("Error al actualizar perfil del usuario %s", current_user.get("id"))
        raise safe_error(500, "Error interno. Intenta de nuevo.")

    if profile is None:
        raise safe_error(404, "Perfil no encontrado.")

    return profile