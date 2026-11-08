# 🏗️ Hito 5 — Backend: Gestión de Inventario con ORM y Doble Base de Datos

> Plan de trabajo fase por fase
> Basado en el módulo "Managing relational databases with FastAPI"
> Fecha: 2026-08-19

---

## 📋 Resumen del Proyecto

**Objetivo:** Desarrollar un backend REST API con FastAPI que gestione un sistema de inventario usando SQLAlchemy ORM y soporte para **doble base de datos** (SQLite en desarrollo, PostgreSQL en producción).

**Proyectos relacionados:**
- `ai-eng-milestone-backend-development` — Backend principal (este plan)
- `ai-eng-inventory-management-backoffice` — Interfaz de backoffice
- `ai-eng-backend-serialization` — Auditoría de serialización

**Stack previsto:**
- Python 3.10+
- FastAPI
- SQLAlchemy 2.0 (async)
- Alembic (migrations)
- Pydantic v2 (schemas/serialization)
- PostgreSQL (producción) + SQLite (dev)
- Docker / docker-compose (opcional)

---

## 🗺️ Fase 0 — Setup y Scaffolding

> **Duración estimada:** 1 sesión
> **Entregable:** Repositorio estructurado con dependencias instaladas

### Tareas

- [ ] Crear carpeta del proyecto en `proyectos/`
- [ ] Inicializar git + `.gitignore` (Python estándar + `.env`)
- [ ] Crear `requirements.txt` con dependencias:
  - `fastapi[standard]`
  - `sqlalchemy>=2.0`
  - `alembic`
  - `asyncpg` (PostgreSQL async driver)
  - `aiosqlite` (SQLite async driver)
  - `pydantic>=2.0`
  - `python-dotenv`
  - `uvicorn`
- [ ] Crear `pyproject.toml` o `setup.cfg` para metadatos
- [ ] Crear estructura de carpetas:

```
proyectos/hito5-inventory-backend/
├── .env                    # variables de entorno
├── .env.example            # plantilla sin secrets
├── .gitignore
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/           # migrations aquí
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI app entrypoint
│   ├── config.py           # settings (DB URL, etc.)
│   ├── database.py         # engine + session factory
│   ├── models/
│   │   ├── __init__.py
│   │   └── inventory.py    # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── inventory.py    # Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── inventory.py    # endpoint definitions
│   ├── crud/
│   │   ├── __init__.py
│   │   └── inventory.py    # database operations
│   └── dependencies.py     # dependency injection
└── tests/
    ├── __init__.py
    ├── conftest.py          # fixtures + test DB
    └── test_inventory.py
```

### ✅ Validación

- [ ] `uvicorn app.main:app --reload` arranca sin errores
- [ ] `GET /health` → `{"status": "ok"}` (endpoint de prueba)
- [ ] `pytest` descubre y pasa tests básicos

---

## Fase 1 — Modelos SQLAlchemy y Doble Base de Datos

> **Duración estimada:** 1-2 sesiones
> **Entregable:** Modelos ORM con conexión a SQLite (dev) y PostgreSQL (prod)

### Conceptos clave del módulo

- **SQLAlchemy 2.0 declarative** — `mapped_column()`, `Mapped[]`, `DeclarativeBase`
- **AsyncSession** — `async with session.begin()` para operaciones asíncronas
- **Conexión dual** — patrón de fábrica que selecciona engine según `DATABASE_URL`
- **Relaciones** — `ForeignKey`, `relationship()`, `back_populates`
- **Índices y constraints** — `unique`, `index`, `nullable`

### Tareas

#### 1.1. Configuración de base de datos dual

- [ ] Crear `app/config.py` con `Settings` class (pydantic-settings o dotenv)
  - `DATABASE_URL`: default `sqlite+aiosqlite:///./dev.db` (dev)
  - `DATABASE_URL`: `postgresql+asyncpg://user:pass@host/db` (prod vía variable de entorno)
- [ ] Crear `app/database.py`:
  - `create_engine()` basado en `settings.DATABASE_URL`
  - `async_sessionmaker` con `expire_on_commit=False`
  - Función `get_db()` como async generator para FastAPI dependency injection
  - Función `init_db()` que ejecuta `Base.metadata.create_all()`

#### 1.2. Modelo de Inventario

- [ ] Crear `app/models/__init__.py` con `Base = declarative_base()`
- [ ] Crear `app/models/inventory.py` con modelo `Item`:

