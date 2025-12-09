"""Sesiones de base de datos y utilidades."""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import contextlib

from utils.database import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextlib.contextmanager
def get_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error de conexión a la BD: {e}")
