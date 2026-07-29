"""
tests/test_security.py — Pruebas unitarias para funciones de seguridad.

Cubre las funciones en services/auth_service.py:
  - create_access_token()
  - verify_password() / hash_password()
  - create_reset_token() / verify_reset_token()
  - invalidate_reset_token() / is_token_invalidated()

NO prueba serialización HTTP. Prueba la lógica de negocio.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["RESET_TOKEN_EXPIRE_MINUTES"] = "30"

from services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
    create_reset_token,
    verify_reset_token,
    invalidate_reset_token,
    is_token_invalidated,
    decode_access_token,
)

TEST_USER_ID = 1


# ═══════════════════════════════════════════════════════════════
# create_access_token
# ═══════════════════════════════════════════════════════════════

class TestCreateAccessToken:
    """Pruebas unitarias para create_access_token()."""

    def test_happy_path_creates_valid_token(self):
        """Crea un token con datos válidos y se puede decodificar."""
        token = create_access_token({"sub": str(TEST_USER_ID), "role": "user"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(TEST_USER_ID)
        assert payload["role"] == "user"
        assert "exp" in payload

    def test_edge_case_empty_data(self):
        """Crea un token incluso con datos vacíos."""
        token = create_access_token({})
        assert token is not None
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload

    def test_edge_case_multiple_fields(self):
        """Crea un token con múltiples claims personalizados."""
        token = create_access_token({
            "sub": "42",
            "role": "admin",
            "email": "admin@trackflow.com",
            "custom": "value",
        })
        payload = decode_access_token(token)
        assert payload["role"] == "admin"
        assert payload["email"] == "admin@trackflow.com"
        assert payload["custom"] == "value"


# ═══════════════════════════════════════════════════════════════
# hash_password / verify_password
# ═══════════════════════════════════════════════════════════════

class TestPasswordHashing:
    """Pruebas unitarias para hash_password() y verify_password()."""

    def test_happy_path_verify_correct_password(self):
        """Contraseña correcta verifica OK contra su hash."""
        password = "SecurePass123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_failure_wrong_password(self):
        """Contraseña incorrecta no verifica contra el hash."""
        hashed = hash_password("SecurePass123!")
        assert verify_password("WrongPass123!", hashed) is False

    def test_edge_case_empty_password(self):
        """Hash de contraseña vacía se genera correctamente."""
        hashed = hash_password("")
        assert isinstance(hashed, str)
        assert len(hashed) > 10
        assert verify_password("", hashed) is True

    def test_edge_case_very_long_password(self):
        """Contraseña muy larga (100+ chars) se maneja correctamente."""
        long_pw = "a" * 200
        hashed = hash_password(long_pw)
        assert verify_password(long_pw, hashed) is True


# ═══════════════════════════════════════════════════════════════
# create_reset_token / verify_reset_token
# ═══════════════════════════════════════════════════════════════

class TestResetToken:
    """Pruebas unitarias para create_reset_token() y verify_reset_token()."""

    def test_happy_path_create_and_verify_reset_token(self):
        """Crea un token de reset y lo verifica correctamente."""
        token = create_reset_token(TEST_USER_ID)
        assert token is not None
        user_id = verify_reset_token(token)
        assert user_id == TEST_USER_ID

    def test_failure_expired_reset_token(self):
        """Token de reset expirado devuelve None.
        Se genera un token con exp en el pasado (epoch=1).
        """
        from jose import jwt
        import os
        secret_key = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
        expired_token = jwt.encode(
            {
                "sub": str(TEST_USER_ID),
                "type": "password_reset",
                "exp": 1,  # 1 de enero de 1970 = ya expiró
            },
            secret_key,
            algorithm="HS256",
        )
        assert verify_reset_token(expired_token) is None

    def test_failure_invalid_signature(self):
        """Token de reset con firma inválida devuelve None."""
        from jose import jwt
        fake_token = jwt.encode(
            {"sub": str(TEST_USER_ID), "type": "password_reset"},
            "wrong-secret-key",
            algorithm="HS256",
        )
        assert verify_reset_token(fake_token) is None

    def test_failure_wrong_token_type(self):
        """Token de reset con type incorrecto devuelve None."""
        from services.auth_service import create_access_token
        access_token = create_access_token({"sub": str(TEST_USER_ID)})
        # Este token tiene type='access' o ninguno, no 'password_reset'
        assert verify_reset_token(access_token) is None

    def test_edge_case_non_existent_user_id(self):
        """Token de reset con user_id 99999 se decodifica correctamente (no verifica existencia)."""
        token = create_reset_token(99999)
        user_id = verify_reset_token(token)
        assert user_id == 99999  # La función decodifica, no verifica existencia en DB


# ═══════════════════════════════════════════════════════════════
# invalidate_reset_token / is_token_invalidated  (anti-replay)
# ═══════════════════════════════════════════════════════════════

class TestTokenInvalidation:
    """Pruebas unitarias para invalidate_reset_token() y is_token_invalidated()."""

    def test_happy_path_token_not_invalidated(self):
        """Token nuevo no está invalidado."""
        token = create_reset_token(TEST_USER_ID)
        assert is_token_invalidated(token) is False

    def test_happy_path_invalidate_token(self):
        """Tras invalidar, el token aparece como usado."""
        token = create_reset_token(TEST_USER_ID)
        invalidate_reset_token(token)
        assert is_token_invalidated(token) is True

    def test_edge_case_different_tokens_dont_interfere(self):
        """Invalidar un token no afecta a otros tokens."""
        token_a = create_reset_token(TEST_USER_ID)
        token_b = create_reset_token(2)
        invalidate_reset_token(token_a)
        assert is_token_invalidated(token_a) is True
        assert is_token_invalidated(token_b) is False

    def test_edge_case_invalidate_malformed_token(self):
        """Invalidar un token malformado no lanza excepción."""
        invalidate_reset_token("token-completamente-invalido")
        assert is_token_invalidated("token-completamente-invalido") is True