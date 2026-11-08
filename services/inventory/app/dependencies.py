# ============================================
# dependencies.py - Inyección de dependencias para FastAPI
# ============================================
# Aquí re-exportamos la función get_db desde database.py
# para que los routers puedan usarla limpiamente.

from app.database import get_db

# Nota: get_db es un async generator que proporciona
# una sesión de base de datos a cada petición HTTP.
# FastAPI la inyecta automáticamente con Depends():
#
# @router.get("/items/")
# async def list_items(db: AsyncSession = Depends(get_db)):
#     ...

__all__ = ["get_db"]