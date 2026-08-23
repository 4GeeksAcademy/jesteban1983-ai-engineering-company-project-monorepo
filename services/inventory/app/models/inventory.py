# ============================================
# models/inventory.py - Modelo ORM de Items de Inventario
# ============================================
# Aquí definimos cómo se guardan los items en la base de datos.
# Cada clase = una tabla en la base de datos.
# Cada atributo = una columna en la tabla.
#
# SQLAlchemy 2.0 usa "type hints" para definir el tipo de cada columna.
# Mapped[int] significa "mapeado a entero" en la BD.

from datetime import datetime  # Para fechas (created_at, updated_at)
from decimal import Decimal    # Para precios (sin errores de redondeo)
from typing import Optional    # Para campos que pueden ser NULL

from sqlalchemy import (
    Boolean,      # Tipo booleano (True/False)
    DateTime,     # Tipo fecha/hora
    Integer,      # Tipo entero
    Numeric,      # Tipo decimal (para dinero)
    String,       # Tipo texto corto (VARCHAR)
    Text,         # Tipo texto largo
    func,         # Funciones SQL como now() para fechas automáticas
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importamos la Base que creamos en database.py
from app.database import Base


class Item(Base):
    """
    Modelo de Item de inventario.
    
    Representa un producto en el almacén.
    Cada instancia de Item = una fila en la tabla "inventory_items".
    
    Ejemplo de uso:
        item = Item(
            sku="CAM-001",
            name="Cámara DSLR",
            price=Decimal("599.99"),
            category="Electronics",
            quantity=50,
        )
    """
    
    # __tablename__ es el nombre de la tabla en la base de datos
    __tablename__ = "inventory_items"

    # --- Columnas de la tabla ---
    # id: Clave primaria (cada item tiene un ID único)
    id: Mapped[int] = mapped_column(primary_key=True)
    # primary_key=True → es la clave principal, se auto-incrementa

    # sku: Código único del producto (Stock Keeping Unit)
    # unique=True → no pueden haber dos items con el mismo SKU
    # index=True → crea un índice para búsquedas rápidas por SKU
    # String(50) → texto de máximo 50 caracteres
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # name: Nombre del producto (obligatorio, máximo 200 caracteres)
    name: Mapped[str] = mapped_column(String(200))

    # description: Descripción del producto
    # Optional[str] → puede ser NULL (no es obligatorio)
    # Text → tipo TEXT en SQL (texto largo sin límite)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # quantity: Cantidad disponible en inventario
    # Integer → número entero
    # default=0 → si no se especifica, comienza en 0
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    # price: Precio unitario del producto
    # Numeric(10, 2) → decimal con 10 dígitos totales, 2 decimales (ej: 599.99)
    # El tipo Decimal de Python evita errores de redondeo (a diferencia de float)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # category: Categoría del producto (Fashion, Electronics, Cosmetics, etc.)
    category: Mapped[str] = mapped_column(String(100))

    # warehouse: Almacén donde se guarda el producto
    # default="main" → por defecto en el almacén principal
    warehouse: Mapped[str] = mapped_column(String(100), default="main")

    # min_stock: Stock mínimo (cuando quantity < min_stock, es "Low stock")
    # default=10 → por defecto, mínimo 10 unidades
    min_stock: Mapped[int] = mapped_column(Integer, default=10)

    # is_active: Indica si el item está activo
    # default=True → por defecto está activo
    # Para "eliminar" un producto, lo desactivamos (borrado lógico)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # created_at: Fecha de creación del registro
    # server_default=func.now() → la BD pone la fecha automáticamente
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # ============================================
    # updated_at: Fecha de última modificación
    # ============================================
    # onupdate=func.now() → se actualiza AUTOMÁTICAMENTE cada vez
    # que se modifica el registro. ¡No necesitas hacer nada!
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),  # Valor inicial al crear
        onupdate=func.now(),        # Se actualiza al modificar
    )

    # ============================================
    # movements: Relación con los movimientos
    # ============================================
    # Esto NO es una columna en la BD, es una "relación virtual".
    # Permite hacer: item.movements → obtener todos los movimientos del item.
    #
    # back_populates="item" → se conecta con Movement.item
    # cascade="all, delete-orphan" → si borras el item, se borran sus movimientos
    movements: Mapped[list["Movement"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        """Representación legible del objeto (útil para debugging)."""
        return f"<Item(id={self.id}, sku='{self.sku}', name='{self.name}')>"