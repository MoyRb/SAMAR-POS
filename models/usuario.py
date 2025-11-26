from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from utils.database import Base   # <── USAR Base central


class Rol(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(32), unique=True, nullable=False)
    descripcion = Column(String(120))
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(120), nullable=False)
    rol_id = Column(BigInteger, ForeignKey("roles.id"), nullable=False)
    pass_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(TIMESTAMP)
    ultimo_login = Column(DateTime)
    debe_cambiar_password = Column(Boolean, default=False)

    rol = relationship("Rol", back_populates="usuarios")
