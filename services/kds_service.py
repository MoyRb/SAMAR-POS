"""Servicios de Kitchen Display System (KDS)."""
from sqlalchemy.orm import Session
from models.pedido import Pedido
from services.pedido_service import PedidoService


class KDSService:
    def __init__(self, db: Session):
        self.db = db
        self.pedidos = PedidoService(db)

    def pedidos_pendientes(self):
        return (
            self.db.query(Pedido)
            .filter(
                Pedido.estado.in_(
                    ["EN_COLA", "PREPARACION", "EN_HORNO", "LISTO"]
                )
            )
            .order_by(Pedido.creado_en.asc())
            .all()
        )

    def marcar_listo(self, pedido_id: int):
        return self.pedidos.cambiar_estado(pedido_id, "LISTO")

    def marcar_servido(self, pedido_id: int):
        return self.pedidos.cambiar_estado(pedido_id, "SERVIDO")

    def totales(self):
        return self.pedidos.totales_por_estado()
