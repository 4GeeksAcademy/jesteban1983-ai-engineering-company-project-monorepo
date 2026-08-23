# ============================================
# models/movement.py - Modelo ORM de Movimientos de Inventario
# ============================================
# Cada movimiento registra un cambio en el stock de un producto.
# Sirve como "auditoría" para saber qué pasó con el inventario.
#
# Tipos de movimiento:
# - "inbound" = entrada de mercancía (aumenta stock)
# - "outbound" = salida/venta (disminuye stock)
# - "adjustment" = ajuste manual (corrige diferencias)

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,   # Clave foránea: referencia a otra tabla
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base


class Movement(Base):
    """
    Modelo de Movimiento de Inventario.
    
    Cada movimiento registra un cambio en la cantidad de un item.
    
    Ejemplo de uso:
        movement = Movement(
            item_id=1,
            movement_type="inbound",
            quantity=20,
            reason="Reposición de stock",
        )
    """
    
    # Nombre de la tabla en la base de datos
    __tablename__ = "inventory_movements"

    # --- Columnas ---
    # id: Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # item_id: Clave foránea → referencia al item relacionado
    # ForeignKey("inventory_items.id") = este campo apunta al id de inventory_items
    # Así conectamos cada movimiento con su producto
    item_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_items.id")
    )

    # movement_type: Tipo de movimiento
    # String(20) → texto corto: "inbound", "outbound", "adjustment"
    movement_type: Mapped[str] = mapped_column(String(20))

    # quantity: Cantidad que cambió (siempre positiva)
    # La dirección (entrada/salida) la define movement_type
    quantity: Mapped[int] = mapped_column(Integer)

    # reason: Razón del movimiento (opcional)
    # Por qué se hizo este movimiento (ej: "Reposición", "Venta", "Ajuste")
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # user_uuid: UUID del operador que realizó el movimiento (opcional)
    # Se asigna desde el frontend tras login. String(36) = formato UUID estándar.
    user_uuid: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True
    )

    # created_at: Fecha del movimiento (automática)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # --- Relaciones ---
    # item: Referencia al Item asociado
    # back_populates="movements" → conexión con Item.movements
    # Esto permite hacer: movement.item.nombre para obtener el nombre del producto
    item: Mapped["Item"] = relationship(back_populates="movements")

    def __repr__(self):
        """Representación legible del objeto."""
        return (
            f"<Movement(id={self.id}, "
            f"item_id={self.item_id}, "
            f"type='{self.movement_type}', "
            f"qty={self.quantity})>"
        )