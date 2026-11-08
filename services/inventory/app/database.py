# ============================================
# database.py - Conexión a la base de datos (SQLite/PostgreSQL)
# ============================================
# Este archivo configura la conexión a la base de datos usando SQLAlchemy.
# Soporta DOS motores de base de datos:
# - SQLite (aiosqlite) para desarrollo local
# - PostgreSQL (asyncpg) para producción
#
# NOTA: Para PostgreSQL en Supabase, SSL está habilitado por defecto.
#
# La diferencia la hace la variable DATABASE_URL en .env

import ssl

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,      # Sesión asíncrona para hacer consultas
    async_sessionmaker, # Fábrica que crea sesiones asíncronas
    create_async_engine, # Crea el motor de base de datos asíncrono
)
from app.base import Base
from app.config import settings  # Importamos la configuración con DATABASE_URL


# ============================================
# Configurar SSL para PostgreSQL
# ============================================
# Supabase y la mayoría de servicios PostgreSQL en la nube exigen SSL.
# asyncpg requiere connect_args con un ssl.SSLContext o el string "require".

def _get_ssl_context() -> ssl.SSLContext | str | None:
    """
    Retorna un contexto SSL si la conexión es PostgreSQL.
    
    - Para PostgreSQL/Supabase: retorna ssl_context con modo "require"
    - Para SQLite: retorna None (no aplica)
    
    Usa la configuración db_ssl_mode del .env para personalizar.
    """
    # Si es SQLite, no necesita SSL
    if "sqlite" in settings.database_url:
        return None
    
    # Para PostgreSQL, crear contexto SSL
    ssl_mode = settings.db_ssl_mode.lower()
    
    if ssl_mode == "disable":
        return None
    
    if ssl_mode == "require":
        # Crea un contexto SSL básico con "require" (no verifica certificado)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    
    if ssl_mode == "verify-full":
        # Verifica certificado (más seguro, requiere CA configurada)
        return ssl.create_default_context()
    
    # Por defecto, modo "prefer" = SSL si el servidor lo soporta
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


# ============================================
# Motor de base de datos (Engine)
# ============================================
# El engine es el objeto principal que maneja la conexión a la BD.
# create_async_engine crea un motor ASÍNCRONO = no bloquea el código
# mientras espera respuesta de la base de datos.

# Obtener contexto SSL según el tipo de BD
ssl_context = _get_ssl_context()
connect_args = {}
if ssl_context is not None:
    connect_args["ssl"] = ssl_context

engine = create_async_engine(
    settings.database_url,  # Ej: "sqlite+aiosqlite:///./dev.db"
    echo=False,             # True = muestra todas las consultas SQL (útil para debugging)
    connect_args=connect_args,  # SSL para PostgreSQL, vacío para SQLite
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
async def check_db_connection():
    """
    Verifica que la conexión a la base de datos responda.
    
    Ejecuta SELECT 1 y lanza una excepción si no hay respuesta.
    Esto evita que la app arranque con una BD caída o mal configurada.
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            if result.scalar() != 1:
                raise ConnectionError("La base de datos no respondió correctamente")
        print(f"✅ Conexión a BD verificada: {settings.database_url}")
    except Exception as e:
        print(f"❌ Error de conexión a BD: {e}")
        print(f"   URL: {settings.database_url}")
        raise ConnectionError(
            f"No se puede conectar a la base de datos: {e}"
        )


async def init_db():
    """
    Crea todas las tablas en la base de datos.
    Se ejecuta al arrancar la aplicación (evento startup).
    """
    async with engine.begin() as conn:
        # create_all crea las tablas definidas en los modelos
        await conn.run_sync(Base.metadata.create_all)