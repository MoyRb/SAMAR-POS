from datetime import datetime
from sqlalchemy import Column, Integer, DECIMAL, Enum, TIMESTAMP, ForeignKey, Boolean, String
from sqlalchemy.orm import relationship

from models.base import Base


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)

    metodo = Column(
        Enum("EFECTIVO", "TARJETA", "TRANSFERENCIA", "VALE", "CORTESIA"),
        default="EFECTIVO",
        nullable=False,
    )

    importe = Column(DECIMAL(10, 2), nullable=False)
    cambio = Column(DECIMAL(10, 2), nullable=False)
    propina = Column(DECIMAL(10, 2), default=0)
    referencia = Column(String(64))
    registrado_por = Column(Integer, nullable=True)
    registrado_en = Column(TIMESTAMP, default=datetime.now, nullable=False)
    liquidado_en_corte = Column(Boolean, default=False)

    pedido = relationship("Pedido", back_populates="pagos")
    cortes = relationship("CorteCaja", secondary="corte_pagos", back_populates="pagos")
