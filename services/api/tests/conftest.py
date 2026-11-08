"""
tests/conftest.py — Fixtures compartidos para todos los tests de autenticación.

Proporciona: app, client, auth_headers, sample_user, etc.

Patrón: TinyDB en directorio temporal, se limpia entre tests.
SECRET_KEY de test: NO usar la de producción.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# ════════════════════════════════════════════════════════════════
# Configurar entorno ANTES de cualquier import de la app
# ════════════════════════════════════════════════════════════════

_tmpdir = tempfile.mkdtemp(prefix="trackflow_test_")

# Variables de entorno de test
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["RESET_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DATABASE_URL"] = ""
os.environ["RESEND_API_KEY"] = "test_resend_key"
os.environ["SENDGRID_API_KEY"] = ""
os.environ["FRONTEND_URL"] = "http://test.local"

# Añadir services/api al path de Python
API_DIR = str(Path(__file__).parent)
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

# ── Configurar db.json en directorio temporal antes de importar database ───
# TinyDB("db.json") crea el archivo en el cwd. Redirigimos a temp.
os.chdir(_tmpdir)

# ── Importar la app ────────────────────────────────────────
from fastapi.testclient import TestClient
from main import app


def _cleanup():
    shutil.rmtree(_tmpdir, ignore_errors=True)


import atexit
atexit.register(_cleanup)


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════

import pytest


@pytest.fixture(autouse=True)
def clean_state():
    """
    Limpia la base de datos y el estado de tokens invalidados
    antes de cada test para garantizar aislamiento.
    """
    from database import users_table, profiles_table
    users_table.truncate()
    profiles_table.truncate()
    from services.auth_service import _invalidated_tokens
    _invalidated_tokens.clear()
    yield


@pytest.fixture
def client() -> TestClient:
    """Proporciona un TestClient de FastAPI."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_user_data() -> dict:
    """Datos de usuario de prueba estándar."""
    return {
        "email": "test@trackflow.com",
        "password": "SecurePass123!",
        "name": "Test User",
    }


@pytest.fixture
def registered_user(client, sample_user_data) -> dict:
    """Registra un usuario en la BD de test y devuelve sus datos."""
    response = client.post("/users/", json={
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
        "name": sample_user_data["name"],
    })
    assert response.status_code in (200, 201), f"Register failed: {response.text}"
    return response.json()


@pytest.fixture
def auth_headers(client, sample_user_data) -> dict:
    """
    Registra un usuario, hace login y devuelve headers con token.
    """
    client.post("/users/", json={
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
        "name": sample_user_data["name"],
    })
    resp = client.post("/auth/login", json={
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    token = data.get("access_token", data.get("token", ""))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_token() -> str:
    """Genera un token que ya expiró (ACCESS_TOKEN_EXPIRE_MINUTES=-1)."""
    original = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "-1"
    from services.auth_service import create_access_token
    token = create_access_token({"sub": "1"})
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = original
    return token


@pytest.fixture
def invalid_token() -> str:
    """Token con firma inválida (otra SECRET_KEY)."""
    from jose import jwt
    return jwt.encode(
        {"sub": "1"},
        "wrong-secret-key-that-does-not-match",
        algorithm="HS256",
    )