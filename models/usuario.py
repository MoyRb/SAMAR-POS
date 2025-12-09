from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import Base


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(32), unique=True, nullable=False)
    descripcion = Column(String(120))
    permisos = Column(String(255), default="")
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(120), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    pass_hash = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(TIMESTAMP, default=datetime.utcnow)
    ultimo_login = Column(DateTime)
    debe_cambiar_password = Column(Boolean, default=False)

    rol = relationship("Rol", back_populates="usuarios")
    bitacoras = relationship("Bitacora", back_populates="usuario")

    def tiene_permiso(self, permiso: str) -> bool:
        if not self.rol or not self.rol.permisos:
            return False
        permisos = {p.strip().lower() for p in self.rol.permisos.split(',') if p.strip()}
        return permiso.lower() in permisos
