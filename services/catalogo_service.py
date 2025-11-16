# services/catalogo_service.py
from sqlalchemy.orm import Session
from models.producto import Producto

class CatalogoService:
    """Servicio para interactuar con el catálogo de productos."""
    def __init__(self, db: Session):
        self.db = db

    def listar(self, solo_activos=True):
        query = self.db.query(Producto)
        if solo_activos:
            query = query.filter(Producto.activo == True)

        productos = query.order_by(Producto.categoria, Producto.nombre).all()

        # Convertimos ORM → dict
        return [
            {
                "id": p.id,
                "nombre": p.nombre,
                "precio": float(p.precio),
                "categoria": p.categoria,
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
                "precio": float(p.precio),
                "categoria": p.categoria,
                "activo": p.activo
            }
            for p in productos
        ]
