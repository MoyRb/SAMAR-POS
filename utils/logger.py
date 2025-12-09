"""Logger central con persistencia en bitácora."""
from loguru import logger

from utils.db_session import get_session
from utils.settings import get_settings
from models.bitacora import Bitacora

settings = get_settings()

logger.remove()
logger.add("logs/samar_pos.log", rotation="1 week", level=settings.log_level)


def log_event(usuario_id, tipo, mensaje):
    """Registra un evento en la base y en el log local."""
    try:
        with get_session() as session:
            session.add(Bitacora(usuario_id=usuario_id, tipo=tipo, mensaje=mensaje))
        logger.log(settings.log_level, f"[{tipo}] {mensaje}")
    except Exception as e:
        logger.error(f"Error al registrar bitácora: {e}")
