#!/bin/bash
# ============================================
# run_dev.sh - Script para ejecutar en desarrollo
# ============================================
# Este script:
# 1. Carga las variables de entorno desde .env
# 2. Ejecuta las migraciones pendientes
# 3. Arranca el servidor de desarrollo

echo "🚀 Iniciando servidor de desarrollo..."

# Cargar variables de entorno desde .env
# set -a = exporta automáticamente las variables leídas
set -a
source .env 2>/dev/null || echo "⚠️  No hay archivo .env, usando defaults"
set +a

# Mostrar qué base de datos estamos usando
echo "📦 Base de datos: $DATABASE_URL"

# Ejecutar migraciones (si existen)
# 2>/dev/null oculta errores si no hay migraciones aún
alembic upgrade head 2>/dev/null || echo "⚠️  No hay migraciones, se crearán tablas al arrancar"

# Arrancar servidor
# --reload = reinicia automáticamente al cambiar código
# --host 0.0.0.0 = accesible desde cualquier IP (no solo localhost)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000