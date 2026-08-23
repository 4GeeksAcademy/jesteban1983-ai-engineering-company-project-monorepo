#!/usr/bin/env python3
"""Script para reescribir la migración de Alembic con comentarios en español."""

import os

content = '''"""initial_models

Revision ID: 291d5b194821
Revises: 
Create Date: 2026-08-19 12:46:57.475981

"""

# ============================================
# Migracion: initial_models
# ============================================
# Esta migracion crea las dos tablas principales del sistema de inventario:
#
# 1. inventory_items - Almacena los articulos del inventario
# 2. inventory_movements - Registra los movimientos (entradas/salidas/ajustes)
#
# Creada automaticamente por: alembic revision --autogenerate -m "initial_models"
# Comando: alembic upgrade head  -> Aplica esta migracion
# Comando: alembic downgrade -1  -> Deshace esta migracion

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "291d5b194821"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica la migracion - Crea las tablas inventory_items y inventory_movements."""
    
    # ============================================
    # Tabla: inventory_items
    # ============================================
    # Columnas:
    #   id          -> Identificador unico (autoincremental)
    #   sku         -> Codigo unico del producto (ej: "LAP-001")
    #   name        -> Nombre del producto
    #   description -> Descripcion detallada (opcional)
    #   quantity    -> Cantidad disponible en stock
    #   price       -> Precio unitario (NUMERIC(10,2) = hasta 99999999.99)
    #   category    -> Categoria del producto (ej: "electronica")
    #   warehouse   -> Almacen donde se encuentra (ej: "principal")
    #   min_stock   -> Stock minimo para alertas
    #   is_active   -> Soft-delete: False = eliminado logico
    #   created_at  -> Fecha de creacion
    #   updated_at  -> Fecha de ultima actualizacion
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("warehouse", sa.String(length=100), nullable=False),
        sa.Column("min_stock", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Indice unico para SKU (no pueden existir dos productos con el mismo SKU)
    op.create_index(op.f("ix_inventory_items_sku"), "inventory_items", ["sku"], unique=True)

    # ============================================
    # Tabla: inventory_movements
    # ============================================
    # Columnas:
    #   id            -> Identificador unico
    #   item_id       -> FK al producto (inventory_items.id)
    #   movement_type -> Tipo: "inbound" | "outbound" | "adjustment"
    #   quantity      -> Cantidad movida
    #   reason        -> Motivo del movimiento (opcional)
    #   created_at    -> Fecha del movimiento
    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("movement_type", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["inventory_items.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Deshace la migracion - Elimina las tablas en orden inverso."""
    # 1. Primero eliminar movements (depende de items)
    op.drop_table("inventory_movements")
    # 2. Eliminar el indice de SKU
    op.drop_index(op.f("ix_inventory_items_sku"), table_name="inventory_items")
    # 3. Finalmente eliminar items
    op.drop_table("inventory_items")
'''

# Ruta al archivo de migracion
migration_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "alembic",
    "versions",
    "291d5b194821_initial_models.py",
)

with open(migration_dir, "w") as f:
    f.write(content)

print(f"Migration file rewritten: {migration_dir}")
print("OK - migration updated with Spanish comments")