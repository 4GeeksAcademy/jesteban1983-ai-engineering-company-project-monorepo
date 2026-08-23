# ============================================
# schemas/inventory.py - Schemas para Items de inventario
# ============================================
# Aquí definimos los esquemas de validación para:
# - Crear un item (ItemCreate): qué datos necesita el usuario
# - Actualizar un item (ItemUpdate): qué datos se pueden modificar
# - Mostrar un item (ItemOut): qué datos devolvemos al usuario
#
# Separamos "lo que entra" de "lo que sale" por seguridad.
# ItemOut incluye id, created_at, updated_at que el usuario NO puede enviar.

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ItemBase(BaseModel):
    """
    Schema base con campos comunes a todas las operaciones.
    
    Todos los campos de creación/actualización comparten estas validaciones.
    Field() añade validaciones extra como:
    - min_length: longitud mínima del texto
    - max_length: longitud máxima
    - gt: mayor que (greater than)
    - ge: mayor o igual que (greater or equal)
    """
    sku: str = Field(
        ..., min_length=3, max_length=50,
        description="Código SKU único del producto (ej: 'CAM-001')",
    )
    name: str = Field(
        ..., min_length=1, max_length=200,
        description="Nombre del producto",
    )
    description: Optional[str] = Field(
        default=None, max_length=1000,
        description="Descripción del producto (opcional)",
    )
    quantity: int = Field(
        default=0, ge=0,
        description="Cantidad disponible en inventario",
    )
    price: Decimal = Field(
        ..., gt=0, max_digits=10, decimal_places=2,
        description="Precio unitario en USD",
    )
    category: str = Field(
        ..., max_length=100,
        description="Categoría (Fashion, Electronics, Cosmetics, Home, Other)",
    )
    warehouse: str = Field(
        default="main", max_length=100,
        description="Almacén donde se guarda",
    )
    min_stock: int = Field(
        default=10, ge=0,
        description="Stock mínimo antes de alerta",
    )
    is_active: bool = Field(
        default=True,
        description="Si está activo (borrado lógico = False)",
    )


class ItemCreate(ItemBase):
    """
    Schema para CREAR un nuevo item.
    Hereda todos los campos de ItemBase.
    """
    pass


class ItemUpdate(BaseModel):
    """
    Schema para ACTUALIZAR un item existente.
    
    Todos los campos son OPCIONALES (None = no cambiar).
    Así podemos actualizar sólo algunos campos.
    
    Ej: PUT /items/1 con {"price": 10.99} → solo cambia el precio
    """
    name: Optional[str] = Field(
        default=None, min_length=1, max_length=200,
    )
    description: Optional[str] = Field(
        default=None, max_length=1000,
    )
    quantity: Optional[int] = Field(
        default=None, ge=0,
    )
    price: Optional[Decimal] = Field(
        default=None, gt=0, max_digits=10, decimal_places=2,
    )
    category: Optional[str] = Field(
        default=None, max_length=100,
    )
    warehouse: Optional[str] = Field(
        default=None, max_length=100,
    )
    min_stock: Optional[int] = Field(
        default=None, ge=0,
    )
    is_active: Optional[bool] = Field(default=None)


class ItemOut(ItemBase):
    """
    Schema para DEVOLVER un item al usuario.
    
    Incluye campos que vienen de la base de datos:
    - id: asignado automáticamente
    - created_at: fecha de creación
    - updated_at: fecha de última modificación
    
    from_attributes=True permite convertir ORM → Schema
    """
    id: int
    created_at: datetime
    updated_at: datetime

    # ConfigDict(from_attributes=True) = permite convertir ORM → Schema
    model_config = ConfigDict(from_attributes=True)

    # ---- Serializador: Decimal → float ----
    # Por defecto, Decimal se convierte a string en JSON.
    # Con este serializador, lo convertimos a número (float).
    # Así el frontend recibe 29.99 en lugar de "29.99"
    @field_serializer("price")
    def serialize_price(self, value: Decimal) -> float:
        """Convierte Decimal a float para la respuesta JSON."""
        return float(value)