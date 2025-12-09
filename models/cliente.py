## models/cliente.py
# Modelo ORM de clientes que guarda datos de contacto y vínculos con pedidos.
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from models.base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    telefono = Column(String(32), nullable=False)
    direccion = Column(String(255))
    observaciones = Column(String(255))
    activo = Column(Boolean, default=True)

    pedidos = relationship("Pedido", back_populates="cliente")
