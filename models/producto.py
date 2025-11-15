# models/producto.py
from sqlalchemy import Column, BigInteger, String, DECIMAL, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Producto(Base):
    __tablename__ = "productos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, unique=True)
    categoria = Column(String(60))
    precio = Column(DECIMAL(10, 2), nullable=False)
    activo = Column(Boolean, default=True)
