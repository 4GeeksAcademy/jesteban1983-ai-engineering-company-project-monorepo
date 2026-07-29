"""
tests/test_passwords.py — Pruebas para endpoints de contraseña.

Cubre:
  - POST /auth/forgot-password
  - POST /auth/reset-password
  - POST /auth/change-password
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))


class TestForgotPassword:
    """Suite de pruebas para POST /auth/forgot-password."""

    URL = "/auth/forgot-password"

    def test_happy_path_email_exists(self, client, registered_user, sample_user_data):
        """
        Email existente → 200 (y se intenta enviar email).
        Mockeamos send_reset_email para no enviar emails reales.
        """
        with patch("routes.auth.send_reset_email") as mock_send:
            response = client.post(self.URL, json={"email": sample_user_data["email"]})
            assert response.status_code == 200
            data = response.json()
            assert "mensaje" in data.get("message", "").lower() or "Si esa dirección" in data.get("message", "")
            # Verificar que se intentó enviar el email
            mock_send.assert_called_once()

    def test_edge_case_email_not_exists(self, client):
        """
        Email no existente → 200 también (seguridad: no revelar existencia).
        """
        with patch("routes.auth.send_reset_email") as mock_send:
            response = client.post(self.URL, json={"email": "noexiste@trackflow.com"})
            assert response.status_code == 200
            # No debe llamar a send_reset_email si no existe el usuario
            mock_send.assert_not_called()

    def test_failure_empty_email(self, client):
        """Email vacío: pasa validación (str no EmailStr), no encuentra usuario, devuelve 200."""
        response = client.post(self.URL, json={"email": ""})
        # El modelo usa str, no EmailStr; endpoint SIEMPRE devuelve 200
        assert response.status_code == 200


class TestResetPassword:
    """Suite de pruebas para POST /auth/reset-password."""

    URL = "/auth/reset-password"

    def _create_password_reset_token(self, user_id: int) -> str:
        """Helper para crear un token de reset válido."""
        from services.auth_service import create_reset_token
        return create_reset_token(user_id)

    def test_happy_path_reset_success(self, client, registered_user):
        """
        Token de reset válido → contraseña cambiada exitosamente.
        """
        user_id = registered_user["id"]
        token = self._create_password_reset_token(user_id)

        response = client.post(self.URL, json={
            "token": token,
            "new_password": "NewSecurePass456!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "actualizada" in data.get("message", "").lower()

        # Verificar que la nueva contraseña funciona para login
        login_resp = client.post("/auth/login", json={
            "email": registered_user["email"],
            "password": "NewSecurePass456!",
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

    def test_failure_expired_token(self, client, registered_user):
        """
        Token de reset expirado → 400.
        Se genera un token con exp en el pasado (epoch=1).
        """
        from jose import jwt
        import os
        user_id = registered_user["id"]
        secret_key = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
        expired_token = jwt.encode(
            {
                "sub": str(user_id),
                "type": "password_reset",
                "exp": 1,  # 1 de enero de 1970 = ya expiró
            },
            secret_key,
            algorithm="HS256",
        )
        response = client.post(self.URL, json={
            "token": expired_token,
            "new_password": "NewSecurePass456!",
        })
        assert response.status_code == 400

    def test_failure_token_already_used(self, client, registered_user):
        """
        Token ya usado (anti-replay) → 400.
        """
        user_id = registered_user["id"]
        token = self._create_password_reset_token(user_id)

        # Primer uso: debe funcionar
        first = client.post(self.URL, json={
            "token": token,
            "new_password": "NewSecurePass456!",
        })
        assert first.status_code == 200

        # Segundo uso con el mismo token: debe fallar (anti-replay)
        second = client.post(self.URL, json={
            "token": token,
            "new_password": "AnotherPass789!",
        })
        assert second.status_code == 400
        data = second.json()
        detail = data.get("detail", {})
        detail_str = detail.get("detail", "") if isinstance(detail, dict) else str(detail)
        assert "ya ha sido utilizado" in detail_str.lower()

    def test_failure_invalid_token(self, client, invalid_token):
        """
        Token malformado → 400.
        """
        response = client.post(self.URL, json={
            "token": "token-completamente-invalido",
            "new_password": "NewSecurePass456!",
        })
        assert response.status_code == 400


class TestChangePassword:
    """Suite de pruebas para POST /auth/change-password."""

    URL = "/auth/change-password"

    def test_happy_path_change_success(self, client, auth_headers, sample_user_data):
        """
        Cambio exitoso cuando la contraseña actual es correcta.
        """
        response = client.post(self.URL, headers=auth_headers, json={
            "current_password": sample_user_data["password"],
            "new_password": "NewSecurePass456!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "actualizada" in data.get("message", "").lower()

        # Verificar que la nueva contraseña funciona para login
        login_resp = client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": "NewSecurePass456!",
        })
        assert login_resp.status_code == 200

    def test_failure_wrong_current_password(self, client, auth_headers, sample_user_data):
        """
        Contraseña actual incorrecta → 400.
        """
        response = client.post(self.URL, headers=auth_headers, json={
            "current_password": "WrongCurrentPass!",
            "new_password": "NewSecurePass456!",
        })
        assert response.status_code == 400
        data = response.json()
        detail = data.get("detail", {})
        detail_str = detail.get("detail", "") if isinstance(detail, dict) else str(detail)
        assert "incorrecta" in detail_str.lower()

    def test_edge_case_short_new_password(self, client, auth_headers, sample_user_data):
        """
        Nueva contraseña corta: el modelo no tiene min_length,
        así que la API la acepta y la hashea.
        """
        response = client.post(self.URL, headers=auth_headers, json={
            "current_password": sample_user_data["password"],
            "new_password": "abc12",  # 5 chars, pero no hay validación de min_length
        })
        # El endpoint acepta cualquier string
        assert response.status_code == 200

    def test_failure_no_auth(self, client):
        """
        Sin token de autenticación → 401.
        """
        response = client.post(self.URL, json={
            "current_password": "SomePass123!",
            "new_password": "NewPass456!",
        })
        assert response.status_code == 401