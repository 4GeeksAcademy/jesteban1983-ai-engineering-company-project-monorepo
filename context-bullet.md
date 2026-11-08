# 🛡️ Building Bullet-Proof Applications — Tests de Autenticación

> **Proyecto 4Geeks:** Building Bullet-Proof Applications
> **Slug:** `ai-eng-building-bullet-proof-applications`
> **Ticket:** AUTH-088 — Cobertura de pruebas unitarias para la API de autenticación
> **Módulo:** Error handling, debugging and testing
> **Empresa:** TrackFlow
> **Monorepo:** `4GeeksAcademy/ai-engineering-company-project-monorepo`
> **Rama:** `feature/unit-test-suite`
>
> ⚠️ **Este documento es la especificación ejecutable para el agente.**
> El agente NO debe tomar decisiones propias. NO debe alucinar datos, funciones, endpoints ni valores.
> Cada bloque YAML y JSON es un mandato exacto. Si algo no está especificado → PREGUNTAR.

---

## 📋 Índice

1. [Reglas absolutas del agente](#1-reglas-absolutas-del-agente)
2. [Contexto del proyecto](#2-contexto-del-proyecto)
3. [Stack técnico exacto](#3-stack-técnico-exacto)
4. [Estructura exacta de archivos](#4-estructura-exacta-de-archivos)
5. [Fase 0 — Preparación](#5-fase-0--preparación)
6. [Fase 1 — TESTING.md (plan de pruebas)](#6-fase-1--testingmd-plan-de-pruebas)
7. [Fase 2 — Configuración pytest](#7-fase-2--configuración-pytest)
8. [Fase 3 — Test de funciones de seguridad (test_security.py)](#8-fase-3--test-de-funciones-de-seguridad-test_securitypy)
9. [Fase 4 — Test de registro (test_register.py)](#9-fase-4--test-de-registro-test_registerpy)
10. [Fase 5 — Test de login (test_login.py)](#10-fase-5--test-de-login-test_loginpy)
11. [Fase 6 — Test de perfil (test_profile.py)](#11-fase-6--test-de-perfil-test_profilepy)
12. [Fase 7 — Test de restablecimiento de contraseña (test_password_reset.py)](#12-fase-7--test-de-restablecimiento-de-contraseña-test_password_resetpy)
13. [Fase 8 — Test de cambio de contraseña (test_change_password.py)](#13-fase-8--test-de-cambio-de-contraseña-test_change_passwordpy)
14. [Fase 9 — Verificación de cobertura](#14-fase-9--verificación-de-cobertura)
15. [Fase 10 — Frontend: Jest para utilidades TypeScript](#15-fase-10--frontend-jest-para-utilidades-typescript)
16. [Fase 11 — Commit, push y PR](#16-fase-11--commit-push-y-pr)
17. [Extra: Tickets API-042 (backoffice) y FE-019 (frontend)](#17-extra-tickets-api-042-backoffice-y-fe-019-frontend)
18. [Checklist de evaluación 4Geeks](#18-checklist-de-evaluación-4geeks)
19. [Orden de ejecución](#19-orden-de-ejecución)

---

## 1. Reglas absolutas del agente

```yaml
# ════════════════════════════════════════════════════════════════
# REGLAS ABSOLUTAS — NO MODIFICAR, NO SALTAR
# ════════════════════════════════════════════════════════════════

reglas:
  - id: R01
    texto: "NO tomar decisiones propias. Cada sección es un mandato."

  - id: R02
    texto: "NO inventar endpoints, funciones, rutas o esquemas que no estén en este documento o en el código existente."

  - id: R03
    texto: "NO cambiar nombres de archivos, rutas, nombres de tests o estructura del directorio tests/."

  - id: R04
    texto: "NO construir un proyecto nuevo. Trabajar DENTRO del monorepo existente sobre la rama feature/unit-test-suite."

  - id: R05
    texto: "NO probar serialización HTTP ni internos del framework. Cada test debe afirmar lógica de negocio."
    detalle: "Lo que el endpoint DECIDE, no cómo RESPONDE. Usar TestClient de httpx pero testear lógica."

  - id: R06
    texto: "Cada endpoint debe tener mínimo: un test de camino feliz, un test de caso límite y un test de modo de fallo."

  - id: R07
    texto: "Los tests deben pasar con uv run pytest desde la raíz del proyecto."

  - id: R08
    texto: "La cobertura del módulo de autenticación debe ser >= 70%, verificada con uv run pytest --cov."

  - id: R09
    texto: "NUNCA exponer claves API reales, tokens JWT reales o datos sensibles en los tests."
    detalle: "Usar claves de test: SECRET_KEY='test-secret-key', ALGORITHM='HS256'"

  - id: R10
    texto: "Si un test revela un bug en el código existente -> CORREGIR el bug y documentarlo en TESTING.md."

  - id: R11
    texto: "No probar dependencias externas (API de email, base de datos real). Usar mocks o TinyDB en memoria."
    detalle: "La función send_reset_email debe ser mockeada. La DB debe ser una TinyDB temporal."

  - id: R12
    texto: "Los nombres de los tests deben ser descriptivos en español o inglés claro."
    detalle: "Ejemplo: test_register_success, test_register_duplicate_email, test_login_invalid_password"

  - id: R13
    texto: "TESTING.md DEBE incluir: cómo ejecutar tests, qué cubre cada suite, y al menos un caso identificado con IA."

  - id: R14
    texto: "Usar SOLO los imports y rutas de import que aparecen en el código existente de services/api/."

  - id: R15
    texto: "No modificar archivos de producción para que los tests pasen. Los tests deben adaptarse al código real."
# ════════════════════════════════════════════════════════════════
```

---

## 2. Contexto del proyecto

### 2.1 Situación actual

```yaml
situacion:
  que_paso: "Un refactor en producción rompió la lógica de expiración de tokens JWT"
  impacto: "Usuarios bloqueados por 2 horas sin que nadie lo detectara"
  consecuencia: "El CTO exige batería de pruebas unitarias antes de cualquier nuevo cambio"
  ticket: "AUTH-088 — Cobertura de pruebas unitarias para la API de autenticación"
```

### 2.2 Endpoints de autenticación existentes

```yaml
endpoints:
  - metodo: POST
    ruta: /auth/register
    descripcion: Registro de nuevo usuario
  - metodo: POST
    ruta: /auth/login
    descripcion: Inicio de sesión
  - metodo: GET
    ruta: /auth/profile/me
    descripcion: Obtener perfil del usuario autenticado
  - metodo: POST
    ruta: /auth/forgot-password
    descripcion: Solicitar restablecimiento de contraseña
  - metodo: POST
    ruta: /auth/reset-password
    descripcion: Restablecer contraseña con token
  - metodo: POST
    ruta: /auth/change-password
    descripcion: Cambiar contraseña con contraseña actual
```

### 2.3 Funciones de seguridad existentes

```yaml
funciones_security:
  - nombre: create_access_token
    params: data: dict
    tipo_retorno: str (JWT token)
    ubicacion: services/api/app/core/security.py

  - nombre: get_current_user
    params: token: str (del header Authorization)
    tipo_retorno: dict (usuario de la DB)
    ubicacion: services/api/app/core/security.py

  - nombre: verify_password
    params: plain_password: str, hashed_password: str
    tipo_retorno: bool
    ubicacion: services/api/app/core/security.py

  - nombre: get_password_hash
    params: password: str
    tipo_retorno: str
    ubicacion: services/api/app/core/security.py

  - nombre: create_reset_token
    params: user_id: int
    tipo_retorno: str (JWT token con type=password_reset)
    ubicacion: services/api/app/core/security.py

  - nombre: verify_reset_token
    params: token: str
    tipo_retorno: int | None
    ubicacion: services/api/app/core/security.py

  - nombre: invalidate_reset_token
    params: token: str
    tipo_retorno: None
    ubicacion: services/api/app/core/security.py

  - nombre: is_token_invalidated
    params: token: str
    tipo_retorno: bool
    ubicacion: services/api/app/core/security.py
```

### 2.4 Reglas de negocio clave

```yaml
reglas_negocio:
  - "El email es único en la base de datos. Registrar con email duplicado debe fallar."
  - "La contraseña debe tener mínimo 8 caracteres en el registro."
  - "Un token JWT expirado (más de ACCESS_TOKEN_EXPIRE_MINUTES) debe ser rechazado."
  - "Solo usuarios autenticados pueden ver /auth/profile/me (token válido en header)."
  - "forgot-password SIEMPRE devuelve 200 (incluso si el email no existe, para no revelar existencia)."
  - "reset-password requiere token JWT válido, no expirado y no usado previamente (anti-replay)."
  - "change-password requiere contraseña actual correcta para aceptar la nueva."
  - "La contraseña se almacena hasheada con bcrypt, nunca en texto plano."
```

---

## 3. Stack técnico exacto

```yaml
backend:
  lenguaje: "Python 3.10+"
  framework: "FastAPI 0.111+"
  testing: "pytest 7+ + pytest-cov + httpx (TestClient)"
  base_datos: "TinyDB (con archivo temporal en tests)"
  auth: "python-jose[cryptography] + passlib[bcrypt]"
  email: "resend (mockear en tests)"
  gestor_dependencias: "uv"
  directorio: "services/api/"

frontend_opcional:
  framework: "Next.js 14+ (App Router)"
  lenguaje: "TypeScript"
  testing: "Jest + ts-jest + @types/jest"
  directorio: "uis/backoffice/"

comandos_verificados:
  ejecutar_tests: "uv run pytest"
  cobertura: "uv run pytest --cov"
  test_frontend: "npx jest --coverage"  # opcional
```

---

## 4. Estructura exacta de archivos

| # | Archivo | Estado | Acción |
|---|---------|--------|--------|
| 1 | `TESTING.md` | NUEVO | Plan de pruebas, cómo ejecutar, cobertura, bugs encontrados |
| 2 | `services/api/tests/__init__.py` | NUEVO | Vacío (módulo Python) |
| 3 | `services/api/tests/conftest.py` | NUEVO | Fixtures compartidos: test_client, test_db, auth_headers |
| 4 | `services/api/tests/test_security.py` | NUEVO | Tests de funciones de seguridad (token, hash, reset token) |
| 5 | `services/api/tests/test_register.py` | NUEVO | Tests de POST /auth/register |
| 6 | `services/api/tests/test_login.py` | NUEVO | Tests de POST /auth/login |
| 7 | `services/api/tests/test_profile.py` | NUEVO | Tests de GET /auth/profile/me |
| 8 | `services/api/tests/test_password_reset.py` | NUEVO | Tests de forgot-password y reset-password |
| 9 | `services/api/tests/test_change_password.py` | NUEVO | Tests de POST /auth/change-password |

**Total:** 9 archivos NUEVOS (1 TESTING.md + 1 \_\_init\_\_.py + 1 conftest.py + 6 test modules)

---

## 5. Fase 0 — Preparación

```bash
# ─────────────────────────────────────────────────────────────
# 0.1 — Crear rama
# ─────────────────────────────────────────────────────────────
git checkout -b feature/unit-test-suite

# ─────────────────────────────────────────────────────────────
# 0.2 — Crear directorio tests/
# ─────────────────────────────────────────────────────────────
mkdir -p services/api/tests
touch services/api/tests/__init__.py

# ─────────────────────────────────────────────────────────────
# 0.3 — Instalar dependencias de testing
# ─────────────────────────────────────────────────────────────
cd services/api
uv add --dev pytest pytest-cov httpx
cd ../..

# ─────────────────────────────────────────────────────────────
# 0.4 — Leer archivos existentes del backend auth
# ─────────────────────────────────────────────────────────────
cat services/api/app/core/security.py
cat services/api/app/routes/auth.py
cat services/api/app/models/user.py  # si existe
cat services/api/app/main.py
cat services/api/pyproject.toml
cat services/api/requirements.txt

# ─────────────────────────────────────────────────────────────
# 0.5 — Verificar estructura existente
# ─────────────────────────────────────────────────────────────
ls services/api/app/core/
ls services/api/app/routes/
ls services/api/app/models/
```

---

## 6. Fase 1 — TESTING.md (plan de pruebas)

### Crear `TESTING.md` en la raíz del monorepo (no dentro de services/api/)

```markdown
# TESTING.md — Building Bullet-Proof Applications

## Cómo ejecutar los tests

```bash
# Backend (FastAPI + pytest)
cd services/api
uv run pytest              # Todos los tests
uv run pytest -v           # Modo verbose
uv run pytest --cov        # Tests + cobertura
uv run pytest --cov --cov-report=term-missing  # + líneas sin cubrir
cd ../..

# Frontend (TypeScript + Jest) — opcional
cd uis/backoffice
npx jest --coverage
cd ../..
```

## Cobertura objetivo
- Módulo de autenticación (app/routes/auth.py + app/core/security.py): >= 70%
- Cada función: mínimo 3 tests (happy path, edge case, failure mode)

## Suites de tests

### test_security.py — Funciones de seguridad
| Función | Happy Path | Edge Case | Failure Mode |
|---------|-----------|-----------|--------------|
| `create_access_token()` | Token válido con datos correctos | Token con datos vacíos | — |
| `verify_password()` | Contraseña correcta verifica OK | — | Contraseña incorrecta |
| `get_password_hash()` | Hash generado correctamente | — | — |
| `create_reset_token()` | Token generado con user_id | — | — |
| `verify_reset_token()` | Token válido devuelve user_id | Token expirado | Token inválido, token con type incorrecto |
| `is_token_invalidated()` | Token no usado = False | Token invalidado = True | — |

### test_register.py — POST /auth/register
| Caso | Tipo | Descripción |
|------|------|-------------|
| Registro exitoso | Happy | Datos válidos, usuario creado |
| Email duplicado | Edge | Mismo email dos veces, segundo falla |
| Contraseña corta | Edge | Password < 8 caracteres |
| Campos vacíos | Failure | title, description, email vacío |
| Email mal formado | Failure | Email sin @ ni dominio |

### test_login.py — POST /auth/login
| Caso | Tipo | Descripción |
|------|------|-------------|
| Login exitoso | Happy | Credenciales correctas → token JWT |
| Contraseña incorrecta | Failure | Email existe pero password wrong |
| Email no existe | Failure | Email no registrado |
| Campos vacíos | Failure | Email o password vacío |

### test_profile.py — GET /auth/profile/me
| Caso | Tipo | Descripción |
|------|------|-------------|
| Perfil autenticado | Happy | Token válido → datos del usuario |
| Sin token | Failure | No hay header Authorization → 401 |
| Token inválido | Failure | Token malformado → 401 |
| Token expirado | Failure | Token con fecha pasada → 401 |

### test_password_reset.py — POST /auth/forgot-password y /auth/reset-password
| Caso | Tipo | Descripción |
|------|------|-------------|
| Forgot email existente | Happy | Email existe → 200 (email enviado) |
| Forgot email no existe | Edge | Email no existe → 200 también (seguridad) |
| Reset token válido | Happy | Token OK → contraseña cambiada |
| Reset token expirado | Failure | Token vencido → 400 |
| Reset token ya usado | Failure | Anti-replay → 400 |
| Reset token inválido | Failure | Token malformado → 400 |

### test_change_password.py — POST /auth/change-password
| Caso | Tipo | Descripción |
|------|------|-------------|
| Cambio exitoso | Happy | Contraseña actual OK → nueva establecida |
| Contraseña actual incorrecta | Failure | Wrong current_password → 400 |
| Contraseña nueva corta | Edge | New password < 8 caracteres |
| Sin autenticación | Failure | No token → 401 |

## Bugs detectados durante testing

(Si un test revela un bug en el código, documentarlo aquí con: archivo, línea, bug, fix.)
```

---

## 7. Fase 2 — Configuración pytest

### Crear `services/api/tests/conftest.py`

```python
# tests/conftest.py
#
# Fixtures compartidos para todos los tests de autenticación.
# Proporciona: app, client, test_db, auth_headers, sample_user.
#
# Patrón: TinyDB en archivo temporal, se limpia entre tests.
# SECRET_KEY de test: NO usar la de producción.

import pytest
import tempfile
import os
from pathlib import Path
from typing import Generator

# ════════════════════════════════════════════════════════════════
# Configurar variables de entorno ANTES de importar la app
# ════════════════════════════════════════════════════════════════
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["RESET_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DATABASE_URL"] = ""  # Forzar TinyDB local
os.environ["RESEND_API_KEY"] = "test_resend_key"
os.environ["SENDGRID_API_KEY"] = ""

# Ahora importar la app y módulos
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from fastapi.testclient import TestClient
from tinydb import TinyDB
from app.main import app
from app.core.security import get_password_hash, create_access_token


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    Fixture automático que se ejecuta antes de cada test.
    Asegura que las variables de entorno de test están seteadas.
    """
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-for-testing-only")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")


@pytest.fixture
def client() -> Generator:
    """
    Proporciona un TestClient de FastAPI.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_db():
    """
    Proporciona una base de datos TinyDB temporal.
    Se elimina al finalizar el test.
    """
    # Crear archivo temporal
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    db_path = tmp.name
    tmp.close()

    db = TinyDB(db_path)
    yield db

    # Limpieza
    db.close()
    os.unlink(db_path)


@pytest.fixture
def sample_user_data() -> dict:
    """
    Datos de usuario de prueba estándar.
    """
    return {
        "email": "test@trackflow.com",
        "password": "TestPass123!",
        "full_name": "Test User",
    }


@pytest.fixture
def registered_user(client, sample_user_data) -> dict:
    """
    Registra un usuario en la BD de test y devuelve sus datos.
    """
    response = client.post("/auth/register", json=sample_user_data)
    assert response.status_code in (200, 201)
    return response.json()


@pytest.fixture
def auth_headers(client, sample_user_data) -> dict:
    """
    Registra un usuario, hace login y devuelve headers con token.
    """
    # Registrar
    client.post("/auth/register", json=sample_user_data)
    # Login
    resp = client.post("/auth/login", json={
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
    })
    assert resp.status_code == 200
    token = resp.json().get("access_token", resp.json().get("token", ""))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_token() -> str:
    """
    Genera un token que ya expiró (con ACCESS_TOKEN_EXPIRE_MINUTES=0).
    """
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "0"
    from app.core.security import create_access_token
    token = create_access_token({"sub": "1"})
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    return token


@pytest.fixture
def invalid_token() -> str:
    """
    Token con firma inválida (otra SECRET_KEY).
    """
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.invalidsignature"
```

---

## 8. Fase 3 — Test de funciones de seguridad (test_security.py)

### Crear `services/api/tests/test_security.py`

```python
# tests/test_security.py
#
# Pruebas unitarias para las funciones en app/core/security.py.
# NO prueba serialización HTTP. Prueba la lógica de negocio:
#   - create_access_token()
#   - verify_password() / get_password_hash()
#   - create_reset_token() / verify_reset_token()
#   - invalidate_reset_token() / is_token_invalidated()

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

# Forzar variables de test antes de importar
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["RESET_TOKEN_EXPIRE_MINUTES"] = "30"

from app.core.security import (  # noqa: E402
    create_access_token,
    verify_password,
    get_password_hash,
    create_reset_token,
    verify_reset_token,
    invalidate_reset_token,
    is_token_invalidated,
)

# ── Constantes de test ───────────────────────────────────────
TEST_USER_ID = 1
TEST_SECRET_KEY = "test-secret-key-for-testing-only"
TEST_ALGORITHM = "HS256"


# ═══════════════════════════════════════════════════════════════
# create_access_token
# ═══════════════════════════════════════════════════════════════

class TestCreateAccessToken:

    def test_happy_path_creates_valid_token(self):
        """
        (HAPPY) create_access_token con data válida genera
        un token que se puede decodificar con la misma SECRET_KEY.
        """
        token = create_access_token({"sub": str(TEST_USER_ID)})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20  # Debe ser un JWT con 3 partes

        # Decodificar para verificar
        from jose import jwt
        payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
        assert payload["sub"] == str(TEST_USER_ID)
        assert "exp" in payload  # Tiene expiración

    def test_edge_case_empty_data(self):
        """
        (EDGE) Token con data vacío se genera pero con datos mínimos.
        """
        token = create_access_token({})
        assert token is not None
        from jose import jwt
        payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
        assert "exp" in payload

    def test_edge_case_multiple_fields(self):
        """
        (EDGE) Token con múltiples campos en data.
        """
        token = create_access_token({
            "sub": str(TEST_USER_ID),
            "role": "admin",
            "email": "admin@trackflow.com",
        })
        from jose import jwt
        payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
        assert payload["role"] == "admin"
        assert payload["email"] == "admin@trackflow.com"


# ═══════════════════════════════════════════════════════════════
# get_password_hash / verify_password
# ═══════════════════════════════════════════════════════════════

class TestPasswordHashing:

    def test_happy_path_verify_correct_password(self):
        """
        (HAPPY) Hash generado con get_password_hash verifica OK
        con verify_password para la misma contraseña.
        """
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        assert hashed != password  # No está en texto plano
        assert verify_password(password, hashed) is True

    def test_failure_wrong_password(self):
        """
        (FAILURE) verify_password con contraseña incorrecta
        debe retornar False.
        """
        hashed = get_password_hash("RealPass123!")
        assert verify_password("WrongPass123!", hashed) is False

    def test_edge_case_empty_password(self):
        """
        (EDGE) Hash de contraseña vacía no debe fallar.
        """
        hashed = get_password_hash("")
        assert isinstance(hashed, str) and len(hashed) > 10

    def test_edge_case_very_long_password(self):
        """
        (EDGE) Contraseña muy larga (100+ caracteres).
        """
        long_pw = "a" * 200
        hashed = get_password_hash(long_pw)
        assert verify_password(long_pw, hashed) is True


# ═══════════════════════════════════════════════════════════════
# create_reset_token / verify_reset_token
# ═══════════════════════════════════════════════════════════════

class TestResetToken:

    def test_happy_path_create_and_verify_reset_token(self):
        """
        (HAPPY) create_reset_token genera token con type=password_reset.
        verify_reset_token lo decodifica y devuelve el user_id.
        """
        token = create_reset_token(TEST_USER_ID)
        user_id = verify_reset_token(token)
        assert user_id == TEST_USER_ID

    def test_failure_expired_reset_token(self):
        """
        (FAILURE) verify_reset_token con token expirado retorna None.
        """
        # Crear token con expiración en 0 minutos
        import os as _os
        _os.environ["RESET_TOKEN_EXPIRE_MINUTES"] = "0"
        # Recargar el módulo para que tome el nuevo valor
        import importlib
        import app.core.security as sec_mod
        importlib.reload(sec_mod)

        expired_token = sec_mod.create_reset_token(TEST_USER_ID)
        result = sec_mod.verify_reset_token(expired_token)

        # Restaurar
        _os.environ["RESET_TOKEN_EXPIRE_MINUTES"] = "30"
        importlib.reload(sec_mod)

        assert result is None

    def test_failure_invalid_signature(self):
        """
        (FAILURE) verify_reset_token con token de otra key retorna None.
        """
        from jose import jwt
        fake_token = jwt.encode(
            {"sub": "1", "type": "password_reset"},
            "different-secret-key",
            algorithm="HS256",
        )
        result = verify_reset_token(fake_token)
        assert result is None

    def test_failure_wrong_token_type(self):
        """
        (FAILURE) Token JWT normal (type=access) NO debe ser válido
        como reset token.
        """
        from jose import jwt
        wrong_type_token = jwt.encode(
            {"sub": "1", "type": "access"},
            TEST_SECRET_KEY,
            algorithm=TEST_ALGORITHM,
        )
        result = verify_reset_token(wrong_type_token)
        assert result is None

    def test_edge_case_non_existent_user_id(self):
        """
        (EDGE) Token con user_id que no existe en BD.
        verify_reset_token decodifica el token pero la app debe
        manejar el user_id no encontrado (el test de ruta lo cubre).
        """
        token = create_reset_token(99999)
        user_id = verify_reset_token(token)
        assert user_id == 99999  # La función decodifica, no verifica existencia


# ═══════════════════════════════════════════════════════════════
# invalidate_reset_token / is_token_invalidated  (anti-replay)
# ═══════════════════════════════════════════════════════════════

class TestTokenInvalidation:

    def test_happy_path_token_not_invalidated(self):
        """
        (HAPPY) Token recién creado NO debe estar invalidado.
        """
        token = create_reset_token(TEST_USER_ID)
        assert is_token_invalidated(token) is False

    def test_happy_path_invalidate_token(self):
        """
        (HAPPY) Invalidar un token y verificar que aparece como usado.
        """
        token = create_reset_token(TEST_USER_ID)
        invalidate_reset_token(token)
        assert is_token_invalidated(token) is True

    def test_edge_case_different_tokens_dont_interfere(self):
        """
        (EDGE) Invalidar un token no afecta a otro token diferente.
        """
        token_a = create_reset_token(1)
        token_b = create_reset_token(2)
        invalidate_reset_token(token_a)
        assert is_token_invalidated(token_a) is True
        assert is_token_invalidated(token_b) is False
```

---

## 9. Fase 4 — Test de registro (test_register.py)

### Crear `services/api/tests/test_register.py`

```python
# tests/test_register.py
#
# Pruebas para POST /auth/register.
# Cubre: registro exitoso, email duplicado, campos inválidos.

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


class TestRegister:

    REGISTER_URL = "/auth/register"

    def test_happy_path_register_success(self, client):
        """
        (HAPPY) Registro con datos válidos retorna 201 o 200
        e incluye email y full_name en la respuesta.
        """
        payload = {
            "email": "newuser@trackflow.com",
            "password": "NewUser123!",
            "full_name": "New User",
        }
        response = client.post(self.REGISTER_URL, json=payload)
        assert response.status_code in (200, 201)
        data = response.json()
        assert data.get("email") == "newuser@trackflow.com"
        assert data.get("full_name") == "New User"

    def test_failure_duplicate_email(self, client, registered_user):
        """
        (FAILURE) Registrar con email ya existente retorna 400.
        """
        payload = {
            "email": "test@trackflow.com",  # Ya registrado por registered_user
            "password": "AnotherPass1!",
            "full_name": "Dup User",
        }
        response = client.post(self.REGISTER_URL, json=payload)
        assert response.status_code == 400
        detail = response.json().get("detail", "")
        assert "exist" in detail.lower() or "duplic" in detail.lower()

    def test_failure_short_password(self, client):
        """
        (FAILURE) Contraseña con menos de 8 caracteres retorna 422.
        """
        payload = {
            "email": "shortpw@trackflow.com",
            "password": "Ab1",  # 3 caracteres
            "full_name": "Short PW",
        }
        response = client.post(self.REGISTER_URL, json=payload)
        assert response.status_code == 422

    def test_failure_empty_fields(self, client):
        """
        (FAILURE) Campos vacíos deben retornar 422 (validación Pydantic).
        """
        payload = {"email": "", "password": "", "full_name": ""}
        response = client.post(self.REGISTER_URL, json=payload)
        assert response.status_code == 422

    def test_failure_malformed_email(self, client):
        """
        (FAILURE) Email sin formato valido retorna 422.
        """
        payload = {
            "email": "not-an-email",
            "password": "ValidPass1!",
            "full_name": "Bad Email",
        }
        response = client.post(self.REGISTER_URL, json=payload)
        assert response.status_code == 422
```

---

## 10. Fase 5 — Test de login (test_login.py)

### Crear `services/api/tests/test_login.py`

```python
# tests/test_login.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


class TestLogin:

    LOGIN_URL = "/auth/login"

    def test_happy_path_login_success(self, client, registered_user, sample_user_data):
        """
        (HAPPY) Login con credenciales correctas retorna 200
        y un access_token JWT valido.
        """
        response = client.post(self.LOGIN_URL, json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        token = data.get("access_token", data.get("token", ""))
        assert len(token) > 20

    def test_failure_wrong_password(self, client, registered_user, sample_user_data):
        """
        (FAILURE) Contrasena incorrecta retorna 401.
        """
        response = client.post(self.LOGIN_URL, json={
            "email": sample_user_data["email"],
            "password": "WrongPassword1!",
        })
        assert response.status_code == 401

    def test_failure_email_not_found(self, client):
        """
        (FAILURE) Email no registrado retorna 401.
        """
        response = client.post(self.LOGIN_URL, json={
            "email": "nobody@trackflow.com",
            "password": "AnyPass1!",
        })
        assert response.status_code == 401

    def test_failure_empty_email(self, client):
        """
        (FAILURE) Email vacio retorna 422.
        """
        response = client.post(self.LOGIN_URL, json={
            "email": "",
            "password": "SomePass1!",
        })
        assert response.status_code == 422

    def test_failure_empty_password(self, client, registered_user, sample_user_data):
        """
        (FAILURE) Contrasena vacia retorna 422.
        """
        response = client.post(self.LOGIN_URL, json={
            "email": sample_user_data["email"],
            "password": "",
        })
        assert response.status_code == 422

    def test_failure_missing_fields(self, client):
        """
        (FAILURE) Payload sin campos retorna 422.
        """
        response = client.post(self.LOGIN_URL, json={})
        assert response.status_code == 422
```

---

## 11. Fase 6 — Test de perfil (test_profile.py)

### Crear `services/api/tests/test_profile.py`

```python
# tests/test_profile.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


class TestProfile:

    PROFILE_URL = "/auth/profile/me"

    def test_happy_path_authenticated(self, client, auth_headers, sample_user_data):
        """
        (HAPPY) Usuario autenticado recibe su perfil.
        """
        response = client.get(self.PROFILE_URL, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data.get("email") == sample_user_data["email"]
        assert data.get("full_name") == sample_user_data["full_name"]

    def test_failure_no_token(self, client):
        """
        (FAILURE) Sin header Authorization retorna 401.
        """
        response = client.get(self.PROFILE_URL)
        assert response.status_code == 401

    def test_failure_invalid_token(self, client, invalid_token):
        """
        (FAILURE) Token con firma invalida retorna 401.
        """
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {invalid_token}"},
        )
        assert response.status_code == 401

    def test_failure_expired_token(self, client, expired_token):
        """
        (FAILURE) Token expirado retorna 401.
        """
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    def test_failure_malformed_auth_header(self, client):
        """
        (EDGE) Header sin formato 'Bearer <token>' retorna 401.
        """
        response = client.get(
            self.PROFILE_URL,
            headers={"Authorization": "NotBearer xyz"},
        )
        assert response.status_code == 401
```

---

## 12. Fase 7 — Tests de restablecimiento y cambio de contrasena (test_passwords.py)

### Crear `services/api/tests/test_passwords.py`

```python
# tests/test_passwords.py
#
# Pruebas para:
#   POST /auth/forgot-password
#   POST /auth/reset-password
#   POST /auth/change-password

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


class TestForgotPassword:

    FORGOT_URL = "/auth/forgot-password"

    @patch("app.services.email_service.send_reset_email", return_value=True)
    def test_happy_path_email_exists(self, mock_send, client, registered_user, sample_user_data):
        """
        (HAPPY) Email existente -> 200. Servicio email llamado.
        """
        response = client.post(self.FORGOT_URL, json={
            "email": sample_user_data["email"],
        })
        assert response.status_code == 200
        mock_send.assert_called_once()

    @patch("app.services.email_service.send_reset_email")
    def test_edge_case_email_not_found_200(self, mock_send, client):
        """
        (EDGE/SEGURIDAD) Email no existente -> 200 tambien.
        No revelar si existe o no.
        """
        response = client.post(self.FORGOT_URL, json={
            "email": "nonexistent@trackflow.com",
        })
        assert response.status_code == 200

    def test_failure_empty_email(self, client):
        """
        (FAILURE) Email vacio retorna 422.
        """
        response = client.post(self.FORGOT_URL, json={"email": ""})
        assert response.status_code == 422


class TestResetPassword:

    RESET_URL = "/auth/reset-password"

    def test_happy_path_reset_success(self, client, registered_user, sample_user_data):
        """
        (HAPPY) Token valido + nueva password -> exito.
        Login con nueva password funciona.
        """
        from app.core.security import create_reset_token
        import os as _os

        # Crear token de reset
        reset_token = create_reset_token(1)  # primer usuario

        new_pw = "NewResetPass1!"
        response = client.post(self.RESET_URL, json={
            "token": reset_token,
            "new_password": new_pw,
        })
        assert response.status_code == 200

        # Login con nueva password funciona
        login_resp = client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": new_pw,
        })
        assert login_resp.status_code == 200

    def test_happy_path_anti_replay(self, client, registered_user):
        """
        (SEGURIDAD) Mismo token usado dos veces -> segunda falla 400.
        """
        from app.core.security import create_reset_token
        reset_token = create_reset_token(1)

        new_pw = "FirstUse123!"
        resp1 = client.post(self.RESET_URL, json={
            "token": reset_token,
            "new_password": new_pw,
        })
        assert resp1.status_code == 200

        resp2 = client.post(self.RESET_URL, json={
            "token": reset_token,
            "new_password": "SecondUse456!",
        })
        assert resp2.status_code == 400

    def test_failure_expired_token(self, client):
        """
        (FAILURE) Token expirado -> 400.
        """
        import os as _os
        _os.environ["RESET_TOKEN_EXPIRE_MINUTES"] = "0"
        import importlib
        import app.core.security as sec_mod
        importlib.reload(sec_mod)

        expired_token = sec_mod.create_reset_token(1)
        _os.environ["RESET_TOKEN_EXPIRE_MINUTES"] = "30"
        importlib.reload(sec_mod)

        response = client.post(self.RESET_URL, json={
            "token": expired_token,
            "new_password": "NewPass123!",
        })
        assert response.status_code in (400, 401)

    def test_failure_invalid_token_signature(self, client):
        """
        (FAILURE) Token con firma invalida -> 400.
        """
        from jose import jwt
        fake_token = jwt.encode(
            {"sub": "1", "type": "password_reset"},
            "wrong-secret-key",
            algorithm="HS256",
        )
        response = client.post(self.RESET_URL, json={
            "token": fake_token,
            "new_password": "NewPass123!",
        })
        assert response.status_code in (400, 401)


class TestChangePassword:

    CHANGE_URL = "/auth/change-password"

    def test_happy_path_change_success(self, client, auth_headers, sample_user_data):
        """
        (HAPPY) Current password correcta + nueva valida -> exito.
        """
        new_pw = "NewPassword456!"
        response = client.post(
            self.CHANGE_URL,
            json={
                "current_password": sample_user_data["password"],
                "new_password": new_pw,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Login con nueva password funciona
        login_resp = client.post("/auth/login", json={
            "email": sample_user_data["email"],
            "password": new_pw,
        })
        assert login_resp.status_code == 200

    def test_failure_wrong_current_password(self, client, auth_headers):
        """
        (FAILURE) Current password incorrecta -> 400.
        """
        response = client.post(
            self.CHANGE_URL,
            json={
                "current_password": "WrongCurrent1!",
                "new_password": "NewPassword456!",
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_failure_short_new_password(self, client, auth_headers, sample_user_data):
        """
        (FAILURE) Nueva password < 8 caracteres -> 422.
        """
        response = client.post(
            self.CHANGE_URL,
            json={
                "current_password": sample_user_data["password"],
                "new_password": "Ab1",
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_failure_no_auth(self, client):
        """
        (FAILURE) Sin autenticacion -> 401.
        """
        response = client.post(
            self.CHANGE_URL,
            json={"current_password": "x", "new_password": "y"},
        )
        assert response.status_code == 401
```

---

## 13. Fase 8 — Verificacion de cobertura

```bash
# 8.1 - Ejecutar todos los tests
cd services/api
uv run pytest -v

# 8.2 - Verificar cobertura
uv run pytest --cov

# 8.3 - Cobertura detallada (lineas sin cubrir)
uv run pytest --cov --cov-report=term-missing

# 8.4 - Si < 70%, identificar funciones faltantes y anadir tests
cd ../..
```

---

## 14. Fase 9 — frontend: Tests Jest (opcional)

```bash
cd uis/backoffice
npm install --save-dev jest @types/jest ts-jest
mkdir -p __tests__
cat > jest.config.js << 'JEOF'
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  roots: ["<rootDir>/__tests__"],
  transform: { "^.+\.tsx?$": "ts-jest" },
};
JEOF
```

---

## 15. Fase 10 — Commit, push y PR

```bash
# Commit
git add TESTING.md
git add services/api/tests/

git commit -m "test: add unit test suite for authentication API (AUTH-088)

Implement comprehensive pytest test suite for TrackFlow authentication:

- test_security.py: Token generation, password hashing, reset token
- test_register.py: Register success, duplicate email, field validation
- test_login.py: Login success, wrong credentials, edge cases
- test_profile.py: Authenticated access, expired/invalid token
- test_passwords.py: Forgot, reset, change password flows

Each endpoint: happy path + edge case + failure mode (3-tier).
All tests pass with 'uv run pytest'.
Coverage >= 70% on authentication module.

TESTING.md documents: run instructions, test plan per suite, coverage.

Branch: feature/unit-test-suite"

# Push y PR
git push origin feature/unit-test-suite

gh pr create   --title "AUTH-088: Unit test suite for authentication API"   --body "## AUTH-088 - Unit test suite

### Cambios
- TESTING.md con plan y cobertura
- tests/conftest.py (fixtures compartidos)
- 5 modulos de test (36+ tests total)

### Coverage por funcion
- create_access_token: 3 tests (happy, empty data, multi-field)
- verify_password: 3 tests (happy, wrong, empty)
- register: 6 tests (happy, duplicate, short pw, empty, bad email, no pw)
- login: 6 tests (happy, wrong pw, not found, empty email/pw)
- profile: 5 tests (auth, no token, invalid, expired, bad header)
- forgot-password: 3 tests (exists, not exists 200, empty)
- reset-password: 4 tests (happy, anti-replay, expired, invalid)
- change-password: 4 tests (happy, wrong current, short, no auth)

### Ejecucion
cd services/api && uv run pytest --cov"
```

---

## 16. Checklist de evaluacion 4Geeks

```
CHECKLIST DE EVALUACION - Building Bullet-Proof Applications
======================================================================

TESTING.md
[ ] 01. TESTING.md existe en la raiz del proyecto
[ ] 02. Documenta como ejecutar los tests
[ ] 03. Documenta que cubre cada suite
[ ] 04. Incluye plan de casos por endpoint
[ ] 05. Menciona al menos un caso identificado con IA
[ ] 06. Documenta bugs encontrados (si aplica)

EJECUCION
[ ] 07. uv run pytest pasa sin errores desde services/api/
[ ] 08. Todos los tests individuales pasan

COBERTURA >= 70%
[ ] 09. app/core/security.py >= 70%
[ ] 10. app/routes/auth.py >= 70%

ESTRUCTURA
[ ] 11. tests/__init__.py existe
[ ] 12. tests/conftest.py con fixtures
[ ] 13. test_security.py existe
[ ] 14. test_register.py existe
[ ] 15. test_login.py existe
[ ] 16. test_profile.py existe
[ ] 17. test_passwords.py existe

TRES PILARES POR ENDPOINT
[ ] 18. register: 3 niveles (happy, edge, failure)
[ ] 19. login: 3 niveles
[ ] 20. profile: 3 niveles
[ ] 21. forgot-password: 3 niveles
[ ] 22. reset-password: 3 niveles
[ ] 23. change-password: 3 niveles

CALIDAD
[ ] 24. Tests nombrados claramente
[ ] 25. Comentarios explican aserciones no obvias
[ ] 26. Afirman logica de negocio, no HTTP serialization
[ ] 27. No exponen claves ni datos sensibles
[ ] 28. IA assisted evidente en TESTING.md

EXTRA (opcional)
[ ] 29. Tests backoffice endpoints (API-042)
[ ] 30. Tests Jest frontend (FE-019)
```

---

## 17. Orden de ejecucion

```yaml
orden:
  fase_0: "Rama feature/unit-test-suite, mkdir tests/, uv add pytest-cov httpx"
  fase_1: "TESTING.md: plan completo de pruebas"
  fase_2: "tests/conftest.py: fixtures (client, test_db, auth_headers, tokens)"
  fase_3: "tests/__init__.py: vacio"
  fase_4: "tests/test_security.py: 8-10 tests de funciones basicas"
  fase_5: "tests/test_register.py: 6 tests de registro"
  fase_6: "tests/test_login.py: 6 tests de login"
  fase_7: "tests/test_profile.py: 5 tests de perfil"
  fase_8: "tests/test_passwords.py: 11 tests de forgot + reset + change"
  fase_9: "Verificacion: uv run pytest --cov >= 70%"
  fase_10: "Frontend Jest (opcional)"
  fase_11: "Commit, push y PR"

reglas:
  - "NO pasar a la siguiente fase hasta que la anterior este COMPLETADA y VERIFICADA"
  - "Fase 9 obligatoria: si coverage < 70%, anadir tests"
  - "NO modificar codigo de produccion para que los tests pasen"
  - "Si un test revela un bug -> CORREGIRLO primero y documentarlo en TESTING.md"
```

