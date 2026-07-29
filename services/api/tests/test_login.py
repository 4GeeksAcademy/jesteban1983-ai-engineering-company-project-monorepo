"""
tests/test_login.py — Pruebas para POST /auth/login.

Cubre: login exitoso, credenciales incorrectas, emails no existentes,
usuarios desactivados, y campos vacíos.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class TestLogin:
    """Suite de pruebas para POST /auth/login."""

    LOGIN_URL = "/auth/login"

    def test_happy_path_login_success(self, client, registered_user, sample_user_data):
        """Login exitoso devuelve access_token."""
        response = client.post(self.LOGIN_URL, json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20

    def test_failure_wrong_password(self, client, registered_user, sample_user_data):
        """Login con contraseña incorrecta debe fallar con 401."""
        response = client.post(self.LOGIN_URL, json={
            "email": sample_user_data["email"],
            "password": "WrongPassword456!",
        })
        assert response.status_code == 401
        data = response.json()
        assert "Credenciales inválidas" in str(data.get("detail", ""))

    def test_failure_email_not_found(self, client):
        """Login con email no registrado debe fallar con 401."""
        response = client.post(self.LOGIN_URL, json={
            "email": "nonexistent@trackflow.com",
            "password": "SomePass123!",
        })
        assert response.status_code == 401
        data = response.json()
        assert "Credenciales inválidas" in str(data.get("detail", ""))

    def test_failure_empty_email(self, client):
        """Login con email vacío debe fallar con 422 (validación Pydantic)."""
        response = client.post(self.LOGIN_URL, json={
            "email": "",
            "password": "SomePass123!",
        })
        assert response.status_code == 422

    def test_failure_empty_password(self, client, registered_user, sample_user_data):
        """Login con password vacío → 401 (verify_password falla)."""
        response = client.post(self.LOGIN_URL, json={
            "email": sample_user_data["email"],
            "password": "",
        })
        # Pydantic acepta string vacío, pero verify_password devuelve False → 401
        assert response.status_code == 401

    def test_failure_inactive_user(self, client, registered_user, sample_user_data):
        """Login de usuario desactivado debe fallar con 401."""
        from database import users_table
        # Buscar el ID del usuario registrado para desactivarlo
        from services.user_service import get_user_by_email
        user = get_user_by_email(sample_user_data["email"])
        users_table.update({"is_active": False}, doc_ids=[user["id"]])
        response = client.post(self.LOGIN_URL, json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        })
        assert response.status_code == 401
        data = response.json()
        assert "desactivado" in str(data.get("detail", ""))