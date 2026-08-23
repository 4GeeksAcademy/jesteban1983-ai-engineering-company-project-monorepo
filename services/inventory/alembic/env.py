# ============================================
# alembic/env.py - Configuración del entorno de Alembic
# ============================================
# Alembic necesita saber DÓNDE están tus modelos para poder
# compararlos con la base de datos actual y generar migraciones.
#
# Este archivo configura:
# 1. Dónde buscar los modelos (target_metadata)
# 2. Cómo conectarse a la BD (sqlalchemy.url)
# 3. Qué incluir en las migraciones automáticas

import os
import re
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ============================================
# IMPORTANTE: Añadir el directorio raíz al path
# ============================================
# Esto permite que Alembic encuentre "app" cuando importamos los modelos.
# Sin esto, tendríamos errores como "ModuleNotFoundError: No module named 'app'"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ============================================
# Importar la Base y los modelos
# ============================================
# Alembic necesita conocer TODOS los modelos para generar migraciones.
# Importar Base es suficiente si todos los modelos heredan de ella.
from app.database import Base
from app.models import Item, Movement  # Forzar importación de modelos

# Configuración de logging de Alembic (lee la sección [loggers] de alembic.ini)
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ============================================
# target_metadata: El "espejo" de la base de datos
# ============================================
# Alembic compara target_metadata (lo que definen tus modelos)
# con el estado actual de la BD para determinar qué cambios hacer.
target_metadata = Base.metadata


# ============================================
# Función para convertir URL async a sync
# ============================================
# Alembic usa SQLAlchemy síncrono, pero nosotros usamos drivers async
# (asyncpg, aiosqlite) en la app. Para que Alembic funcione,
# necesitamos convertir:
#   "postgresql+asyncpg://..."  →  "postgresql://..."
#   "sqlite+aiosqlite:///..."   →  "sqlite:///..."
def _to_sync_url(url: str) -> str:
    """Convierte una URL de base de datos async a sync para Alembic.
    
    Ejemplos:
        postgresql+asyncpg://user:pass@host/db → postgresql://user:pass@host/db
        sqlite+aiosqlite:///./dev.db          → sqlite:///./dev.db
    """
    return re.sub(r"(\w+)\+\w+://", r"\1://", url)


# ============================================
# Función para obtener la URL de la BD
# ============================================
# Prioridad:
# 1. Variable de entorno DATABASE_URL (producción/Supabase)
# 2. Lo que está en alembic.ini (desarrollo local)
def get_database_url() -> str:
    """Obtiene la URL de la base de datos y la convierte a formato sync."""
    # Intentar usar variable de entorno primero
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = config.get_main_option("sqlalchemy.url")
    # Convertir async → sync para Alembic
    sync_url = _to_sync_url(db_url)
    print(f"[Alembic] Conectando a: {sync_url}")
    return sync_url


# ============================================
# Configuración para migraciones OFFLINE (generar SQL)
# ============================================
# No usamos esto normalmente, pero está disponible.
def run_migrations_offline() -> None:
    """
    Genera migraciones en modo offline.
    Útil para revisar el SQL antes de ejecutarlo.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================
# Configuración para migraciones ONLINE (ejecutar contra BD)
# ============================================
def run_migrations_online() -> None:
    """
    Conecta a la BD y ejecuta las migraciones.
    Este es el modo que usamos normalmente.
    """
    # Obtener configuración de alembic.ini
    configuration = config.get_section(config.config_ini_section, {})
    
    # Sobrescribir la URL de la BD
    configuration["sqlalchemy.url"] = get_database_url()

    # Crear conexión a la BD
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Conectar y ejecutar migraciones
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================
# Decidir qué modo usar
# ============================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()