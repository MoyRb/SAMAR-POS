"""Sesiones de base de datos y utilidades."""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import contextlib

from utils.database import engine
from models.base import Base

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _register_models():
    """Importa modelos para que SQLAlchemy registre sus mapeos."""

    import models.producto  # noqa: F401
    import models.pedido  # noqa: F401
    import models.usuario  # noqa: F401
    import models.pago  # noqa: F401
    import models.corte  # noqa: F401
    import models.cliente  # noqa: F401
    import models.bitacora  # noqa: F401


def init_db():
    """Crea tablas y datos mínimos si no existen.

    Esto permite que el sistema arranque en instalaciones nuevas sin pasos
    manuales. Crea la estructura de tablas y garantiza la existencia de un rol
    y usuario administrador por defecto.
    """

    from models.usuario import Rol, Usuario
    from passlib.hash import bcrypt

    _register_models()
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        admin_role = session.query(Rol).filter_by(nombre="admin").first()
        if not admin_role:
            admin_role = Rol(
                nombre="admin",
                descripcion="Administrador del sistema",
                permisos="*",
            )
            session.add(admin_role)
            session.flush()

        admin_user = session.query(Usuario).filter_by(username="admin").first()
        if not admin_user:
            admin_user = Usuario(
                username="admin",
                nombre="Administrador",
                rol_id=admin_role.id,
                pass_hash=bcrypt.hash("admin"),
                activo=True,
            )
            session.add(admin_user)

        session.commit()

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
