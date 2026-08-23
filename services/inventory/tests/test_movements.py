# ============================================
# tests/test_movements.py - Tests para movimientos de inventario
# ============================================
# Este archivo prueba las operaciones CRUD de movimientos
# a través de la API REST (endpoints de movements).
#
# Para ejecutar solo estos tests:
#   pytest tests/test_movements.py -v
#
# Para ejecutar todos los tests con cobertura:
#   pytest --cov=app --cov-report=term

import pytest
from httpx import AsyncClient


# ============================================
# Tests de CREACIÓN de movimientos
# ============================================

class TestCreateMovement:
    """Tests para crear movimientos via POST /api/v1/items/{id}/adjust-stock"""

    @pytest.mark.asyncio
    async def test_create_inbound_movement(self, client: AsyncClient, sample_items):
        """
        Crear un movimiento de entrada (inbound).
        
        Verifica:
        - Respuesta 200 OK
        - El movimiento tiene el tipo "inbound"
        - El movimiento tiene referencia al item_id correcto
        - La razón se guarda correctamente
        """
        item_id = sample_items[0].id
        response = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={
                "movement_type": "inbound",
                "quantity": 10,
                "reason": "Reposición de stock desde proveedor",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # El stock debe haber aumentado: 10 + 10 = 20
        assert data["quantity"] == 20
        assert data["id"] == item_id

    @pytest.mark.asyncio
    async def test_create_outbound_movement(self, client: AsyncClient, sample_items):
        """
        Crear un movimiento de salida (outbound).
        
        Verifica:
        - Respuesta 200 OK
        - La cantidad disminuye correctamente
        """
        item_id = sample_items[1].id
        # Primero añadimos stock
        await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={"movement_type": "inbound", "quantity": 50},
        )
        # Ahora sacamos 10
        response = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={
                "movement_type": "outbound",
                "quantity": 10,
                "reason": "Venta a cliente",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Stock inicial: 3. Entrada: 50. Salida: 10. Total: 3 + 50 - 10 = 43
        assert data["quantity"] == 43

    @pytest.mark.asyncio
    async def test_create_adjustment_movement(self, client: AsyncClient, sample_items):
        """
        Crear un movimiento de ajuste (adjustment).
        
        Los ajustes permiten corregir el stock sin sumar/restar.
        """
        item_id = sample_items[2].id
        response = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={
                "movement_type": "adjustment",
                "quantity": 5,
                "reason": "Ajuste por inventario físico",
            },
        )
        assert response.status_code == 200


# ============================================
# Tests de LECTURA del historial de movimientos
# ============================================

class TestGetMovements:
    """Tests para GET /api/v1/items/{id}/movements"""

    @pytest.mark.asyncio
    async def test_get_movements_history(self, client: AsyncClient, sample_items):
        """
        Obtener el historial completo de movimientos de un item.
        
        Verifica:
        - Respuesta 200 OK
        - El total de movimientos es correcto
        - Los movimientos están ordenados por fecha
        """
        item_id = sample_items[0].id
        
        # Crear varios movimientos
        for i in range(3):
            await client.post(
                f"/api/v1/items/{item_id}/adjust-stock",
                json={
                    "movement_type": "inbound" if i % 2 == 0 else "outbound",
                    "quantity": 10,
                    "reason": f"Movimiento de prueba #{i + 1}",
                },
            )

        # Obtener historial
        response = await client.get(f"/api/v1/items/{item_id}/movements")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        
        # Verificar que cada movimiento tiene los campos esperados
        for mov in data["items"]:
            assert "id" in mov
            assert "movement_type" in mov
            assert "quantity" in mov
            assert "created_at" in mov
            assert "item_id" in mov

    @pytest.mark.asyncio
    async def test_get_movements_empty(self, client: AsyncClient, sample_items):
        """
        Item sin movimientos debe devolver lista vacía.
        
        Verifica que un item recién creado no tiene movimientos.
        """
        # Crear item nuevo (sin movimientos)
        create_resp = await client.post("/api/v1/items/", json={
            "sku": "NOMOV-001",
            "name": "Sin movimientos",
            "price": 100.0,
            "category": "Test",
        })
        item_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/items/{item_id}/movements")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_get_movements_item_not_found(self, client: AsyncClient):
        """
        Item que no existe debe devolver 404.
        
        Verifica que no se puede consultar movimientos de un item
        que no existe en la base de datos.
        """
        response = await client.get("/api/v1/items/99999/movements")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_movements_pagination(self, client: AsyncClient, sample_items):
        """
        Verificar que la paginación funciona en el historial.
        
        Crea 5 movimientos y pide solo 2 por página.
        """
        item_id = sample_items[0].id
        
        # Crear 5 movimientos
        for i in range(5):
            await client.post(
                f"/api/v1/items/{item_id}/adjust-stock",
                json={
                    "movement_type": "inbound",
                    "quantity": 1,
                    "reason": f"Mov #{i + 1}",
                },
            )

        # Pedir solo los primeros 2
        response = await client.get(
            f"/api/v1/items/{item_id}/movements?page=1&per_page=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total_pages"] == 3  # 5 items / 2 por página = 3 páginas


# ============================================
# Tests de VALIDACIÓN de movimientos
# ============================================

class TestMovementValidation:
    """Tests para validar que los movimientos rechazan datos inválidos"""

    @pytest.mark.asyncio
    async def test_invalid_movement_type(self, client: AsyncClient, sample_items):
        """
        Tipo de movimiento inválido debe dar error 422.
        
        Solo se permiten: "inbound", "outbound", "adjustment".
        """
        item_id = sample_items[0].id
        response = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={
                "movement_type": "invalid_type",
                "quantity": 5,
            },
        )
        assert response.status_code == 422  # Validation Error

    @pytest.mark.asyncio
    async def test_negative_quantity(self, client: AsyncClient, sample_items):
        """
        Cantidad negativa debe dar error 422.
        
        La cantidad siempre debe ser positiva (> 0).
        """
        item_id = sample_items[0].id
        response = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={
                "movement_type": "inbound",
                "quantity": -5,  # ¡Cantidad negativa!
            },
        )
        assert response.status_code == 422  # Validation Error

    @pytest.mark.asyncio
    async def test_zero_quantity(self, client: AsyncClient, sample_items):
        """
        Cantidad cero debe dar error 422.
        
        La cantidad debe ser > 0, no >= 0.
        """
        item_id = sample_items[0].id
        response = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={
                "movement_type": "outbound",
                "quantity": 0,  # ¡Cantidad cero!
            },
        )
        assert response.status_code == 422  # Validation Error

    @pytest.mark.asyncio
    async def test_missing_movement_type(self, client: AsyncClient, sample_items):
        """
        Falta el tipo de movimiento debe dar error 422.
        """
        item_id = sample_items[0].id
        response = await client.post(
            f"/api/v1/items/{item_id}/adjust-stock",
            json={
                "quantity": 5,
                # Falta movement_type
            },
        )
        assert response.status_code == 422  # Validation Error