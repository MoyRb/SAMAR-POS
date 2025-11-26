# utils/database.py
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# ---- CONFIGURACIÓN DEL ENGINE ----
DB_USER = "root"
DB_PASS = "Marlen17"
DB_HOST = "localhost"
DB_NAME = "samar_pos"

DB_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(
    DB_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    echo=True
)

# ---- BASE ÚNICA PARA TODOS LOS MODELOS ----
Base = declarative_base()
