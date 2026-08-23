# 🏪 TrackFlow Inventory API

> **Backend REST API para gestión de inventario con SQLAlchemy ORM y doble base de datos (SQLite + PostgreSQL)**

---

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#-descripción-del-proyecto)
2. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
3. [Estructura del Proyecto](#-estructura-del-proyecto)
4. [Instalación y Configuración](#-instalación-y-configuración)
5. [Variables de Entorno](#-variables-de-entorno)
6. [Ejecución](#-ejecución)
7. [Migraciones con Alembic](#-migraciones-con-alembic)
8. [Endpoints de la API](#-endpoints-de-la-api)
9. [Pruebas (Tests)](#-pruebas-tests)
10. [Docker y PostgreSQL Local](#-docker-y-postgresql-local)
11. [Supabase (Producción)](#-supabase-producción)
12. [Esquema de la Base de Datos](#-esquema-de-la-base-de-datos)
13. [Checklist de Entrega](#-checklist-de-entrega)

---

## 📖 Descripción del Proyecto

Este proyecto es un **backend REST API** construido con **FastAPI** y **SQLAlchemy 2.0 (async)** que gestiona un sistema de inventario completo.

### ¿Qué puedes hacer con esta API?

- ✅ **Crear, leer, actualizar y eliminar** items del inventario
- ✅ **Ajustar stock** (entrada, salida, ajuste) con registro automático de movimientos
- ✅ **Filtrar y buscar** items por categoría, almacén, texto, stock bajo
- ✅ **Paginación** para manejar grandes volúmenes de datos
- ✅ **Documentación automática** en Swagger UI (`/docs`)

### Doble Base de Datos

La API soporta **dos motores de base de datos** sin cambiar ni una línea de código:

| Entorno | Base de Datos | Driver | ¿Para qué? |
|---------|--------------|--------|------------|
| 🖥️ Desarrollo | SQLite | `aiosqlite` | Pruebas locales, no requiere instalación |
| ☁️ Producción | PostgreSQL | `asyncpg` | Cuando lo despliegues en un servidor real |

Esto se logra simplemente cambiando la variable `DATABASE_URL` en el archivo `.env`.

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | ¿Para qué sirve? |
|------------|---------|-------------------|
| **Python** | ≥ 3.10 | Lenguaje de programación |
| **FastAPI** | ≥ 0.115 | Framework web para crear APIs REST |
| **SQLAlchemy 2.0** | ≥ 2.0 | ORM (Object-Relational Mapper) para conectar con BD |
| **Alembic** | ≥ 1.13 | Migraciones automáticas de la base de datos |
| **Pydantic v2** | ≥ 2.0 | Validación de datos (schemas de entrada/salida) |
| **Uvicorn** | ≥ 0.35 | Servidor ASGI para ejecutar FastAPI |
| **asyncpg** | ≥ 0.30 | Driver para PostgreSQL asíncrono |
| **aiosqlite** | ≥ 0.20 | Driver para SQLite asíncrono |
| **pytest** | ≥ 8.0 | Framework de pruebas |
| **Docker** | — | Contenedor para PostgreSQL local |

---

## 📁 Estructura del Proyecto

```
services/inventory/
│
├── .env                    # 🔒 Variables de entorno (NO se sube a Git)
├── .env.example            # 📝 Plantilla del .env (sí se sube a Git)
├── .gitignore              # Archivos ignorados por Git
├── README.md               # 📄 Este archivo
├── requirements.txt        # Dependencias del proyecto
├── pyproject.toml          # Metadatos y configuración del proyecto
├── docker-compose.yml      # PostgreSQL local con Docker
├── alembic.ini             # Configuración de Alembic
│
├── alembic/                # Migraciones de la base de datos
│   ├── env.py              # Configuración del entorno Alembic
│   ├── script.py.mako      # Plantilla para generar migraciones
│   └── versions/           # Migraciones generadas aquí
│       └── 291d5b194821_initial_models.py  # 🗃️ Migración inicial
│
├── app/                    # 📦 Código principal de la aplicación
│   ├── __init__.py         # Marca la carpeta como paquete Python
│   ├── main.py             # 🚀 Punto de entrada (FastAPI app)
│   ├── config.py           # ⚙️ Configuración (variables de entorno)
│   ├── database.py         # 🗄️ Conexión a la base de datos
│   ├── dependencies.py     # 🔗 Inyección de dependencias
│   │
│   ├── models/             # 📐 Modelos SQLAlchemy (tablas de la BD)
│   │   ├── __init__.py     # Exporta Base y todos los modelos
│   │   ├── inventory.py    # Modelo Item (productos)
│   │   └── movement.py     # Modelo Movement (movimientos de stock)
│   │
│   ├── schemas/            # 📋 Schemas Pydantic (validación de datos)
│   │   ├── __init__.py
│   │   ├── common.py       # Paginación, respuestas genéricas
│   │   ├── inventory.py    # Schemas de Item
│   │   └── movement.py     # Schemas de Movement
│   │
│   ├── crud/              # 🔄 Operaciones CRUD (base de datos)
│   │   ├── __init__.py
│   │   ├── inventory.py   # CRUD de items
│   │   └── movement.py    # CRUD de movimientos
│   │
│   └── routers/           # 🛣️ Endpoints de la API
│       ├── __init__.py
│       └── inventory.py   # Rutas REST de inventario
│
├── scripts/               # 📜 Scripts auxiliares
│   ├── run_dev.sh         # Ejecutar en desarrollo
│   ├── run_prod.sh        # Ejecutar en producción
│   ├── fix_tests.py       # Utilidad para corregir tests
│   └── rewrite_migration.py # Utilidad para formatear migraciones
│
└── tests/                 # 🧪 Tests automatizados
    ├── __init__.py
    ├── conftest.py        # Fixtures compartidos (BD de prueba, cliente HTTP)
    ├── test_inventory.py  # Tests del CRUD de inventario
    ├── test_movements.py  # Tests de movimientos
    ├── test_filters.py    # Tests de filtros y paginación
    ├── test_crud.py       # Tests unitarios del CRUD
    └── test_database.py   # Tests de conexión a BD
```

---

## ⚙️ Instalación y Configuración

### Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- (Opcional) Docker para PostgreSQL local

### Paso 1: Clonar el repositorio y entrar al proyecto

```bash
cd services/inventory
```

### Paso 2: Crear un entorno virtual (recomendado)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

O usando pip directo:

```bash
pip install "fastapi[standard]>=0.115.0" "sqlalchemy>=2.0.0" "alembic>=1.13.0" "asyncpg>=0.30.0" "aiosqlite>=0.20.0" "pydantic>=2.0.0" "pydantic-settings>=2.0.0" "uvicorn[standard]>=0.35.0" "python-dotenv>=1.0.0" "pytest>=8.0.0" "pytest-asyncio>=0.24.0" "httpx>=0.27.0" "pytest-cov>=5.0.0"
```

### Paso 4: Configurar variables de entorno

Copia el archivo de ejemplo y ajústalo:

```bash
cp .env.example .env
```

Luego edita `.env` con tu configuración. Para **desarrollo local**, usa SQLite:

```env
DATABASE_URL="sqlite+aiosqlite:///./dev.db"
```

---

## 🔐 Variables de Entorno

Todas las variables se definen en el archivo `.env`:

| Variable | Descripción | Valor por Defecto | Ejemplo |
|----------|-------------|-------------------|---------|
| `DATABASE_URL` | URL de conexión a la BD | `sqlite+aiosqlite:///./dev.db` | `postgresql+asyncpg://user:pass@host:5432/db` |
| `APP_NAME` | Nombre de la app (Swagger) | `TrackFlow Inventory API` | — |
| `CORS_ORIGINS` | Orígenes permitidos (separados por coma) | `http://localhost:3000` | `http://localhost:3000,https://midominio.com` |

### Ejemplos de DATABASE_URL

```env
# 🖥️ Desarrollo local SIN instalar nada (SQLite)
DATABASE_URL="sqlite+aiosqlite:///./dev.db"

# 🐳 PostgreSQL local con Docker
DATABASE_URL="postgresql+asyncpg://app:devpassword@localhost:5432/inventory"

# ☁️ Supabase (PostgreSQL en la nube)
DATABASE_URL="postgresql+asyncpg://postgres:TU_CONTRASEÑA@db.tuproyecto.supabase.co:5432/postgres"
```

> ⚠️ **Importante**: El archivo `.env` contiene credenciales y NO debe subirse a Git. El archivo `.env.example` es la plantilla segura que sí se sube.

---

## 🚀 Ejecución

### Desarrollo local (SQLite)

Con SQLite **no necesitas instalar nada**, solo ejecuta:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O usando el script:

```bash
bash scripts/run_dev.sh
```

La API estará disponible en: **http://localhost:8000**

### Documentación Swagger

Abre en tu navegador:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoint de Salud

```bash
curl http://localhost:8000/health
# Respuesta: {"status": "ok", "app": "TrackFlow Inventory API"}
```

---

## 🔄 Migraciones con Alembic

### ¿Qué son las migraciones?

Las migraciones permiten **cambiar la estructura de la base de datos** (crear tablas, añadir columnas) sin perder los datos existentes.

### Comandos básicos

```bash
# 1️⃣ Generar una migración automática (compara modelos vs BD actual)
alembic revision --autogenerate -m "descripcion_del_cambio"

# 2️⃣ Aplicar la migración (crea las tablas en la BD)
alembic upgrade head

# 3️⃣ Ver el historial de migraciones
alembic history

# 4️⃣ Deshacer la última migración
alembic downgrade -1
```

### Migración ya generada

Este proyecto ya incluye la migración inicial (`291d5b194821_initial_models.py`) que crea las tablas:

- `inventory_items` — Tabla de productos
- `inventory_movements` — Tabla de movimientos de stock

Para aplicarla:

```bash
alembic upgrade head
```

> ⚠️ **Nota sobre migraciones con PostgreSQL**: Alembic usa drivers **síncronos** (psycopg2), no async. Si usas PostgreSQL, la URL se convierte automáticamente de `postgresql+asyncpg://` a `postgresql://` en `alembic/env.py`.

---

## 🌐 Endpoints de la API

| Método | Endpoint | Descripción | Códigos de Respuesta |
|--------|----------|-------------|---------------------|
| `GET` | `/health` | Verificar que la API funciona | `200` |
| `GET` | `/api/v1/items/` | Listar items con filtros y paginación | `200` |
| `GET` | `/api/v1/items/{id}` | Obtener un item por ID | `200`, `404` |
| `POST` | `/api/v1/items/` | Crear un nuevo item | `201`, `409`, `422` |
| `PUT` | `/api/v1/items/{id}` | Actualizar un item (parcial) | `200`, `404`, `422` |
| `DELETE` | `/api/v1/items/{id}` | Eliminar (desactivar) un item | `200`, `404` |
| `POST` | `/api/v1/items/{id}/adjust-stock` | Ajustar stock de un item | `200`, `400`, `404` |
| `GET` | `/api/v1/items/{id}/movements` | Historial de movimientos | `200`, `404` |

### Ejemplos de uso con curl

#### Crear un item

```bash
curl -X POST http://localhost:8000/api/v1/items/ \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "CAM-001",
    "name": "Cámara DSLR",
    "description": "Cámara réflex digital profesional",
    "quantity": 10,
    "price": 599.99,
    "category": "Electronics",
    "warehouse": "main",
    "min_stock": 5
  }'
```

#### Listar items (con filtros)

```bash
# Todos los items
curl http://localhost:8000/api/v1/items/

# Filtrar por categoría
curl "http://localhost:8000/api/v1/items/?category=Electronics"

# Buscar por nombre o SKU
curl "http://localhost:8000/api/v1/items/?search=DSLR"

# Stock bajo
curl "http://localhost:8000/api/v1/items/?low_stock=true"

# Paginación
curl "http://localhost:8000/api/v1/items/?page=1&per_page=10"
```

#### Ajustar stock

```bash
# Entrada de stock (+5 unidades)
curl -X POST http://localhost:8000/api/v1/items/1/adjust-stock \
  -H "Content-Type: application/json" \
  -d '{"movement_type": "inbound", "quantity": 5, "reason": "Nuevo lote recibido"}'

# Salida de stock (-3 unidades)
curl -X POST http://localhost:8000/api/v1/items/1/adjust-stock \
  -H "Content-Type: application/json" \
  -d '{"movement_type": "outbound", "quantity": 3, "reason": "Venta a cliente"}'
```

---

## 🧪 Pruebas (Tests)

### Ejecutar todos los tests

```bash
pytest tests/ -v
```

### Ejecutar con cobertura

```bash
pytest tests/ --cov=app --cov-report=term
```

### Resultados esperados

```
50 passed in 2.13s
Coverage: 87% (mínimo requerido: 80%)
```

### Tests disponibles

| Archivo | Tests | ¿Qué prueba? |
|---------|-------|--------------|
| `test_inventory.py` | 11 | CRUD completo + ajuste de stock |
| `test_movements.py` | 9 | Creación de movimientos, validaciones |
| `test_filters.py` | 16 | Filtros, paginación, casos borde, health |
| `test_crud.py` | 10 | Operaciones CRUD directamente |
| `test_database.py` | 2 | Conexión a la base de datos |

### Nota sobre los tests

Los tests usan **SQLite en memoria** (no necesitan PostgreSQL). La base de datos de prueba se crea y destruye automáticamente en cada ejecución. Así los tests son rápidos y aislados.

---

## 🐳 Docker y PostgreSQL Local

### Requisito

Tener **Docker** instalado en tu máquina.

### Paso 1: Levantar PostgreSQL

```bash
docker compose up -d
```

Esto crea un contenedor con PostgreSQL 16 con:
- **Base de datos**: `inventory`
- **Usuario**: `app`
- **Contraseña**: `devpassword` (o la variable `DB_PASSWORD`)
- **Puerto**: `5432`

### Paso 2: Configurar .env

Cambia `DATABASE_URL` en `.env` a:

```env
DATABASE_URL="postgresql+asyncpg://app:devpassword@localhost:5432/inventory"
```

### Paso 3: Ejecutar migraciones

```bash
alembic upgrade head
```

### Paso 4: Iniciar la API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Comandos útiles de Docker

```bash
docker compose up -d      # Iniciar PostgreSQL
docker compose down       # Detener PostgreSQL
docker compose logs -f    # Ver logs de PostgreSQL
```

---

## ☁️ Supabase (Producción)

### ¿Qué es Supabase?

Supabase es un servicio en la nube que proporciona una base de datos **PostgreSQL** gratuita (hasta 500MB). Es la opción recomendada para producción.

### Configuración

1. Crea una cuenta en [supabase.com](https://supabase.com)
2. Crea un nuevo proyecto
3. En la sección **Project Settings → Database**, copia la **Connection string** (URI)
4. Pégala en tu `.env`:

```env
DATABASE_URL="postgresql+asyncpg://postgres:TU_CONTRASEÑA@db.tuproyecto.supabase.co:5432/postgres"
```

### Migraciones en Supabase

```bash
# Las migraciones se ejecutan IGUAL que en local
alembic upgrade head
```

> ⚠️ **Importante**: Si estás en GitHub Codespaces, puede que no puedas conectarte a Supabase porque los Codespaces bloquean conexiones externas. En ese caso:
> - Usa **SQLite** para desarrollo local
> - Ejecuta las migraciones contra Supabase **desde tu máquina local**

---

## 🗄️ Esquema de la Base de Datos

### Tabla: `inventory_items` (Productos)

| Columna | Tipo | Descripción | Restricciones |
|---------|------|-------------|--------------|
| `id` | Integer | Identificador único | PRIMARY KEY, AUTO INCREMENT |
| `sku` | String(50) | Código único del producto | UNIQUE, INDEX |
| `name` | String(200) | Nombre del producto | NOT NULL |
| `description` | Text | Descripción detallada | NULLABLE |
| `quantity` | Integer | Cantidad en stock | DEFAULT 0 |
| `price` | Numeric(10,2) | Precio unitario | NOT NULL |
| `category` | String(100) | Categoría del producto | NOT NULL |
| `warehouse` | String(100) | Almacén donde está | DEFAULT 'main' |
| `min_stock` | Integer | Stock mínimo para alertas | DEFAULT 10 |
| `is_active` | Boolean | Si el producto está activo | DEFAULT TRUE |
| `created_at` | DateTime | Fecha de creación | AUTO |
| `updated_at` | DateTime | Última modificación | AUTO |

### Tabla: `inventory_movements` (Movimientos de Stock)

| Columna | Tipo | Descripción | Restricciones |
|---------|------|-------------|--------------|
| `id` | Integer | Identificador único | PRIMARY KEY, AUTO INCREMENT |
| `item_id` | Integer | Producto relacionado | FOREIGN KEY → inventory_items.id |
| `movement_type` | String(20) | Tipo: inbound / outbound / adjustment | NOT NULL |
| `quantity` | Integer | Cantidad ajustada | NOT NULL |
| `reason` | Text | Motivo del movimiento | NULLABLE |
| `created_at` | DateTime | Fecha del movimiento | AUTO |

### Relaciones

```
inventory_items (1) ────── (N) inventory_movements
     │                              │
     └── id ───────────────────── item_id (ForeignKey)
```

- Un **Item** puede tener muchos **Movements**
- Un **Movement** pertenece a un solo **Item**
- Cuando se elimina un Item (soft delete), sus movimientos NO se eliminan

---

## ✅ Checklist de Entrega

### Requisitos del plan (Hito 5)

| # | Requisito | Estado | ¿Cómo verificarlo? |
|---|-----------|--------|-------------------|
| 1 | `README.md` con instrucciones | ✅ Completo | Este archivo |
| 2 | `.env.example` con variables | ✅ Completo | `cat .env.example` |
| 3 | `requirements.txt` con versiones | ✅ Completo | `cat requirements.txt` |
| 4 | `docker-compose.yml` para PostgreSQL | ✅ Completo | `cat docker-compose.yml` |
| 5 | Schema de BD documentado | ✅ Completo | Sección "Esquema de la BD" |
| 6 | Migraciones Alembic funcionales | ✅ Completo | `alembic upgrade head` |
| 7 | API documentada en `/docs` (Swagger) | ✅ Completo | Arrancar y abrir `/docs` |
| 8 | Tests pasando + cobertura > 80% | ✅ Completo | `pytest --cov=app --cov-report=term` → 87% |
| 9 | Endpoints CRUD + stock + historial | ✅ Completo | 8 endpoints funcionando |
| 10 | Soporte dual SQLite + PostgreSQL | ✅ Completo | Solo cambiar `DATABASE_URL` |

### Resumen de resultados

| Métrica | Resultado |
|---------|-----------|
| Tests totales | 50 ✅ |
| Tests pasando | 50 de 50 ✅ |
| Cobertura de código | 87% ✅ (mínimo 80%) |
| Endpoints implementados | 8 de 8 ✅ |
| Bases de datos soportadas | SQLite + PostgreSQL ✅ |
| Migraciones generadas | 1 (creación inicial) ✅ |

---

## 📚 Comandos Rápidos

```bash
# 🚀 Iniciar servidor (desarrollo)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 🧪 Ejecutar tests
pytest tests/ -v --cov=app --cov-report=term

# 🗃️ Aplicar migraciones
alembic upgrade head

# 🔄 Generar nueva migración
alembic revision --autogenerate -m "descripcion"

# ⏪ Deshacer migración
alembic downgrade -1

# 🐳 Iniciar PostgreSQL local
docker compose up -d

# 🐳 Detener PostgreSQL local
docker compose down
```

---

## 👨‍💻 Autor

Proyecto desarrollado como parte del bootcamp **AI Engineering** de 4Geeks Academy.

---

## 📝 Licencia

MIT