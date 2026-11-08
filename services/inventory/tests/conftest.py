# ============================================
# tests/conftest.py - Fixtures de prueba (configuración compartida)
# ============================================
# Los fixtures son funciones que se ejecutan antes de cada test.
# Preparan el entorno: base de datos, cliente HTTP, datos de prueba.
#
# pytest busca automáticamente este archivo y pone los fixtures
# disponibles para todos los tests.

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.base import Base
from app.database import get_db
from app.main import app

# ============================================
# Motor de base de datos para TESTS
# ============================================
# Usamos SQLite en MEMORIA para tests (rápido y aislado)
# Cada test session usa una BD limpia

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Creamos un motor específico para tests
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Fábrica de sesiones para tests
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ============================================
# Fixture: Crear tablas antes y limpiar después
# ============================================
@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture que provee una sesión de BD para tests.
    
    - Antes de cada test: crea todas las tablas
    - Después de cada test: cierra sesión y elimina tablas
    """
    # Setup: crear tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Proveer sesión
    async with TestSessionFactory() as session:
        yield session

    # Teardown: eliminar tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ============================================
# Fixture: Cliente HTTP para llamar a la API
# ============================================
@pytest_asyncio.fixture
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture que crea un cliente HTTP asíncrono.
    
    Reemplaza la dependencia get_db con nuestra sesión de test.
    Así los endpoints usan la BD de pruebas sin saberlo.
    """
    # ---- Sobrescribir la dependencia ----
    # Hacemos que cada petición use nuestra sesión de test
    async def _override_get_db():
        yield async_session

    # Reemplazamos la dependencia original con la de test
    app.dependency_overrides[get_db] = _override_get_db

    # ---- Crear cliente HTTP ----
    # ASGITransport permite llamar a FastAPI sin un servidor real
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # ---- Limpiar ----
    app.dependency_overrides.clear()


# ============================================
# Fixture: Datos de prueba (items de ejemplo)
# ============================================
@pytest_asyncio.fixture
async def sample_items(async_session: AsyncSession) -> list:
    """
    Crea items de ejemplo para usar en tests.
    """
    from app.models.inventory import Item
    from decimal import Decimal

    items_data = [
        Item(
            sku="CAM-001", name="Cámara DSLR",
            price=Decimal("599.99"), quantity=10,
            category="Electronics", warehouse="main",
            min_stock=5,
        ),
        Item(
            sku="TBL-002", name="Tablet Pro",
            price=Decimal("399.99"), quantity=3,
            category="Electronics", warehouse="main",
            min_stock=10,  # Low stock! (3 < 10)
        ),
        Item(
            sku="SHP-003", name="Zapatos Deportivos",
            price=Decimal("89.99"), quantity=50,
            category="Fashion", warehouse="main",
            min_stock=20,
        ),
    ]

    for item in items_data:
        async_session.add(item)
    
    await async_session.commit()

    # Refrescar para obtener IDs
    for item in items_data:
        await async_session.refresh(item)

    return items_data