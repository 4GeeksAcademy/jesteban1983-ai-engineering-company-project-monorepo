# TESTING.md — Building Bullet-Proof Applications

## Cómo ejecutar los tests

```bash
# Backend (FastAPI + pytest)
cd services/api
pytest              # Todos los tests
pytest -v           # Modo verbose
pytest --cov        # Tests + cobertura
pytest --cov --cov-report=term-missing  # + líneas sin cubrir
cd ../..
```

## Cobertura objetivo
- Módulo de autenticación (routes/auth.py + services/auth_service.py + dependencies/auth_deps.py): >= 70%
- Cada función: mínimo 3 tests (happy path, edge case, failure mode)

## Suites de tests

### test_security.py — Funciones de seguridad (services/auth_service.py)
| Función | Happy Path | Edge Case | Failure Mode |
|---------|-----------|-----------|--------------|
| `create_access_token()` | Token válido con datos correctos | Token con datos vacíos | — |
| `verify_password()` | Contraseña correcta verifica OK | — | Contraseña incorrecta |
| `get_password_hash()` / `hash_password()` | Hash generado correctamente | — | — |
| `create_reset_token()` | Token generado con user_id | — | — |
| `verify_reset_token()` | Token válido devuelve user_id | Token expirado | Token inválido, token con type incorrecto |
| `is_token_invalidated()` | Token no usado = False | Token invalidado = True | — |

### test_register.py — POST /users/
| Caso | Tipo | Descripción |
|------|------|-------------|
| Registro exitoso | Happy | Datos válidos, usuario creado |
| Email duplicado | Edge | Mismo email dos veces, segundo falla |
| Contraseña corta | Edge | Password < 6 caracteres |
| Campos vacíos | Failure | email vacío |
| Email mal formado | Failure | Email sin @ ni dominio |

### test_login.py — POST /auth/login
| Caso | Tipo | Descripción |
|------|------|-------------|
| Login exitoso | Happy | Credenciales correctas → token JWT |
| Contraseña incorrecta | Failure | Email existe pero password wrong |
| Email no existe | Failure | Email no registrado |
| Campos vacíos | Failure | Email o password vacío |

### test_profile.py — GET /auth/me
| Caso | Tipo | Descripción |
|------|------|-------------|
| Perfil autenticado | Happy | Token válido → datos del usuario |
| Sin token | Failure | No hay header Authorization → 401 |
| Token inválido | Failure | Token malformado → 401 |
| Token expirado | Failure | Token con fecha pasada → 401 |

### test_passwords.py — POST /auth/forgot-password, /auth/reset-password y /auth/change-password
| Caso | Tipo | Descripción |
|------|------|-------------|
| Forgot email existente | Happy | Email existe → 200 (email enviado) |
| Forgot email no existe | Edge | Email no existe → 200 también (seguridad) |
| Reset token válido | Happy | Token OK → contraseña cambiada |
| Reset token expirado | Failure | Token vencido → 400 |
| Reset token ya usado | Failure | Anti-replay → 400 |
| Reset token inválido | Failure | Token malformado → 400 |
| Cambio exitoso | Happy | Contraseña actual OK → nueva establecida |
| Contraseña actual incorrecta | Failure | Wrong current_password → 400 |
| Contraseña nueva corta | Edge | New password < 6 caracteres |
| Sin autenticación | Failure | No token → 401 |

## Casos identificados con IA (OpenAI Codex / GPT-4)

1. **Anti-replay en reset-password**: El token de reset debe invalidarse tras su uso para prevenir reutilización. Caso identificado mediante análisis de la lógica de `invalidate_reset_token()` vs `is_token_invalidated()` en el código existente.

2. **Forgot-password no revela existencia**: Aunque el endpoint siempre devuelve 200, internamente se genera un token y se envía email SOLO si el usuario existe. Esto previene enumeración de emails.

3. **safe_error vs HTTPException**: El código usa dos mecanismos diferentes para errores HTTP: `safe_error()` (anida en dict) y `HTTPException` directa (detail string plano). Los tests verifican ambos formatos.

## Bugs detectados durante testing

*(Ningún bug detectado hasta el momento. Si algún test revela un bug, se documentará aquí con: archivo, línea, bug y fix.)*