```python
class Item(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(100))
    warehouse: Mapped[str] = mapped_column(String(100), default="main")
    min_stock: Mapped[int] = mapped_column(Integer, default=10)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

#### 1.3. Modelo de Movimientos (opcional pero recomendado)

- [ ] Crear `app/models/movement.py` con modelo `Movement`:

```python
class Movement(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("inventory_items.id"))
    movement_type: Mapped[str] = mapped_column(String(20))  # "inbound" | "outbound" | "adjustment"
    quantity: Mapped[int] = mapped_column(Integer)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    item: Mapped["Item"] = relationship(back_populates="movements")
```

Y añadir a `Item`:
```python
    movements: Mapped[list["Movement"]] = relationship(back_populates="item", cascade="all, delete-orphan")
```

### ✅ Validación

- [ ] `python -c "from app.models import Base; print('Models OK')"` no da errores de importación
- [ ] `init_db()` crea tablas en SQLite sin errores
- [ ] Cambiando `DATABASE_URL` a PostgreSQL, `init_db()` funciona igual

---

## Fase 2 — Schemas Pydantic y Serialización

> **Duración estimada:** 1 sesión
> **Entregable:** Schemas de entrada/salida con validación

### Conceptos clave del módulo

- **Pydantic v2** — `BaseModel`, `Field()`, `model_validator`, `ConfigDict`
- **Schemas de request vs response** — separación clara
- **Nested serialization** — `movements: list[MovementOut]` con `from_attributes=True`
- **Validación personalizada** — `@field_validator`, `@model_validator`

### Tareas

#### 2.1. Schemas base

- [ ] Crear `app/schemas/__init__.py`
- [ ] Crear `app/schemas/inventory.py`:

```python
class ItemBase(BaseModel):
    sku: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    quantity: int = Field(default=0, ge=0)
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    category: str = Field(..., max_length=100)
    warehouse: str = Field(default="main", max_length=100)
    min_stock: int = Field(default=10, ge=0)
    is_active: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    quantity: int | None = Field(default=None, ge=0)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    category: str | None = None
    warehouse: str | None = None
    min_stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

