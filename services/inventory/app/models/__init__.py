# ============================================
# models/__init__.py - Exporta la clase Base
# ============================================
# Este archivo importa la Base desde database.py para que
# Alembic (migraciones) pueda encontrar todos los modelos.
# También importa los modelos para que estén disponibles
# desde "from app.models import Item, Movement"

from app.database import Base  # Base para modelos SQLAlchemy
from app.models.inventory import Item  # Modelo de inventario
from app.models.movement import Movement  # Modelo de movimientos

# Exportamos todo para que esté disponible desde app.models
__all__ = ["Base", "Item", "Movement"]