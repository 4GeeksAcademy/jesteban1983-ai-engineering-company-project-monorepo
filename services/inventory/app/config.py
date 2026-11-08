# ============================================
# config.py - Configuración del backend de inventario
# ============================================
# Este archivo maneja todas las variables de configuración
# usando pydantic-settings para leer desde .env

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando pydantic-settings.
    
    Pydantic-settings lee automáticamente las variables desde:
    1. Archivo .env (si existe)
    2. Variables de entorno del sistema
    
    Heredamos de BaseSettings para obtener esa funcionalidad mágica.
    """

    # --- Configuración de la app ---
    # app_name: Nombre de la aplicación para mostrar en Swagger/docs
    app_name: str = "TrackFlow Inventory API"
    
    # cors_origins: Orígenes permitidos para CORS (separados por coma)
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002"

    # --- Base de datos ---
    # DATABASE_URL: La URL de conexión a la base de datos
    # Por defecto usa SQLite (desarrollo local)
    # En producción se configura como variable de entorno con PostgreSQL
    database_url: str = "sqlite+aiosqlite:///./dev.db"

    # DB_SSL_MODE: Modo SSL para conexión a PostgreSQL
    # Valores comunes: "require", "prefer", "disable", "verify-full"
    # Supabase requiere SSL, por defecto usamos "require"
    db_ssl_mode: str = "require"

    # Configuración para que pydantic-settings busque en .env
    # extra="ignore" significa que ignora variables extras que no estén definidas aquí
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# ---- Instancia única de configuración ----
# Creamos UNA sola instancia de Settings que se reutiliza en toda la app
# Esto se llama "singleton" - una única instancia global
settings = Settings()