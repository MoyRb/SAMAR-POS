from sqlalchemy import (
    Column, BigInteger, String, DECIMAL, Enum, TIMESTAMP, Text, ForeignKey, Integer
)
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    folio = Column(String(24), unique=True)
    canal = Column(Enum("SALON", "DOMICILIO"), default="SALON", nullable=False)
    estado = Column(
        Enum("EN_COLA", "EN_HORNO", "LISTO", "SERVIDO", "ENTREGADO", "CERRADO"),
        default="EN_COLA",
        nullable=False
    )
    mesa = Column(String(10))
    notas = Column(Text)

    subtotal = Column(DECIMAL(10, 2), default=0)
    envio = Column(DECIMAL(10, 2), default=0)
    total = Column(DECIMAL(10, 2), default=0)
    pagado = Column(Integer, default=0)

    creado_por = Column(BigInteger, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(TIMESTAMP, default=datetime.now, nullable=False)

    items = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="pedido")


class PedidoItem(Base):
    __tablename__ = "pedido_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pedido_id = Column(BigInteger, ForeignKey("pedidos.id"))
    producto_id = Column(BigInteger, ForeignKey("productos.id"))

    cantidad = Column(BigInteger, nullable=False)
    precio_unit = Column(DECIMAL(10, 2), nullable=False)
    notas = Column(String(255))

    pedido = relationship("Pedido", back_populates="items")
