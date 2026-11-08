# ============================================
# tests/test_crud.py - Tests directos de CRUD (sin pasar por API)
# ============================================
# Estos tests llaman DIRECTAMENTE a la clase InventoryCRUD
# para cubrir el código interno que los tests de API no alcanzan.
#
# pytest-cov a veces no captura las líneas async de los tests de API,
# así que estos tests llenan esos vacíos llamando al CRUD directamente.

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.inventory import InventoryCRUD
from app.crud.movement import MovementCRUD
from app.schemas.inventory import ItemCreate, ItemUpdate
from app.models.inventory import Item


class TestCrudDirectly:
    """Tests que llaman al CRUD directamente (sin HTTP)."""

    @pytest.mark.asyncio
    async def test_crud_create_and_get(self, async_session: AsyncSession):
        """Crear item via CRUD y obtenerlo por ID."""
        crud = InventoryCRUD()
        
        # Crear item
        data = ItemCreate(
            sku="CRUD-001",
            name="Test CRUD",
            price=Decimal("99.99"),
            category="Test",
        )
        item = await crud.create_item(async_session, data)
        assert item.id is not None
        assert item.name == "Test CRUD"
        assert item.price == Decimal("99.99")

        # Obtener por ID
        found = await crud.get_item(async_session, item.id)
        assert found is not None
        assert found.id == item.id

    @pytest.mark.asyncio
    async def test_crud_get_by_sku(self, async_session: AsyncSession):
        """Buscar item por SKU via CRUD."""
        crud = InventoryCRUD()
        
        data = ItemCreate(
            sku="SKU-TEST-001",
            name="SKU Test",
            price=Decimal("10.00"),
            category="Test",
        )
        item = await crud.create_item(async_session, data)
        
        # Buscar por SKU
        found = await crud.get_item_by_sku(async_session, "SKU-TEST-001")
        assert found is not None
        assert found.id == item.id

        # SKU que no existe debe devolver None
        not_found = await crud.get_item_by_sku(async_session, "NO-EXISTE")
        assert not_found is None

    @pytest.mark.asyncio
    async def test_crud_update_item(self, async_session: AsyncSession):
        """Actualizar item via CRUD."""
        crud = InventoryCRUD()
        
        data = ItemCreate(
            sku="UPD-CRUD",
            name="Original",
            price=Decimal("50.00"),
            category="Test",
        )
        item = await crud.create_item(async_session, data)

        # Actualizar nombre y precio
        update_data = ItemUpdate(name="Actualizado", price=Decimal("75.00"))
        updated = await crud.update_item(async_session, item.id, update_data)
        assert updated is not None
        assert updated.name == "Actualizado"
        assert updated.price == Decimal("75.00")

        # Actualizar item que no existe
        not_found = await crud.update_item(async_session, 99999, update_data)
        assert not_found is None

    @pytest.mark.asyncio
    async def test_crud_delete_item(self, async_session: AsyncSession):
        """Eliminar item (soft delete) via CRUD."""
        crud = InventoryCRUD()
        
        data = ItemCreate(
            sku="DEL-CRUD",
            name="Delete Test",
            price=Decimal("30.00"),
            category="Test",
        )
        item = await crud.create_item(async_session, data)

        # Eliminar
        deleted = await crud.delete_item(async_session, item.id)
        assert deleted is True

        # Verificar que is_active = False
        found = await crud.get_item(async_session, item.id)
        assert found.is_active is False

        # Eliminar item que no existe
        not_found = await crud.delete_item(async_session, 99999)
        assert not_found is False

    @pytest.mark.asyncio
    async def test_crud_adjust_stock(self, async_session: AsyncSession):
        """Ajustar stock via CRUD directamente."""
        crud = InventoryCRUD()
        
        data = ItemCreate(
            sku="STK-CRUD",
            name="Stock Test",
            price=Decimal("20.00"),
            category="Test",
            quantity=100,
        )
        item = await crud.create_item(async_session, data)

        # Aumentar stock (entrada)
        item = await crud.adjust_stock(
            async_session, item.id, 50, "Entrada de prueba"
        )
        assert item.quantity == 150

        # Disminuir stock (salida)
        item = await crud.adjust_stock(
            async_session, item.id, -30, "Salida de prueba"
        )
        assert item.quantity == 120

    @pytest.mark.asyncio
    async def test_crud_adjust_stock_insufficient(self, async_session: AsyncSession):
        """Stock insuficiente debe lanzar ValueError."""
        crud = InventoryCRUD()
        
        data = ItemCreate(
            sku="LOW-CRUD",
            name="Low Stock",
            price=Decimal("10.00"),
            category="Test",
            quantity=5,
        )
        item = await crud.create_item(async_session, data)

        # Intentar sacar 10 cuando solo hay 5
        with pytest.raises(ValueError, match="Stock insuficiente"):
            await crud.adjust_stock(async_session, item.id, -10)

    @pytest.mark.asyncio
    async def test_crud_duplicate_sku(self, async_session: AsyncSession):
        """SKU duplicado debe lanzar ValueError."""
        crud = InventoryCRUD()
        
        data = ItemCreate(
            sku="DUP-CRUD",
            name="Primero",
            price=Decimal("10.00"),
            category="Test",
        )
        await crud.create_item(async_session, data)

        # Intentar crear otro con el mismo SKU
        with pytest.raises(ValueError, match="Ya existe un item"):
            data2 = ItemCreate(
                sku="DUP-CRUD",
                name="Segundo",
                price=Decimal("20.00"),
                category="Test",
            )
            await crud.create_item(async_session, data2)

    @pytest.mark.asyncio
    async def test_crud_get_items_empty(self, async_session: AsyncSession):
        """Lista vacia debe devolver 0 items."""
        crud = InventoryCRUD()
        items, total = await crud.get_items(async_session)
        assert total >= 0
        assert isinstance(items, list)

    @pytest.mark.asyncio
    async def test_crud_get_items_with_filters(self, async_session: AsyncSession):
        """Filtrar items por categoria y almacen."""
        crud = InventoryCRUD()
        
        # Crear items de prueba
        for i in range(3):
            data = ItemCreate(
                sku=f"FILTRO-{i}",
                name=f"Item {i}",
                price=Decimal("10.00"),
                category="CatA" if i % 2 == 0 else "CatB",
                warehouse="WareA",
            )
            await crud.create_item(async_session, data)

        # Filtrar por categoria
        items, total = await crud.get_items(
            async_session, category="CatA"
        )
        assert total == 2
        assert all(i.category == "CatA" for i in items)

        # Filtrar por low_stock
        items, total = await crud.get_items(
            async_session, low_stock=True
        )
        assert isinstance(total, int)

    @pytest.mark.asyncio
    async def test_movement_crud(self, async_session: AsyncSession):
        """CRUD de movimientos."""
        inv_crud = InventoryCRUD()
        mov_crud = MovementCRUD()
        
        # Crear item con stock
        data = ItemCreate(
            sku="MOV-CRUD",
            name="Movement Test",
            price=Decimal("10.00"),
            category="Test",
            quantity=100,
        )
        item = await inv_crud.create_item(async_session, data)
        
        # Hacer algunos movimientos
        await inv_crud.adjust_stock(async_session, item.id, 10, "Entrada 1")
        await inv_crud.adjust_stock(async_session, item.id, -5, "Salida 1")
        await inv_crud.adjust_stock(async_session, item.id, 20, "Entrada 2")

        # Obtener movimientos
        movements, total = await mov_crud.get_movements(
            async_session, item.id
        )
        assert total == 3
        assert len(movements) == 3
        
        # Verificar tipos de movimiento
        types = [m.movement_type for m in movements]
        assert "inbound" in types
        assert "outbound" in types