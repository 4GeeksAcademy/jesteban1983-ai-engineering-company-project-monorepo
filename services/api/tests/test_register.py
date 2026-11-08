"""
tests/test_register.py — Pruebas para POST /users/ (registro de usuario).

Cubre: registro exitoso, email duplicado, campos inválidos.

Nota: El registro de usuarios se realiza en POST /users/, no en /auth/register.
El endpoint /users/ redirige a register_user() que llama a create_user().
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class TestRegister:
    """Suite de pruebas para POST /users/ — Registro de usuario."""

    REGISTER_URL = "/users/"

    def test_happy_path_register_success(self, client):
        """Registro exitoso con datos válidos."""
        response = client.post(self.REGISTER_URL, json={
            "email": "newuser@trackflow.com",
            "password": "SecurePass123!",
            "name": "New User",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@trackflow.com"
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "id" in data
        assert "hashed_password" not in data  # No exponer hash

    def test_edge_case_duplicate_email(self, client):
        """Registrar con email duplicado debe fallar con 409."""
        # Primer registro
        first = client.post(self.REGISTER_URL, json={
            "email": "dup@trackflow.com",
            "password": "SecurePass123!",
            "name": "First",
        })
        assert first.status_code == 200

        # Segundo registro con mismo email
        second = client.post(self.REGISTER_URL, json={
            "email": "dup@trackflow.com",
            "password": "AnotherPass123!",
            "name": "Second",
        })
        assert second.status_code == 409
        # safe_error envuelve detail en un dict
        detail = second.json().get("detail", {})
        if isinstance(detail, dict):
            assert "ya está registrado" in detail.get("detail", "")
        elif isinstance(detail, str):
            assert "ya está registrado" in detail

    def test_failure_short_password(self, client):
        """Contraseña con menos de 6 caracteres debe fallar."""
        response = client.post(self.REGISTER_URL, json={
            "email": "shortpw@trackflow.com",
            "password": "abc12",  # 5 chars, min_length=6
            "name": "Short PW",
        })
        assert response.status_code == 422  # Validation error de Pydantic

    def test_failure_empty_email(self, client):
        """Email vacío debe fallar con 422."""
        response = client.post(self.REGISTER_URL, json={
            "email": "",
            "password": "SecurePass123!",
            "name": "No Email",
        })
        assert response.status_code == 422

    def test_failure_malformed_email(self, client):
        """Email sin @ debe fallar con 422."""
        response = client.post(self.REGISTER_URL, json={
            "email": "not-an-email",
            "password": "SecurePass123!",
            "name": "Bad Email",
        })
        assert response.status_code == 422

    def test_failure_missing_password(self, client):
        """Sin campo password debe fallar con 422."""
        response = client.post(self.REGISTER_URL, json={
            "email": "nopass@trackflow.com",
            "name": "No Password",
        })
        assert response.status_code == 422