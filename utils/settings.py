"""Configuración centralizada de la aplicación.

Este módulo lee variables de entorno y ofrece valores por defecto seguros
para desarrollo y pruebas. Si existe un archivo `.env` en el directorio
raíz, se cargan sus pares `CLAVE=valor` de manera sencilla para no
introducir dependencias adicionales.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Dict


def _load_env_file(path: Path) -> Dict[str, str]:
    """Carga un archivo .env plano si existe.

    El formato esperado es `CLAVE=valor`, con líneas en blanco y
    comentarios iniciados por `#` ignorados.
    """
    if not path.exists():
        return {}

    values: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


@dataclass
class Settings:
    """Contenedor de configuración cargada desde el entorno."""

    database_url: str
    db_pool_size: int
    db_max_overflow: int
    db_echo: bool
    log_level: str
    app_env: str

    @classmethod
    def load(cls) -> "Settings":
        project_root = Path(__file__).resolve().parent.parent
        env_values = _load_env_file(project_root / ".env")
        os.environ.update({k: v for k, v in env_values.items() if k not in os.environ})

        # Permite usar DATABASE_URL directamente o armarla desde componentes
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite+pysqlite:///./samar_pos.db",
        )
        if not database_url.startswith("sqlite") and "mysql" not in database_url:
            # fallback a MySQL usando componentes separados
            user = os.getenv("DB_USER", "root")
            password = os.getenv("DB_PASSWORD", "password")
            host = os.getenv("DB_HOST", "localhost")
            name = os.getenv("DB_NAME", "samar_pos")
            database_url = (
                f"mysql+mysqlconnector://{user}:{password}@{host}/{name}?charset=utf8mb4"
            )

        return cls(
            database_url=database_url,
            db_pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            db_max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            db_echo=os.getenv("DB_ECHO", "false").lower() in {"1", "true", "yes"},
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            app_env=os.getenv("APP_ENV", "development"),
        )


def get_settings() -> Settings:
    """Devuelve una instancia singleton de configuración."""
    if not hasattr(get_settings, "_cache"):
        get_settings._cache = Settings.load()  # type: ignore[attr-defined]
    return get_settings._cache  # type: ignore[attr-defined]
