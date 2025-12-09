"""Servicios para registrar pagos y cierres parciales."""
from sqlalchemy.orm import Session
from models.pago import Pago
from utils.logger import log_event


class PagoService:
    def __init__(self, db: Session):
        self.db = db

    def registrar(self, pedido_id: int, importe: float, metodo: str, cambio: float = 0, referencia: str | None = None, usuario_id: int | None = None):
        pago = Pago(
            pedido_id=pedido_id,
            importe=importe,
            metodo=metodo,
            cambio=cambio,
            referencia=referencia,
            registrado_por=usuario_id,
        )
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)
        log_event(usuario_id, "PAGO", f"Pago registrado en pedido {pedido_id}")
        return pago

    def pagos_por_pedido(self, pedido_id: int):
        return self.db.query(Pago).filter_by(pedido_id=pedido_id).all()
