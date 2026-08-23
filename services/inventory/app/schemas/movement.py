# ============================================
# schemas/movement.py - Schemas para Movimientos de Inventario
# ============================================
# Los movimientos registran cambios de stock (entradas, salidas, ajustes).

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MovementCreate(BaseModel):
    """
    Schema para CREAR un movimiento de inventario.
    
    movement_type: "inbound" (entrada), "outbound" (salida), "adjustment" (ajuste)
    quantity: cantidad del cambio (siempre positiva, la dirección la da el tipo)
    reason: motivo del movimiento (opcional)
    """
    movement_type: str = Field(
        ...,
        pattern="^(inbound|outbound|adjustment)$",
        description="Tipo: inbound (entrada), outbound (salida), adjustment (ajuste)",
    )
    quantity: int = Field(
        ..., gt=0,
        description="Cantidad del movimiento (siempre positiva)",
    )
    reason: Optional[str] = Field(
        default=None, max_length=500,
        description="Razón del movimiento",
    )


class MovementOut(BaseModel):
    """
    Schema para DEVOLVER un movimiento al usuario.
    from_attributes=True permite convertir desde ORM.
    """
    id: int
    item_id: int
    movement_type: str
    quantity: int
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)