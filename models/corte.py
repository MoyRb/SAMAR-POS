## models/corte.py
# Modelos ORM que representan cortes de caja, asociación de pagos y registros de
# liquidación entregados.
from datetime import datetime
from sqlalchemy import Column, Integer, DECIMAL, TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import relationship

from models.base import Base


class CorteCaja(Base):
    __tablename__ = "cortes_caja"

    id = Column(Integer, primary_key=True, autoincrement=True)
    abierto_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cerrado_por = Column(Integer, ForeignKey("usuarios.id"))
    abierto_en = Column(TIMESTAMP, default=datetime.utcnow)
    cerrado_en = Column(TIMESTAMP)
    observaciones = Column(String(255))

    total_efectivo = Column(DECIMAL(10, 2), default=0)
    total_tarjeta = Column(DECIMAL(10, 2), default=0)
    total_transferencia = Column(DECIMAL(10, 2), default=0)
    total_vales = Column(DECIMAL(10, 2), default=0)

    pagos = relationship("Pago", secondary="corte_pagos", back_populates="cortes")


class CortePago(Base):
    __tablename__ = "corte_pagos"

    corte_id = Column(Integer, ForeignKey("cortes_caja.id"), primary_key=True)
    pago_id = Column(Integer, ForeignKey("pagos.id"), primary_key=True)


class Liquidacion(Base):
    __tablename__ = "liquidaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    corte_id = Column(Integer, ForeignKey("cortes_caja.id"))
    responsable = Column(String(120), nullable=False)
    entregado_en = Column(TIMESTAMP, default=datetime.utcnow)
    total_entregado = Column(DECIMAL(10, 2), default=0)
    diferencia = Column(DECIMAL(10, 2), default=0)

    corte = relationship("CorteCaja")
