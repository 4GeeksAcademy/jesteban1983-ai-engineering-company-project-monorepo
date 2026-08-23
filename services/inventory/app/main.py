# ============================================
# main.py - Punto de entrada de la aplicación FastAPI
# ============================================
# Este es el ARCHIVO PRINCIPAL que arranca el servidor.
# 
# Para ejecutar: uvicorn app.main:app --reload
# 
# --reload significa que se reinicia automáticamente cuando cambia el código
# (solo para desarrollo)

import logging
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings  # Configuración (variables de entorno)
from app.database import check_db_connection, init_db  # Función para crear tablas + healthcheck
from app.routers.inventory import router as inventory_router


# ============================================
# Configuración de logging
# ============================================
logger = logging.getLogger("inventory.api")


# ============================================
# Manejador del ciclo de vida de la app
# ============================================
# asynccontextmanager permite ejecutar código al INICIO y al FINAL de la app.
# 
# - startup: se ejecuta cuando arranca el servidor
# - shutdown: se ejecuta cuando se detiene el servidor
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Código que se ejecuta al iniciar y detener la aplicación.
    
    - Al iniciar: crea las tablas de la BD si no existen
    - Al detener: no hacemos nada especial
    """
    # ---- STARTUP: Al arrancar ----
    print("🚀 Iniciando TrackFlow Inventory API...")
    
    # 1️ Verificar conexión a base de datos primero
    print("🔌 Verificando conexión a base de datos...")
    await check_db_connection()
    print("✅ Conexión a base de datos establecida")
    
    # 2️ Crear tablas si no existen
    await init_db()  # Crea las tablas en la base de datos
    print("✅ Tablas creadas/verificadas correctamente")
    
    yield  # La app corre aquí
    
    # ---- SHUTDOWN: Al detener ----
    print("👋 Servidor detenido")


# ============================================
# Crear la aplicación FastAPI
# ============================================
app = FastAPI(
    title=settings.app_name,        # Título de la API (en Swagger)
    description="API REST para gestión de inventario con soporte dual SQLite/PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,              # Manejador de ciclo de vida
)

# ============================================
# Configuración de CORS
# ============================================
# CORS = Cross-Origin Resource Sharing
# Permite que el frontend (Next.js en otro puerto) llame a esta API
origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Orígenes permitidos
    allow_credentials=True,      # Permitir cookies
    allow_methods=["*"],         # Todos los métodos HTTP
    allow_headers=["*"],         # Todos los headers
)

# ============================================
# Incluir routers
# ============================================
# Conectamos las rutas de inventario a la app principal
app.include_router(inventory_router)


# ============================================
# Endpoint de salud (health check)
# ============================================
@app.get("/health", tags=["Health"])
async def health():
    """
    Endpoint de verificación de salud.
    Útil para saber si el servidor está funcionando.
    """
    return {"status": "ok", "app": settings.app_name}