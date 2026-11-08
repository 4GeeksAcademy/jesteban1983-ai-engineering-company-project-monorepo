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

from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from ..dependencies.auth_deps import get_current_user, get_admin_user
    from ..core.security import check_rate_limit, log_security_event
    from ..core.errors import safe_error, log_and_raise
    from ..models import MessageResponse
    from ..models.profile_models import ProfileCreate
    from ..models.user_models import UserCreate, UserResponse, UserRole, UserUpdate
    from ..services.user_service import (
        create_user,
        delete_user,
        get_all_users,
        get_user_by_email,
        get_user_by_id,
        update_user,
    )
except (ImportError, ValueError):
    from dependencies.auth_deps import get_current_user, get_admin_user
    from core.security import check_rate_limit, log_security_event
    from core.errors import safe_error, log_and_raise
    from models import MessageResponse
    from models.profile_models import ProfileCreate
    from models.user_models import UserCreate, UserResponse, UserRole, UserUpdate
    from services.user_service import (
        create_user,
        delete_user,
        get_all_users,
        get_user_by_email,
        get_user_by_id,
        update_user,
    )

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# POST /users — REGISTRO (PÚBLICO CON HARDENING)
# ─────────────────────────────────────────────────────────────

@router.post("/", response_model=UserResponse, status_code=200)
def register_user(user_data: UserCreate, request: Request):
    """
    Registra un nuevo usuario en el sistema.

    Endpoint PÚBLICO — no requiere autenticación.
    HARDENING OWASP A01: Se fuerza irrevocablemente role='user' para prevenir
    auto-escalada de privilegios a 'admin' o 'manager' vía registro público.
    """
    # Rate limit contra registros masivos / DoS
    check_rate_limit(request, "users_register", max_requests=10, window_seconds=60)

    # Forzar rol 'user' y estado activo en registro público (mitiga VULN-01)
    user_data.role = UserRole.user
    user_data.is_active = True

    # Extraer datos de profile si vienen en el payload
    profile_data = None
    if hasattr(user_data, 'name') or hasattr(user_data, 'phone') or hasattr(user_data, 'address'):
        profile_data = ProfileCreate(
            name=getattr(user_data, 'name', None),
            phone=getattr(user_data, 'phone', None),
            address=getattr(user_data, 'address', None),
        )

    try:
        user = create_user(user_data, profile_data)
        uid = getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else "")
        uemail = getattr(user, "email", None) or (user.get("email") if isinstance(user, dict) else "")
        log_security_event(
            event_type="USER_REGISTERED",
            client_ip=request.client.host if request.client else "127.0.0.1",
            details=f"Usuario registrado exitosamente con id={uid}",
            user_identifier=str(uemail),
            success=True
        )
    except ValueError as e:
        logger.warning("Registro duplicado o inválido: %s", e)
        raise safe_error(409, str(e))
    except Exception as exc:
        logger.exception("Error al crear usuario")
        raise safe_error(500, "Error interno al registrar usuario.")

    return user


# ─────────────────────────────────────────────────────────────
# GET /users — LISTAR (PROTEGIDO — SOLO ADMIN / VULN-02)
# ─────────────────────────────────────────────────────────────

@router.get("/", response_model=list[UserResponse])
def list_users(current_user: dict = Depends(get_admin_user)):
    """
    Lista todos los usuarios registrados.

    PROTEGIDO — Requiere rol 'admin' (mitiga enumeración de usuarios OWASP A01).
    No incluye hashed_password en la respuesta.
    """
    try:
        return get_all_users()
    except Exception as exc:
        logger.exception("Error al listar usuarios")
        raise safe_error(500, "Error interno al obtener usuarios.")


# ─────────────────────────────────────────────────────────────
# GET /users/{user_id} — OBTENER POR ID (PROTEGIDO — OWNER O ADMIN / VULN-03)
# ─────────────────────────────────────────────────────────────

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, request: Request, current_user: dict = Depends(get_current_user)):
    """
    Obtiene un usuario por su ID.

    PROTEGIDO — Requiere ser el propio usuario (owner) o un administrador (mitiga IDOR).
    """
    if current_user["id"] != user_id and current_user.get("role") != "admin":
        client_ip = request.client.host if request.client else "127.0.0.1"
        log_security_event(
            event_type="UNAUTHORIZED_USER_INSPECTION",
            client_ip=client_ip,
            details=f"Usuario {current_user['id']} intentó acceder sin permiso al usuario {user_id}",
            user_identifier=str(current_user["id"]),
            success=False
        )
        raise safe_error(403, "No tienes permisos para consultar este usuario.")

    try:
        user = get_user_by_id(user_id)
    except Exception as exc:
        logger.exception("Error al obtener usuario %s", user_id)
        raise safe_error(500, "Error interno.")
    if user is None:
        raise safe_error(404, f"Usuario con id {user_id} no encontrado.")

    return user


# ─────────────────────────────────────────────────────────────
# PUT /users/{user_id} — ACTUALIZAR (PROTEGIDO — OWNER O ADMIN / VULN-04)
# ─────────────────────────────────────────────────────────────

@router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: int,
    update_data: UserUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Actualiza los datos de un usuario.

    PROTEGIDO — Solo owner o admin.
    HARDENING: Usuarios no administradores tienen estrictamente prohibido alterar
    los campos 'role' o 'is_active' (mitiga auto-escalada de privilegios).
    """
    is_admin = current_user.get("role") == "admin"
    is_owner = current_user["id"] == user_id

    if not is_owner and not is_admin:
        raise safe_error(403, "No tienes permisos para actualizar este usuario.")

    # Si NO es admin, bloquear modificación de rol y estado activo
    if not is_admin:
        if update_data.role is not None or update_data.is_active is not None:
            client_ip = request.client.host if request.client else "127.0.0.1"
            log_security_event(
                event_type="PRIVILEGE_ESCALATION_ATTEMPT",
                client_ip=client_ip,
                details=f"Usuario {current_user['id']} intentó modificar rol o estado activo",
                user_identifier=str(current_user["id"]),
                success=False
            )
            raise safe_error(403, "Solo administradores pueden modificar el rol o el estado activo de una cuenta.")

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

@router.delete("/{user_id}", response_model=MessageResponse)
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

    return MessageResponse(message="Usuario y perfil eliminados correctamente")