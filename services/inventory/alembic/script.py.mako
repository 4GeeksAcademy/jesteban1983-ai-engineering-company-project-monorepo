# ============================================
# script.py.mako - Plantilla para generar migraciones
# ============================================
# Cuando ejecutas "alembic revision --autogenerate", Alembic usa
# esta plantilla para crear el archivo de migración.
# 
# Las variables con ${} son reemplazadas automáticamente:
# - message: El mensaje que pusiste en -m "mensaje"
# - revision: ID único de esta migración
# - down_revision: ID de la migración anterior
# - create_date: Fecha de creación

"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Aplica la migración (crea/modifica tablas)."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Deshace la migración (vuelve al estado anterior)."""
    ${downgrades if downgrades else "pass"}