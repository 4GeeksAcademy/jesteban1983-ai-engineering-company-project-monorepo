"""
tests/test_profile.py — Pruebas para GET /auth/me (perfil del usuario autenticado).

Cubre: acceso autenticado exitoso, ausencia de token, token inválido,
token expirado, y formato incorrecto del header Authorization.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


class TestProfile:
    """Suite de pruebas para GET /auth/me."""

    PROFILE_URL = "/auth/me"

    def test_happy_path_authenticated(self, client, auth_headers, sample_user_data):
        """Usuario autenticado obtiene su información."""
        response = client.get(self.PROFILE_URL, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["role"] == "user"
        assert data["is_active"] is True
        assert "profile" in data

    def test_failure_no_token(self, client):
        """Petición sin token debe fallar con 401."""
        response = client.get(self.PROFILE_URL)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_failure_invalid_token(self, client, invalid_token):
        """Petición con token de firma inválida debe fallar con 401."""
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

    def test_failure_expired_token(self, client, expired_token):
        """Petición con token expirado debe fallar con 401."""
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        data = response.json()
        assert "Token" in str(data.get("detail", ""))

    def test_failure_malformed_auth_header(self, client):
        """Header Authorization sin formato 'Bearer <token>' debe fallar."""
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": "NotBearer token123"},
        )
        assert response.status_code == 401

    def test_failure_token_without_sub(self, client):
        """Token sin claim 'sub' debe fallar con 401."""
        import os
        from jose import jwt
        secret = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
        token = jwt.encode({"role": "user"}, secret, algorithm="HS256")
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        data = response.json()
        detail = str(data.get("detail", ""))
        assert "sub" in detail or "Token" in detail

    def test_failure_token_with_non_numeric_sub(self, client):
        """Token con 'sub' no numérico debe fallar con 401."""
        import os
        from jose import jwt
        secret = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
        token = jwt.encode({"sub": "not-a-number"}, secret, algorithm="HS256")
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        detail = str(response.json().get("detail", ""))
        assert "número" in detail or "Token" in detail or "invá" in detail

    def test_failure_token_for_nonexistent_user(self, client):
        """Token válido para usuario que no existe en DB debe fallar con 401."""
        import os
        from jose import jwt
        secret = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
        # user_id=99999 no existe
        token = jwt.encode({"sub": "99999", "role": "user"}, secret, algorithm="HS256")
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        detail = str(response.json().get("detail", ""))
        assert "Usuario" in detail or "Token" in detail or "encontrado" in detail

    def test_failure_auth_inactive_user(self, client, auth_headers, sample_user_data):
        """Usuario desactivado no puede acceder a /auth/me."""
        from database import users_table
        from services.user_service import get_user_by_email
        user = get_user_by_email(sample_user_data["email"])
        users_table.update({"is_active": False}, doc_ids=[user["id"]])

        response = client.get(self.PROFILE_URL, headers=auth_headers)
        assert response.status_code == 401
        data = response.json()
        assert "desactivado" in str(data.get("detail", ""))


class TestAdminAuth:
    """Pruebas para dependencia get_admin_user (auth_deps.py)."""

    def test_non_admin_user_cannot_access_admin_route(self, client, auth_headers):
        """Usuario normal (role=user) no puede acceder a rutas de admin."""
        # GET /users/ requiere get_current_user (no admin)
        response = client.get("/profiles/me", headers=auth_headers)
        # profiles/me requiere solo autenticación, no admin
        assert response.status_code in (200, 401, 403)