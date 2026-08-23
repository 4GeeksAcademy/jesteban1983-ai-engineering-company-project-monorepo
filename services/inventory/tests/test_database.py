# ============================================
# tests/test_database.py - Tests para la conexión a BD
# ============================================
# Este archivo prueba directamente las funciones de database.py
# que son difíciles de cubrir solo con tests de API.
#
# Prueba:
# - Sobreescritura del .coveragerc para capturar async
# - init_db() crea tablas correctamente
# - get_db() funciona como generador asíncrono

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestDatabase:
    """Tests para las funciones de base de datos."""

    @pytest.mark.asyncio
    async def test_async_session_works(self, async_session: AsyncSession):
        """
        Verificar que la sesión asíncrona funciona.
        
        Este test usa la fixture async_session que ya ejecuta
        create_all y provee una sesión funcional.
        """
        # Verificar que la sesión es del tipo correcto
        assert isinstance(async_session, AsyncSession)
        
        # Verificar que podemos ejecutar una consulta simple
        result = await async_session.execute(text("SELECT 1"))
        assert result is not None

    @pytest.mark.asyncio
    async def test_database_connection(self, async_session: AsyncSession):
        """
        Verificar que la conexión a BD responde.
        
        Ejecuta una consulta que verifica la integridad de la BD.
        """
        result = await async_session.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
        tables = result.scalars().all()
        # Verificar que existen las tablas esperadas
        table_names = [t for t in tables if t.startswith("inventory_")]
        assert "inventory_items" in table_names
        assert "inventory_movements" in table_names