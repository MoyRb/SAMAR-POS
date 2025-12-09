"""Sesiones de base de datos y utilidades."""
import contextlib
import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

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

    default_username = os.getenv("ADMIN_DEFAULT_USERNAME", "admin")
    default_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin")
    force_reset = os.getenv("ADMIN_FORCE_RESET", "false").lower() == "true"

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

        admin_user = session.query(Usuario).filter_by(username=default_username).first()
        if not admin_user:
            admin_user = Usuario(
                username=default_username,
                nombre="Administrador",
                rol_id=admin_role.id,
                pass_hash=bcrypt.hash(default_password),
                activo=True,
            )
            session.add(admin_user)
            print(
                f"[INIT] Usuario admin creado: usuario='{default_username}' contraseña='{default_password}'."
            )
        elif force_reset:
            admin_user.pass_hash = bcrypt.hash(default_password)
            print(
                "[INIT] Contraseña del usuario admin restablecida por variable ADMIN_FORCE_RESET=true."
            )

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
