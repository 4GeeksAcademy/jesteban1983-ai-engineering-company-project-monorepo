# ============================================
# schemas/common.py - Schemas compartidos (paginación, etc.)
# ============================================
# Schemas = modelos de Pydantic para validar datos que entran/salen de la API
# No confundir con los modelos SQLAlchemy que son para la base de datos.
#
# Diferencia clave:
# - Modelo ORM (models/) = cómo se guarda en la BD
# - Schema Pydantic (schemas/) = cómo se valida lo que envía el usuario
#
# Generic[T] permite crear schemas que funcionan con cualquier tipo de dato.
# PaginatedResponse[ItemOut] contendrá items de tipo ItemOut.

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

# T es un "tipo genérico" - representa cualquier tipo
T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Parámetros de paginación para listas.
    
    Se usa como query params en los endpoints GET /items/.
    Ejemplo: GET /items/?page=2&per_page=10
    
    page: Número de página (empieza en 1)
    per_page: Items por página (entre 1 y 100)
    """
    page: int = Field(default=1, ge=1, description="Número de página")
    per_page: int = Field(
        default=20, ge=1, le=100, description="Items por página"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta paginada genérica.
    
    Contiene:
    - items: Lista de elementos de la página actual
    - total: Total de elementos en toda la consulta
    - page: Página actual
    - per_page: Items por página
    - total_pages: Total de páginas (se calcula automáticamente)
    """
    items: list[T]                          # Los elementos de esta página
    total: int = Field(..., description="Total de elementos")  # Total global
    page: int = Field(..., description="Página actual")
    per_page: int = Field(..., description="Elementos por página")
    total_pages: int = Field(..., description="Total de páginas")