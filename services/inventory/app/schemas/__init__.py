# ============================================
# schemas/__init__.py
# ============================================
# Exporta todos los schemas para importarlos fácilmente

from app.schemas.common import PaginationParams, PaginatedResponse
from app.schemas.inventory import (
    ItemBase,
    ItemCreate,
    ItemUpdate,
    ItemOut,
)
from app.schemas.movement import MovementCreate, MovementOut

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemOut",
    "MovementCreate",
    "MovementOut",
]