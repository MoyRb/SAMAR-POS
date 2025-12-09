import importlib
## tests/conftest.py
# Configura fixtures de Pytest y un engine en memoria para pruebas aisladas.
from pathlib import Path
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.base import Base


def build_memory_engine():
    return create_engine(
        "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}
    )


@pytest.fixture
def db_session(monkeypatch):
    # Fuerza a settings a usar SQLite memoria
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    import utils.settings

    importlib.reload(utils.settings)
    engine = build_memory_engine()

    # Importa modelos para registrar metadata
    import models.producto  # noqa: F401
    import models.pedido  # noqa: F401
    import models.usuario  # noqa: F401
    import models.pago  # noqa: F401
    import models.corte  # noqa: F401
    import models.cliente  # noqa: F401
    import models.bitacora  # noqa: F401

    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
