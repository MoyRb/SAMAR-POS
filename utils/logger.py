# utils/logger.py
from loguru import logger
from sqlalchemy import text
from utils.db_session import engine

logger.add("logs/samar_pos.log", rotation="1 week", level="INFO")

def log_event(usuario_id, tipo, mensaje):
    """Registra un evento en la base y en el log local."""
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO bitacora (usuario_id, tipo, mensaje)
                    VALUES (:u, :t, :m)
                """),
                {"u": usuario_id, "t": tipo, "m": mensaje},
            )
        logger.info(f"[{tipo}] {mensaje}")
    except Exception as e:
        logger.error(f"Error al registrar bitácora: {e}")
