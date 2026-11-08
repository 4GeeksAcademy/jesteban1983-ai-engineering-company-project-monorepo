#!/bin/bash
# ============================================
# run_prod.sh - Script para ejecutar en producción (Supabase)
# ============================================
# Este script configura la app para usar Supabase (PostgreSQL).
#
# Antes de ejecutar, asegúrate de:
# 1. Tener DATABASE_URL configurada en .env o como variable de entorno
# 2. Tener la contraseña de Supabase lista

echo "🚀 Iniciando servidor de PRODUCCIÓN..."

# Cargar variables de entorno
set -a
source .env 2>/dev/null || echo "⚠️  No hay archivo .env"
set +a

# Verificar que estamos usando PostgreSQL
if [[ "$DATABASE_URL" != postgresql* ]]; then
    echo "❌ ERROR: Para producción necesitas PostgreSQL."
    echo "   Configura DATABASE_URL en .env como:"
    echo "   DATABASE_URL=postgresql+asyncpg://postgres:password@host:6543/postgres"
    exit 1
fi

echo "📦 Conectando a Supabase PostgreSQL..."

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
alembic upgrade head

# Arrancar servidor (sin --reload en producción)
echo "🌐 Servidor corriendo en http://0.0.0.0:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000