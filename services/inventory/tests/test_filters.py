# ============================================
# tests/test_filters.py - Tests de filtros y búsqueda
# ============================================
# Este archivo prueba las operaciones de filtrado en la API
# que no están cubiertas por los tests básicos.
#
# Incluye:
# - Filtros por categoría, almacén, estado activo
# - Búsqueda por texto (SKU, nombre)
# - Filtro de stock bajo (low_stock)
# - Paginación
# - Combinaciones de filtros

import pytest
from httpx import AsyncClient


class TestItemFilters:
    """Tests para filtros en GET /api/v1/items/"""

    @pytest.mark.asyncio
    async def test_filter_by_category(self, client: AsyncClient, sample_items):
        """Filtrar items por categoría debe devolver solo los de esa categoría."""
        # sample_items tiene 3 items en categorías:
        # - 2 en "Electronics" (CAM-001, TBL-002)
        # - 1 en "Fashion" (SHP-003)
        response = await client.get("/api/v1/items/?category=Electronics")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["category"] == "Electronics"

        # Filtrar por Office debe devolver 1
        response = await client.get("/api/v1/items/?category=Fashion")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "Fashion"

    @pytest.mark.asyncio
    async def test_filter_by_warehouse(self, client: AsyncClient, sample_items):
        """Filtrar items por almacén."""
        # sample_items: los 3 estan en "main"
        response = await client.get("/api/v1/items/?warehouse=main")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for item in data["items"]:
            assert item["warehouse"] == "main"

    @pytest.mark.asyncio
    async def test_filter_by_is_active(self, client: AsyncClient, sample_items):
        """Filtrar items activos/inactivos."""
        # Primero desactivar un item
        item_id = sample_items[0].id
        await client.delete(f"/api/v1/items/{item_id}")

        # Ahora filtrar solo inactivos
        response = await client.get("/api/v1/items/?is_active=false")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for item in data["items"]:
            assert item["is_active"] is False

    @pytest.mark.asyncio
    async def test_search_by_sku(self, client: AsyncClient, sample_items):
        """Buscar items por SKU (búsqueda parcial)."""
        response = await client.get("/api/v1/items/?search=CAM")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "CAM-001"

    @pytest.mark.asyncio
    async def test_search_by_name(self, client: AsyncClient, sample_items):
        """Buscar items por nombre (búsqueda parcial)."""
        response = await client.get("/api/v1/items/?search=Tablet")
        assert response.status_code == 200
        data = response.json()
        # "Tablet Pro" contiene "Tablet"
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "TBL-002"

    @pytest.mark.asyncio
    async def test_search_no_results(self, client: AsyncClient, sample_items):
        """Búsqueda sin resultados debe devolver lista vacía."""
        response = await client.get("/api/v1/items/?search=ZZZZNOEXISTE")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_filter_low_stock(self, client: AsyncClient, sample_items):
        """Filtrar items con stock bajo (quantity < min_stock)."""
        # sample_items[1] (TBL-002) tiene quantity=3, min_stock=10
        # sample_items[2] (PAP-003) tiene quantity=25, min_stock=5
        # Solo TBL-002 tiene stock bajo
        response = await client.get("/api/v1/items/?low_stock=true")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "TBL-002"

    @pytest.mark.asyncio
    async def test_pagination_second_page(self, client: AsyncClient, sample_items):
        """Paginar: segunda página con per_page=2."""
        response = await client.get("/api/v1/items/?page=2&per_page=2")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["per_page"] == 2
        # Con 3 items totales y 2 por página, página 2 tiene 1 item
        assert len(data["items"]) == 1
        assert data["total_pages"] == 2

    @pytest.mark.asyncio
    async def test_combined_filters(self, client: AsyncClient, sample_items):
        """Combinar múltiples filtros a la vez."""
        response = await client.get(
            "/api/v1/items/?category=Electronics&warehouse=main&low_stock=true"
        )
        assert response.status_code == 200
        data = response.json()
        # Solo TBL-002 cumple: Electronics, main, low_stock
        assert data["total"] == 1
        assert data["items"][0]["sku"] == "TBL-002"


class TestItemEdgeCases:
    """Tests para casos borde de la API de items."""

    @pytest.mark.asyncio
    async def test_create_item_with_minimal_data(self, client: AsyncClient):
        """Crear item solo con campos obligatorios (usa valores por defecto)."""
        response = await client.post("/api/v1/items/", json={
            "sku": "MIN-001",
            "name": "Mínimo",
            "price": 1.99,
            "category": "Test",
            # Sin quantity (default 0), warehouse (default ""), min_stock (default 0)
        })
        assert response.status_code == 201
        data = response.json()
        assert data["quantity"] == 0
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_item_very_long_name(self, client: AsyncClient):
        """Nombre muy largo debe funcionar (hasta 200 caracteres)."""
        long_name = "A" * 200
        response = await client.post("/api/v1/items/", json={
            "sku": "LONG-001",
            "name": long_name,
            "price": 10.0,
            "category": "Test",
        })
        assert response.status_code == 201
        assert response.json()["name"] == long_name

    @pytest.mark.asyncio
    async def test_update_item_not_found(self, client: AsyncClient):
        """Actualizar item que no existe debe devolver 404."""
        response = await client.put("/api/v1/items/99999", json={"name": "Nuevo"})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_item_all_fields(self, client: AsyncClient):
        """Actualizar todos los campos de un item."""
        create_resp = await client.post("/api/v1/items/", json={
            "sku": "ALL-001",
            "name": "Original",
            "price": 10.0,
            "category": "Test",
            "quantity": 5,
            "warehouse": "A",
            "min_stock": 2,
        })
        item_id = create_resp.json()["id"]

        response = await client.put(f"/api/v1/items/{item_id}", json={
            "name": "Actualizado",
            "description": "Nueva descripción",
            "price": 15.50,
            "category": "NuevaCat",
            "quantity": 10,
            "warehouse": "B",
            "min_stock": 5,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Actualizado"
        assert data["description"] == "Nueva descripción"
        assert data["price"] == 15.50
        assert data["category"] == "NuevaCat"
        assert data["quantity"] == 10
        assert data["warehouse"] == "B"
        assert data["min_stock"] == 5

    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, client: AsyncClient):
        """Eliminar item que no existe debe devolver 404."""
        response = await client.delete("/api/v1/items/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_item_default_values(self, client: AsyncClient):
        """Verificar valores por defecto al crear item."""
        response = await client.post("/api/v1/items/", json={
            "sku": "DEF-001",
            "name": "Defaults",
            "price": 25.0,
            "category": "Test",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None
        assert data["warehouse"] == "main"
        assert data["min_stock"] == 10
        assert data["is_active"] is True


class TestHealthEndpoint:
    """Tests para el endpoint de salud GET /health"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """El endpoint /health debe responder OK."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app"] == "TrackFlow Inventory API"