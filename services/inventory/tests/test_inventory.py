# ============================================
# tests/test_inventory.py - Tests para la API de inventario
# ============================================
# Estos tests verifican que todos los endpoints funcionan correctamente.
# pytest ejecuta cada función que empieza con "test_".
#
# Para ejecutar: pytest tests/ -v
# -v = modo verbose (muestra nombre de cada test)

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================
# Tests de CREACIÓN de items
# ============================================

class TestCreateItem:
    """Tests para POST /api/v1/items/"""

    @pytest.mark.asyncio
    async def test_create_item_success(self, client: AsyncClient):
        """Debe crear un item correctamente y devolver 201"""
        response = await client.post("/api/v1/items/", json={
            "sku": "TEST-001",
            "name": "Item de prueba",
            "price": 29.99,
            "category": "Electronics",
            "quantity": 100,
        })
        # Verificar código de respuesta
        assert response.status_code == 201
        
        data = response.json()
        # Verificar que devuelve los datos correctos
        assert data["sku"] == "TEST-001"
        assert data["name"] == "Item de prueba"
        assert data["price"] == 29.99
        assert data["quantity"] == 100
        # Verificar que tiene ID asignado
        assert data["id"] is not None

    @pytest.mark.asyncio
    async def test_create_item_duplicate_sku(self, client: AsyncClient):
        """Crear item con SKU duplicado debe dar error 409"""
        # Crear primer item
        await client.post("/api/v1/items/", json={
            "sku": "DUP-001",
            "name": "Primero",
            "price": 10.0,
            "category": "Other",
        })
        # Intentar crear otro con el mismo SKU
        response = await client.post("/api/v1/items/", json={
            "sku": "DUP-001",
            "name": "Segundo (duplicado)",
            "price": 10.0,
            "category": "Other",
        })
        assert response.status_code == 409  # Conflict

    @pytest.mark.asyncio
    async def test_create_item_invalid_price(self, client: AsyncClient):
        """Precio negativo debe dar error de validación 422"""
        response = await client.post("/api/v1/items/", json={
            "sku": "INV-001",
            "name": "Precio inválido",
            "price": -5.0,  # ¡Negativo!
            "category": "Other",
        })
        assert response.status_code == 422  # Validation Error


# ============================================
# Tests de LECTURA de items
# ============================================

class TestGetItem:
    """Tests para GET /api/v1/items/ y GET /api/v1/items/{id}"""

    @pytest.mark.asyncio
    async def test_list_items_empty(self, client: AsyncClient):
        """Lista vacía debe devolver 0 items"""
        response = await client.get("/api/v1/items/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_get_item_not_found(self, client: AsyncClient):
        """Item que no existe debe devolver 404"""
        response = await client.get("/api/v1/items/99999")
        assert response.status_code == 404


# ============================================
# Tests de ACTUALIZACIÓN de items
# ============================================

class TestUpdateItem:
    """Tests para PUT /api/v1/items/{id}"""

    @pytest.mark.asyncio
    async def test_update_item_name(self, client: AsyncClient):
        """Actualizar solo el nombre debe funcionar"""
        # Crear item primero
        create_resp = await client.post("/api/v1/items/", json={
            "sku": "UPD-001",
            "name": "Nombre original",
            "price": 15.0,
            "category": "Test",
        })
        item_id = create_resp.json()["id"]

        # Actualizar solo el nombre
        response = await client.put(f"/api/v1/items/{item_id}", json={
            "name": "Nombre actualizado",
        })
        assert response.status_code == 200
        assert response.json()["name"] == "Nombre actualizado"


# ============================================
# Tests de ELIMINACIÓN (borrado lógico)
# ============================================

class TestDeleteItem:
    """Tests para DELETE /api/v1/items/{id}"""

    @pytest.mark.asyncio
    async def test_delete_item_soft_delete(self, client: AsyncClient):
        """Borrar item debe marcarlo como inactivo"""
        # Crear item
        create_resp = await client.post("/api/v1/items/", json={
            "sku": "DEL-001",
            "name": "A eliminar",
            "price": 5.0,
            "category": "Test",
        })
        item_id = create_resp.json()["id"]

        # Eliminar
        delete_resp = await client.delete(f"/api/v1/items/{item_id}")
        assert delete_resp.status_code == 200

        # Verificar que is_active = False
        get_resp = await client.get(f"/api/v1/items/{item_id}")
        assert get_resp.json()["is_active"] is False


# ============================================
# Tests de AJUSTE DE STOCK
# ============================================

class TestAdjustStock:
    """Tests para POST /api/v1/items/{id}/adjust-stock"""

    @pytest.mark.asyncio
    async def test_inbound_increases_stock(self, client: AsyncClient):
        """Entrada de stock debe aumentar la cantidad"""
        # Crear item con stock 10
        create_resp = await client.post("/api/v1/items/", json={
            "sku": "STK-001", "name": "Stock test",
            "price": 10.0, "category": "Test", "quantity": 10,
        })
        item_id = create_resp.json()["id"]

        # Entrada de 5 unidades
        adj_resp = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={"movement_type": "inbound", "quantity": 5, "reason": "Reposición"},
        )
        assert adj_resp.status_code == 200
        assert adj_resp.json()["quantity"] == 15  # 10 + 5

    @pytest.mark.asyncio
    async def test_outbound_decreases_stock(self, client: AsyncClient):
        """Salida de stock debe disminuir la cantidad"""
        create_resp = await client.post("/api/v1/items/", json={
            "sku": "STK-002", "name": "Stock out",
            "price": 10.0, "category": "Test", "quantity": 20,
        })
        item_id = create_resp.json()["id"]

        adj_resp = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={"movement_type": "outbound", "quantity": 7, "reason": "Venta"},
        )
        assert adj_resp.status_code == 200
        assert adj_resp.json()["quantity"] == 13  # 20 - 7

    @pytest.mark.asyncio
    async def test_insufficient_stock(self, client: AsyncClient):
        """Salida mayor que stock debe dar error 400"""
        create_resp = await client.post("/api/v1/items/", json={
            "sku": "STK-003", "name": "Stock bajo",
            "price": 10.0, "category": "Test", "quantity": 5,
        })
        item_id = create_resp.json()["id"]

        # Intentar sacar 10 cuando solo hay 5
        adj_resp = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={"movement_type": "outbound", "quantity": 10},
        )
        assert adj_resp.status_code == 400  # Bad Request


# ============================================
# Tests de MOVIMIENTOS (historial)
# ============================================

class TestMovements:
    """Tests para GET /api/v1/items/{id}/movements"""

    @pytest.mark.asyncio
    async def test_movements_history(self, client: AsyncClient):
        """Ajustar stock debe crear un movimiento"""
        create_resp = await client.post("/api/v1/items/", json={
            "sku": "MOV-001", "name": "Mov test",
            "price": 10.0, "category": "Test", "quantity": 10,
        })
        item_id = create_resp.json()["id"]

        # Hacer un ajuste
        await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={"movement_type": "inbound", "quantity": 5},
        )

        # Verificar que se creó el movimiento
        mov_resp = await client.get(f"/api/v1/items/{item_id}/movements")
        assert mov_resp.status_code == 200
        assert mov_resp.json()["total"] == 1
        assert mov_resp.json()["items"][0]["movement_type"] == "inbound"