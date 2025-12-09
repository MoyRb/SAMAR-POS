"""Servicios de apertura/cierre y corte de caja."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from models.corte import CorteCaja, CortePago, Liquidacion
from models.pago import Pago
from utils.logger import log_event


class CorteService:
    def __init__(self, db: Session):
        self.db = db

    def abrir_caja(self, usuario_id: int, observaciones: str = "") -> CorteCaja:
        corte = CorteCaja(abierto_por=usuario_id, observaciones=observaciones)
        self.db.add(corte)
        self.db.commit()
        self.db.refresh(corte)
        log_event(usuario_id, "CORTE_ABIERTO", f"Corte {corte.id} abierto")
        return corte

    def cerrar_caja(self, corte_id: int, usuario_id: int):
        corte = self.db.query(CorteCaja).get(corte_id)
        corte.cerrado_por = usuario_id
        corte.cerrado_en = datetime.utcnow()

        totales = (
            self.db.query(Pago.metodo, func.sum(Pago.importe - Pago.cambio))
            .filter(Pago.liquidado_en_corte == False)
            .group_by(Pago.metodo)
            .all()
        )
        for metodo, total in totales:
            if metodo == "EFECTIVO":
                corte.total_efectivo = total or 0
            elif metodo == "TARJETA":
                corte.total_tarjeta = total or 0
            elif metodo == "TRANSFERENCIA":
                corte.total_transferencia = total or 0
            elif metodo == "VALE":
                corte.total_vales = total or 0

        pagos = self.db.query(Pago).filter(Pago.liquidado_en_corte == False).all()
        for pago in pagos:
            self.db.add(CortePago(corte_id=corte.id, pago_id=pago.id))
            pago.liquidado_en_corte = True

        self.db.commit()
        log_event(usuario_id, "CORTE_CERRADO", f"Corte {corte.id} cerrado")
        return corte

    def registrar_liquidacion(self, corte_id: int, responsable: str, total_entregado: float):
        corte = self.db.query(CorteCaja).get(corte_id)
        esperado = float(corte.total_efectivo or 0)
        diferencia = total_entregado - esperado
        liquidacion = Liquidacion(
            corte_id=corte_id,
            responsable=responsable,
            total_entregado=total_entregado,
            diferencia=diferencia,
        )
        self.db.add(liquidacion)
        self.db.commit()
        log_event(None, "LIQUIDACION", f"Corte {corte_id} liquidado por {responsable}")
        return liquidacion

    def resumen_repartidores_y_salon(self):
        """Retorna totales cobrados por repartidor y por ventas en salón.

        Agrupa los pagos por repartidor únicamente para pedidos de domicilio
        y calcula el total cobrado en salón para dar visibilidad durante el
        corte de caja.
        """
        from models.pedido import Pedido, Reparto
        from models.pago import Pago

        repartos = (
            self.db.query(Reparto.repartidor, func.sum(Pago.importe - Pago.cambio))
            .join(Pedido, Pedido.id == Reparto.pedido_id)
            .join(Pago, Pago.pedido_id == Pedido.id)
            .filter(Pedido.canal == "DOMICILIO")
            .group_by(Reparto.repartidor)
            .all()
        )

        salon = (
            self.db.query(func.sum(Pago.importe - Pago.cambio))
            .join(Pedido, Pedido.id == Pago.pedido_id)
            .filter(Pedido.canal == "SALON")
            .scalar()
            or 0
        )

        return {
            "repartidores": {nombre: float(total or 0) for nombre, total in repartos},
            "salon": float(salon or 0),
        }
