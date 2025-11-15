# services/pedido_service.py
from sqlalchemy.orm import Session
from models.pedido import Pedido, PedidoItem
from datetime import datetime
import random

class PedidoService:
    """Servicio para crear y administrar pedidos."""
    def __init__(self, db: Session):
        self.db = db

    def nuevo(self, usuario_id, canal="SALON", mesa=None):
        """Crea un nuevo pedido temporal."""
        folio = f"TEMP-{random.randint(10000,99999)}"
        pedido = Pedido(
            folio=folio,
            canal=canal,
            mesa=mesa,
            creado_por=usuario_id,
            creado_en=datetime.now()
        )
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    def agregar_item(self, pedido_id, producto, cantidad=1, notas=""):
        """Agrega un producto al pedido."""
        item = PedidoItem(
            pedido_id=pedido_id,
            producto_id=producto.id,
            cantidad=cantidad,
            precio_unit=producto.precio,
            notas=notas
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def calcular_totales(self, pedido_id):
        """Recalcula subtotal, IVA y total."""
        pedido = self.db.query(Pedido).filter_by(id=pedido_id).first()
        subtotal = sum(i.precio_unit * i.cantidad for i in pedido.items)
        iva = subtotal * 0.16
        pedido.subtotal = subtotal
        pedido.total = subtotal + iva
        self.db.commit()
        self.db.refresh(pedido)
        return pedido