class ItemOut(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

#### 2.2. Schemas de movimientos

- [ ] Crear `app/schemas/movement.py` con `MovementCreate`, `MovementOut`

#### 2.3. Schemas de paginación y filtros

- [ ] Crear `app/schemas/common.py`:

```python
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int
```

### ✅ Validación

- [ ] `ItemCreate(sku="ABC-123", name="Widget", price=9.99)` funciona
- [ ] `ItemCreate(price=-1)` rechaza con error de validación
- [ ] `ItemOut.model_validate(db_item)` convierte ORM → schema

---

## Fase 3 — CRUD Operations

> **Duración estimada:** 1-2 sesiones
> **Entregable:** Capa CRUD completa con manejo de errores

### Conceptos clave del módulo

- **Async CRUD** — `await db.execute()`, `await db.commit()`, `await db.refresh()`
- **Query building** — `select()`, `where()`, `order_by()`, `limit()`, `offset()`
- **Filtros dinámicos** — construcción condicional de queries
- **Manejo de errores** — HTTPException con status codes semánticos

### Tareas

#### 3.1. CRUD de Items

- [ ] Crear `app/crud/__init__.py`
- [ ] Crear `app/crud/inventory.py` con funciones asíncronas:

```python
async def get_items(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    category: str | None = None,
    warehouse: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    low_stock: bool = False,
) -> tuple[list[Item], int]:
    """Listar items con filtros opcionales y paginación."""

async def get_item(db: AsyncSession, item_id: int) -> Item | None:
    """Obtener item por ID."""

async def get_item_by_sku(db: AsyncSession, sku: str) -> Item | None:
    """Obtener item por SKU (unique)."""

async def create_item(db: AsyncSession, data: ItemCreate) -> Item:
    """Crear item (validar SKU único)."""

async def update_item(db: AsyncSession, item_id: int, data: ItemUpdate) -> Item | None:
    """Actualizar item parcialmente."""

async def delete_item(db: AsyncSession, item_id: int) -> bool:
    """Borrado lógico (is_active=False) o físico."""

async def adjust_stock(
    db: AsyncSession,
    item_id: int,
    quantity_change: int,
    reason: str | None = None,
) -> Item:
    """Ajustar stock + registrar movimiento."""
```

#### 3.2. CRUD de Movimientos

- [ ] Crear `app/crud/movement.py` con:
  - `get_movements(item_id)` — historial de movimientos
  - `create_movement(item_id, type, qty, reason)` — registrar movimiento

### ✅ Validación

- [ ] `create_item` con SKU duplicado → HTTPException 409
- [ ] `get_item` con ID inexistente → HTTPException 404
- [ ] `adjust_stock` con cantidad > stock disponible → error controlado
- [ ] `delete_item` hace borrado lógico (cambia `is_active=False`)

---

## Fase 4 — Routers y Endpoints

> **Duración estimada:** 1 sesión
> **Entregable:** API REST completa con documentación automática

### Tareas

#### 4.1. Router de Items

Crear `app/routers/inventory.py`:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/items/` | Listar items (con filtros y paginación) |
| `GET` | `/api/v1/items/{item_id}` | Obtener item por ID |
| `POST` | `/api/v1/items/` | Crear nuevo item |
| `PUT` | `/api/v1/items/{item_id}` | Actualizar item |
| `DELETE` | `/api/v1/items/{item_id}` | Eliminar (desactivar) item |
| `POST` | `/api/v1/items/{item_id}/adjust-stock` | Ajustar stock |
| `GET` | `/api/v1/items/{item_id}/movements` | Historial de movimientos |

#### 4.2. Dependencias

- [ ] Crear `app/dependencies.py` con reutilización de `get_db`
- [ ] Middleware para CORS (si aplica)
- [ ] Middleware para logging de requests

#### 4.3. App principal

- [ ] En `app/main.py`:
  - Crear FastAPI app con título, descripción, versión
  - Incluir routers con prefijo `/api/v1`
  - Evento `startup` para `init_db()`
  - Endpoint `GET /health`

### ✅ Validación

- [ ] Swagger UI en `/docs` muestra todos los endpoints
- [ ] `GET /api/v1/items/` → `{"items": [], "total": 0, "page": 1, ...}`
- [ ] `POST /api/v1/items/` con datos válidos → 201 + item creado
- [ ] `POST /api/v1/items/` con datos inválidos → 422 con errores de validación

---

## Fase 5 — Alembic Migrations

> **Duración estimada:** 1 sesión
> **Entregable:** Migrations funcionales para ambas bases de datos

### Conceptos clave del módulo

- **Alembic** — `alembic init alembic/`, `alembic revision --autogenerate`
- **env.py** — configuración de `target_metadata = Base.metadata`
- **Migrations sequenciales** — `upgrade()` y `downgrade()`
- **Dual-DB migrations** — probar migration en SQLite, ejecutar en PostgreSQL

### Tareas

- [ ] Configurar `alembic.ini` con `sqlalchemy.url = sqlite+aiosqlite:///./dev.db`
- [ ] Configurar `alembic/env.py`:
  - Importar `Base` de `app.models`
  - `target_metadata = Base.metadata`
  - Permitir override de `sqlalchemy.url` vía variable de entorno
- [ ] `alembic revision --autogenerate -m "initial_models"` → generar primera migration
- [ ] `alembic upgrade head` → aplicar migration
- [ ] Modificar modelo (ej: añadir campo `weight`), generar migration, aplicar
- [ ] `alembic history` → ver historial
- [ ] Probar `alembic downgrade -1` → rollback funcional

### ✅ Validación

- [ ] `alembic upgrade head` ejecuta sin errores
- [ ] `alembic downgrade -1` deshace sin errores
- [ ] Las tablas reflejan exactamente los modelos definidos
- [ ] Migration funciona tanto en SQLite como PostgreSQL

---

## Fase 6 — Tests

> **Duración estimada:** 1-2 sesiones
> **Entregable:** Suite de tests con pytest + fixtures async

### Conceptos clave del módulo

- **pytest-asyncio** — `@pytest.mark.asyncio` para tests async
- **Fixtures de base de datos** — crear/test DB, session, data de prueba
- **TestClient** — `httpx.AsyncClient` con FastAPI
- **Cobertura** — `pytest-cov`

### Tareas

- [ ] Configurar `conftest.py`:
  - SQLite en memoria para tests
  - `Base.metadata.create_all()` en setup
  - Fixture `async_session` como dependencia
  - Fixture `client` como `AsyncClient`
- [ ] Tests de CRUD:
  - Crear item → verificar 201 + datos correctos
  - Crear item con SKU duplicado → 409
  - Obtener item → 200 + datos correctos
  - Obtener item inexistente → 404
  - Actualizar item → 200 + datos actualizados
  - Eliminar item → 200 + is_active=False
- [ ] Tests de filtros y paginación:
  - Filtrar por categoría
  - Buscar por texto
  - Paginación: page/per_page
- [ ] Tests de stock:
  - Ajustar stock → verificar cantidad + movimiento creado
  - Ajuste negativo mayor que stock → manejo de error

### ✅ Validación

- [ ] `pytest -v` → todos los tests pasan (mínimo 10-15 tests)
- [ ] `pytest --cov=app --cov-report=term` → cobertura > 80%

---

## Fase 7 — Integración con Doble Base de Datos (Producción)

> **Duración estimada:** 1 sesión
> **Entregable:** Configuración para PostgreSQL en producción

### Tareas

- [ ] Configurar Docker Compose para PostgreSQL local:

```yaml
version: "3.9"
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: inventory
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

- [ ] Crear script `scripts/run_prod.sh`:
  ```bash
  export DATABASE_URL=postgresql+asyncpg://app:${DB_PASSWORD}@localhost:5432/inventory
  alembic upgrade head
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
- [ ] Verificar que con `DATABASE_URL` apuntando a PostgreSQL:
  - `alembic upgrade head` funciona
  - CRUD completo funciona
  - Tests pasan (ajustando fixture de conexión)

### ✅ Validación

- [ ] Docker Compose levanta PostgreSQL
- [ ] `alembic upgrade head` en PostgreSQL crea tablas correctamente
- [ ] Misma API funciona con ambas bases de datos sin cambiar código

---

## 📦 Entregable Final

### Estructura completa del proyecto

```
proyectos/hito5-inventory-backend/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── docker-compose.yml
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial_models.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   └── movement.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── inventory.py
│   │   └── movement.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── inventory.py
│   └── crud/
│       ├── __init__.py
│       ├── inventory.py
│       └── movement.py
├── scripts/
│   ├── run_dev.sh
│   └── run_prod.sh
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_inventory.py
    └── test_movements.py
```

### Checklist de entrega

- [ ] `README.md` con instrucciones de instalación, configuración y uso
- [ ] `.env.example` con todas las variables necesarias
- [ ] `requirements.txt` con versiones fijadas
- [ ] `docker-compose.yml` para PostgreSQL local
- [ ] Schema de la base de datos documentado (modelos + relaciones)
- [ ] Migrations con Alembic funcionales
- [ ] API documentada en `/docs` (Swagger)
- [ ] Tests pasando con cobertura > 80%
- [ ] Endpoints para CRUD completo + ajuste de stock + historial
- [ ] Soporte dual: SQLite (dev) y PostgreSQL (prod)

---

## 🧠 Temas del Módulo Cubiertos

| Tema | Estado en este plan |
|------|-------------------|
| SQLAlchemy 2.0 ORM (declarative, mapped_column) | ✅ Fase 1 |
| Async sessions y engines | ✅ Fase 1 |
| Conexión dual (SQLite / PostgreSQL) | ✅ Fase 1 + 7 |
| Pydantic v2 schemas y validación | ✅ Fase 2 |
| CRUD asíncrono con filtros dinámicos | ✅ Fase 3 |
| REST API con FastAPI routers | ✅ Fase 4 |
| Alembic migrations (autogenerate, upgrade, downgrade) | ✅ Fase 5 |
| Testing con pytest-asyncio y AsyncClient | ✅ Fase 6 |
| Serialización y deserialización | ✅ Fase 2 + 4 |
| Manejo de errores HTTP | ✅ Fase 3 + 4 |

---

## 🚀 Flujo de Trabajo Recomendado

```
Por sesión:
1. Leer esta fase del plan
2. Revisar conceptos clave listados
3. Implementar código
4. Validar con checklist de la fase
5. Hacer commit con mensaje descriptivo
6. Compartir progreso si hay dudas
```

> **Nota:** Si necesitas ayuda con conceptos específicos (SQLAlchemy async, validación Pydantic, configuración de Alembic), invoca el skill mentor con `skill 4geeks / [tu pregunta]`.