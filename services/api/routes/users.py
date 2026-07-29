"""
routes/users.py — Endpoints CRUD para User

TODOS los endpoints están protegidos EXCEPTO POST /users (registro).

Rutas:
- POST   /users         → Registrar (PÚBLICO)
- GET    /users         → Listar (PROTEGIDO)
- GET    /users/{id}    → Obtener por ID (PROTEGIDO)
- PUT    /users/{id}    → Actualizar (PROTEGIDO — solo owner o admin)
- DELETE /users/{id}    → Eliminar (PROTEGIDO — solo owner o admin)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from core.errors import safe_error, log_and_raise
from dependencies.auth_deps import get_current_user
from models.profile_models import ProfileCreate
from models.user_models import UserCreate, UserResponse, UserUpdate
from services.user_service import (
    create_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
)

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# POST /users — REGISTRO (PÚBLICO)
# ─────────────────────────────────────────────────────────────

@router.post("/", response_model=UserResponse, status_code=200)
def register_user(user_data: UserCreate):
    """
    Registra un nuevo usuario en el sistema.

    Endpoint PÚBLICO — no requiere autenticación.
    Crea automáticamente el perfil vinculado al usuario.

    Args:
        user_data: email, password, role (opcional), más datos de profile.

    Retorna:
        UserResponse con id, email, role, is_active, created_at.

    Raises:
        409: Si el email ya está registrado.
        422: Si los datos no pasan validación Pydantic.
    """
    try:
        user_data_dict = user_data.model_dump() if hasattr(user_data, 'model_dump') else {}
        profile_data = None
        profile_fields = {k: v for k, v in user_data_dict.items() if k in ('name', 'phone', 'address')}
        if any(profile_fields.values()):
            profile_data = ProfileCreate(**profile_fields)
    except Exception as exc:
        logger.exception("Error al extraer datos de perfil durante registro")
        raise safe_error(422, "Datos de perfil inválidos.")

    try:
        user = create_user(user_data, profile_data)
    except ValueError as e:
        logger.warning("Registro duplicado o inválido: %s", e)
        raise safe_error(409, str(e))
    except Exception as exc:
        logger.exception("Error al crear usuario")
        raise safe_error(500, "Error interno al registrar usuario.")

    return user


# ─────────────────────────────────────────────────────────────
# GET /users — LISTAR (PROTEGIDO)
# ─────────────────────────────────────────────────────────────

@router.get("/", response_model=list[UserResponse])
def list_users(current_user: dict = Depends(get_current_user)):
    """
    Lista todos los usuarios registrados.

    PROTEGIDO — requiere token JWT válido.
    No incluye hashed_password en la respuesta.

    Args:
        current_user: Usuario autenticado (inyectado por get_current_user).

    Retorna:
        Lista de UserResponse.
    """
    try:
        return get_all_users()
    except Exception as exc:
        logger.exception("Error al listar usuarios")
        raise safe_error(500, "Error interno al obtener usuarios.")


# ─────────────────────────────────────────────────────────────
# GET /users/{user_id} — OBTENER POR ID (PROTEGIDO)
# ─────────────────────────────────────────────────────────────

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """
    Obtiene un usuario por su ID.

    PROTEGIDO — requiere token JWT válido.

    Args:
        user_id: ID del usuario a buscar.

    Retorna:
        UserResponse con los datos del usuario.

    Raises:
        404: Si el usuario no existe.
    """
    try:
        user = get_user_by_id(user_id)
    except Exception as exc:
        logger.exception("Error al obtener usuario %s", user_id)
        raise safe_error(500, "Error interno.")

    if user is None:
        raise safe_error(404, f"Usuario con id {user_id} no encontrado.")

    return user


# ─────────────────────────────────────────────────────────────
# PUT /users/{user_id} — ACTUALIZAR (PROTEGIDO — owner o admin)
# ─────────────────────────────────────────────────────────────

@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: int,
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Actualiza los datos de un usuario.

    PROTEGIDO — solo el propio usuario (owner) o un admin pueden actualizar.

    Args:
        user_id: ID del usuario a actualizar.
        update_data: Campos a actualizar (todos opcionales).
        current_user: Usuario autenticado.

    Retorna:
        UserResponse con los datos actualizados.

    Raises:
        403: Si no es owner ni admin.
        404: Si el usuario no existe.
    """
    # Verificar permisos: solo owner o admin
    if current_user["id"] != user_id and current_user.get("role") != "admin":
        raise safe_error(403, "No tienes permisos para actualizar este usuario.")

    try:
        user = update_user(user_id, update_data)
    except Exception as exc:
        logger.exception("Error al actualizar usuario %s", user_id)
        raise safe_error(500, "Error interno al actualizar usuario.")

    if user is None:
        raise safe_error(404, f"Usuario con id {user_id} no encontrado.")

    return user


# ─────────────────────────────────────────────────────────────
# DELETE /users/{user_id} — ELIMINAR (PROTEGIDO — owner o admin)
# ─────────────────────────────────────────────────────────────

@router.delete("/{user_id}")
def delete_user_endpoint(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    Elimina un usuario y su perfil vinculado.

    PROTEGIDO — solo el propio usuario (owner) o un admin pueden eliminar.

    Args:
        user_id: ID del usuario a eliminar.
        current_user: Usuario autenticado.

    Retorna:
        Mensaje de confirmación.

    Raises:
        403: Si no es owner ni admin.
        404: Si el usuario no existe.
    """
    # Verificar permisos: solo owner o admin
    if current_user["id"] != user_id and current_user.get("role") != "admin":
        raise safe_error(403, "No tienes permisos para eliminar este usuario.")

    try:
        deleted = delete_user(user_id)
    except Exception as exc:
        logger.exception("Error al eliminar usuario %s", user_id)
        raise safe_error(500, "Error interno al eliminar usuario.")

    if not deleted:
        raise safe_error(404, f"Usuario con id {user_id} no encontrado.")

    return {"message": "Usuario y perfil eliminados correctamente"}