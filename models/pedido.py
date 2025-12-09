## models/pedido.py
# Definiciones ORM para pedidos, sus partidas, y los repartos asociados que
# permiten seguir el flujo desde la captura hasta la entrega.
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    Enum,
    TIMESTAMP,
    Text,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship

from models.base import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    folio = Column(String(24), unique=True)
    canal = Column(Enum("SALON", "DOMICILIO", "PARA_LLEVAR"), default="SALON", nullable=False)
    estado = Column(
        Enum(
            "EN_COLA",
            "PREPARACION",
            "EN_HORNO",
            "LISTO",
            "SERVIDO",
            "ENTREGADO",
            "CANCELADO",
            "CERRADO",
        ),
        default="EN_COLA",
        nullable=False,
    )
    mesa = Column(String(10))
    notas = Column(Text)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    direccion_entrega = Column(String(255))
    telefono_contacto = Column(String(32))

    subtotal = Column(DECIMAL(10, 2), default=0)
    envio = Column(DECIMAL(10, 2), default=0)
    propina = Column(DECIMAL(10, 2), default=0)
    total = Column(DECIMAL(10, 2), default=0)
    pagado = Column(Boolean, default=False)

    creado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(TIMESTAMP, default=datetime.now, nullable=False)
    actualizado_en = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    items = relationship("PedidoItem", back_populates="pedido", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="pedido", cascade="all, delete-orphan")
    repartos = relationship("Reparto", back_populates="pedido", cascade="all, delete-orphan")
    cliente = relationship("Cliente", back_populates="pedidos")


class PedidoItem(Base):
    __tablename__ = "pedido_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    tamano_id = Column(Integer, ForeignKey("tamanos.id"))

    cantidad = Column(Integer, nullable=False)
    precio_unit = Column(DECIMAL(10, 2), nullable=False)
    notas = Column(String(255))

    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")
    tamano = relationship("Tamano")


class Reparto(Base):
    __tablename__ = "repartos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    repartidor = Column(String(80))
    estado = Column(Enum("ASIGNADO", "EN_RUTA", "ENTREGADO", "DEVUELTO"), default="ASIGNADO")
    entregado_en = Column(TIMESTAMP)
    notas = Column(String(255))

    pedido = relationship("Pedido", back_populates="repartos")
