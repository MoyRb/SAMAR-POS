from sqlalchemy import Column, Integer, String, DECIMAL, Boolean

from models.base import Base


class CargoExtra(Base):
    __tablename__ = "cargos_extra"

    id = Column(Integer, primary_key=True, autoincrement=True)
    concepto = Column(String(120), nullable=False)
    importe = Column(DECIMAL(10, 2), nullable=False)
    aplica_envio = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
