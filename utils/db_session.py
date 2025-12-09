"""Sesiones de base de datos y utilidades."""
from sqlalchemy.orm import sessionmaker
## utils/db_session.py
# Gestiona la sesión de SQLAlchemy, inicializa el esquema y prepara datos demo
# para permitir arrancar el sistema sin configuración adicional.
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import contextlib

from utils.database import engine
from models.base import Base
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def _register_models():
    """Importa modelos para que SQLAlchemy registre sus mapeos."""

    import models.producto  # noqa: F401
    import models.pedido  # noqa: F401
    import models.usuario  # noqa: F401
    import models.pago  # noqa: F401
    import models.corte  # noqa: F401
    import models.cliente  # noqa: F401
    import models.bitacora  # noqa: F401


def _bootstrap_catalogo(session):
    """Crea categorías, tamaños y productos demo si la tabla está vacía."""
    from models.producto import Categoria, Tamano, Producto

    if session.query(Producto).count() > 0:
        return

    pizzas = session.query(Categoria).filter_by(nombre="Pizzas").first()
    bebidas = session.query(Categoria).filter_by(nombre="Bebidas").first()
    postres = session.query(Categoria).filter_by(nombre="Postres").first()

    if not pizzas:
        pizzas = Categoria(nombre="Pizzas", descripcion="Favoritas del horno")
        session.add(pizzas)
    if not bebidas:
        bebidas = Categoria(nombre="Bebidas", descripcion="Refrescos y cafés")
        session.add(bebidas)
    if not postres:
        postres = Categoria(nombre="Postres", descripcion="Algo dulce para cerrar")
        session.add(postres)

    chica = session.query(Tamano).filter_by(nombre="Chica").first()
    grande = session.query(Tamano).filter_by(nombre="Grande").first()
    if not chica:
        chica = Tamano(nombre="Chica", diametro_cm=25, factor_precio=1)
        session.add(chica)
    if not grande:
        grande = Tamano(nombre="Grande", diametro_cm=35, factor_precio=1.5)
        session.add(grande)

    session.flush()

    demo_productos = [
        Producto(nombre="Margarita Clásica", categoria=pizzas, tamano=chica, precio_base=120, es_pizza=True),
        Producto(nombre="Pepperoni", categoria=pizzas, tamano=grande, precio_base=190, es_pizza=True),
        Producto(nombre="Refresco Lata", categoria=bebidas, precio_base=25, es_pizza=False),
        Producto(nombre="Café Americano", categoria=bebidas, precio_base=30, es_pizza=False),
        Producto(nombre="Pay de Queso", categoria=postres, precio_base=65, es_pizza=False),
    ]

    session.add_all(demo_productos)


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

        _bootstrap_catalogo(session)
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
