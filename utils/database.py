"""Conexión a base de datos usando SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

from models.base import Base
from utils.settings import get_settings

settings = get_settings()

# Configura el engine en función del URL: SQLite usa connect_args simples
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=settings.db_echo,
    )
else:
    engine = create_engine(
        settings.database_url,
        poolclass=QueuePool,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_recycle=3600,
        echo=settings.db_echo,
    )

__all__ = ["engine", "Base"]
