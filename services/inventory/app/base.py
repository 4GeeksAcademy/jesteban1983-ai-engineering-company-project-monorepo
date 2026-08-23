# ============================================
# app/base.py - Base declarativa de SQLAlchemy
# ============================================
# Separamos Base en su propio módulo para evitar que
# Alembic tenga que importar todo database.py (que crea
# el engine asíncrono) solo para obtener la metadata.
#
# Así, env.py importa Base desde aquí sin efectos secundarios.

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos del proyecto.
    
    Todos los modelos ORM heredan de esta clase.
    SQLAlchemy registra automáticamente cada modelo en Base.metadata,
    que es lo que Alembic necesita para generar migraciones.
    """
    pass