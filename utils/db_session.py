# utils/db_session.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import contextlib

# Configuración de conexión MySQL
DB_USER = "root"             # Cambia si usas otro usuario
DB_PASS = "Marlen17"      # Cambia por tu contraseña real
DB_HOST = "localhost"
DB_NAME = "samar_pos"

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"

# Crea el engine
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
    echo=False  # cambia a True si quieres ver las consultas SQL en consola
)

# Configura la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextlib.contextmanager
def get_session():
    """Genera una sesión de base de datos segura para usar con 'with'."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def test_connection():
    """Verifica que la conexión a la base sea exitosa."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error de conexión con la base de datos: {e}")
