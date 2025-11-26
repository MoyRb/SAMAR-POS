from sqlalchemy import Column, BigInteger, DECIMAL, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from utils.database import Base
from datetime import datetime


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pedido_id = Column(BigInteger, ForeignKey("pedidos.id"), nullable=False)

    metodo = Column(
        Enum("EFECTIVO", "TARJETA", "TRANSFERENCIA"),
        default="EFECTIVO",
        nullable=False
    )

    importe = Column(DECIMAL(10, 2), nullable=False)
    cambio = Column(DECIMAL(10, 2), nullable=False)

    registrado_por = Column(BigInteger, nullable=True)
    registrado_en = Column(TIMESTAMP, default=datetime.now, nullable=False)

    pedido = relationship("Pedido", back_populates="pagos")
