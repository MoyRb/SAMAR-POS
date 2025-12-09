from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(60), nullable=False, unique=True)
    descripcion = Column(String(180))

    productos = relationship("Producto", back_populates="categoria")


class Tamano(Base):
    __tablename__ = "tamanos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(32), nullable=False, unique=True)
    diametro_cm = Column(Integer)
    factor_precio = Column(DECIMAL(5, 2), default=1)

    productos = relationship("Producto", back_populates="tamano")


class Ingrediente(Base):
    __tablename__ = "ingredientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(80), unique=True, nullable=False)
    costo_unitario = Column(DECIMAL(10, 2), nullable=False, default=0)
    inventario = Column(Integer, default=0)
    activo = Column(Boolean, default=True)

    producto_ingredientes = relationship("ProductoIngrediente", back_populates="ingrediente")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False, unique=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    tamano_id = Column(Integer, ForeignKey("tamanos.id"))
    precio_base = Column(DECIMAL(10, 2), nullable=False)
    es_pizza = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)

    categoria = relationship("Categoria", back_populates="productos")
    tamano = relationship("Tamano", back_populates="productos")
    ingredientes = relationship("ProductoIngrediente", back_populates="producto", cascade="all, delete-orphan")


class ProductoIngrediente(Base):
    __tablename__ = "producto_ingredientes"

    producto_id = Column(Integer, ForeignKey("productos.id"), primary_key=True)
    ingrediente_id = Column(Integer, ForeignKey("ingredientes.id"), primary_key=True)
    cantidad = Column(Integer, default=1)
    extra = Column(Boolean, default=False)

    producto = relationship("Producto", back_populates="ingredientes")
    ingrediente = relationship("Ingrediente", back_populates="producto_ingredientes")
