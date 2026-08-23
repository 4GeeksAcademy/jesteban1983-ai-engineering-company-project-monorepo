# ============================================
# database.py - Conexión a la base de datos (SQLite/PostgreSQL)
# ============================================
# Este archivo configura la conexión a la base de datos usando SQLAlchemy.
# Soporta DOS motores de base de datos:
# - SQLite (aiosqlite) para desarrollo local
# - PostgreSQL (asyncpg) para producción
#
# La diferencia la hace la variable DATABASE_URL en .env

from sqlalchemy.ext.asyncio import (
    AsyncSession,      # Sesión asíncrona para hacer consultas
    async_sessionmaker, # Fábrica que crea sesiones asíncronas
    create_async_engine, # Crea el motor de base de datos asíncrono
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings  # Importamos la configuración con DATABASE_URL


# ============================================
# Motor de base de datos (Engine)
# ============================================
# El engine es el objeto principal que maneja la conexión a la BD.
# create_async_engine crea un motor ASÍNCRONO = no bloquea el código
# mientras espera respuesta de la base de datos.
engine = create_async_engine(
    settings.database_url,  # Ej: "sqlite+aiosqlite:///./dev.db"
    echo=False,             # True = muestra todas las consultas SQL (útil para debugging)
)


# ============================================
# Fábrica de sesiones (Session Factory)
# ============================================
# async_sessionmaker crea un "generador" de sesiones.
# Cada vez que llamamos a async_sessionmaker(), obtenemos una nueva sesión.
# expire_on_commit=False evita que SQLAlchemy invalide los objetos después
# de guardarlos (así podemos seguir accediendo a sus atributos).
AsyncSessionFactory = async_sessionmaker(
    bind=engine,               # Conecta la fábrica al motor
    class_=AsyncSession,       # Usa sesiones asíncronas
    expire_on_commit=False,    # No expirar objetos tras commit
)


# ============================================
# Clase Base para los modelos ORM
# ============================================
# Todos nuestros modelos (Item, Movement) heredarán de esta clase.
# DeclarativeBase es la clase base de SQLAlchemy 2.0 para crear modelos.
class Base(DeclarativeBase):
    pass


# ============================================
# Dependencia para FastAPI (inyección de dependencias)
# ============================================
# Esta función se usa como dependencia en los endpoints de FastAPI.
# Cada petición HTTP obtiene su propia sesión de base de datos.
# 
# Es un "generador asíncrono" (async generator):
# 1. yield session → entrega la sesión al endpoint
# 2. finally → cuando termina, cierra la sesión automáticamente
async def get_db():
    """
    Obtiene una sesión de base de datos.
    USO: En los endpoints de FastAPI como dependencia.
    
    Ejemplo:
    @app.get("/items/")
    async def list_items(db: AsyncSession = Depends(get_db)):
        ...
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session  # Entrega la sesión al endpoint
        finally:
            await session.close()  # Cierra la sesión al terminar


# ============================================
# Inicialización de la base de datos
# ============================================
async def init_db():
    """
    Crea todas las tablas en la base de datos.
    Se ejecuta al arrancar la aplicación (evento startup).
    
    Base.metadata.create_all() examina TODOS los modelos que heredan de Base
    y crea las tablas que no existan todavía.
    """
    async with engine.begin() as conn:
        # create_all crea las tablas definidas en los modelos
        await conn.run_sync(Base.metadata.create_all)