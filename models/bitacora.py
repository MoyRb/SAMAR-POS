from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class Bitacora(Base):
    __tablename__ = "bitacora"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    tipo = Column(String(50), nullable=False)
    mensaje = Column(String(255), nullable=False)
    creado_en = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="bitacoras")
