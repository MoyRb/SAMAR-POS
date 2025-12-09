# services/catalogo_service.py
from sqlalchemy.orm import Session
from models.producto import Categoria, Producto, Tamano

class CatalogoService:
    """Servicio para interactuar con el catálogo de productos."""
    def __init__(self, db: Session):
        self.db = db

    def listar(self, solo_activos=True):
        query = self.db.query(Producto)
        if solo_activos:
            query = query.filter(Producto.activo == True)

        productos = (
            query.join(Producto.categoria, isouter=True)
            .order_by(Categoria.id, Producto.nombre)
            .all()
        )

        # Convertimos ORM → dict
        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "precio": float(p.precio_base),
                "categoria": p.categoria.nombre if p.categoria else None,
                "tamano": p.tamano.nombre if p.tamano else None,
                "activo": p.activo
            }
            for p in productos
        ]

    def buscar(self, texto: str):
        productos = (
            self.db.query(Producto)
            .filter(Producto.nombre.like(f"%{texto}%"))
            .all()
        )

        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "precio": float(p.precio_base),
                "categoria": p.categoria.nombre if p.categoria else None,
                "tamano": p.tamano.nombre if p.tamano else None,
                "activo": p.activo
            }
            for p in productos
        ]

    def crear_producto(self, nombre: str, precio: float, categoria_nombre: str | None = None,
                       es_pizza: bool = False, tamano_nombre: str | None = None):
        """Crea un producto rápido para ventas directas."""
        categoria = None
        if categoria_nombre:
            categoria = self.db.query(Categoria).filter_by(nombre=categoria_nombre).first()
            if not categoria:
                categoria = Categoria(nombre=categoria_nombre)
                self.db.add(categoria)
                self.db.flush()

        tamano = None
        if tamano_nombre:
            tamano = self.db.query(Tamano).filter_by(nombre=tamano_nombre).first()
            if not tamano:
                tamano = Tamano(nombre=tamano_nombre)
                self.db.add(tamano)
                self.db.flush()

        producto = Producto(
            nombre=nombre,
            categoria=categoria,
            tamano=tamano,
            precio_base=precio,
            es_pizza=es_pizza,
            activo=True,
        )

        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)

        return {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": float(producto.precio_base),
            "categoria": producto.categoria.nombre if producto.categoria else None,
            "tamano": producto.tamano.nombre if producto.tamano else None,
            "activo": producto.activo,
        }
