## services/reparto_service.py
"""Servicios para gestionar envíos y repartos, incluyendo listados y estados."""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from models.pedido import Pedido, Reparto


class RepartoService:
    def __init__(self, db: Session):
        self.db = db

    def listar(self, estado: Optional[str] = None) -> List[Reparto]:
        query = (
            self.db.query(Reparto)
            .options(
                selectinload(Reparto.pedido).selectinload(Pedido.cliente),
                selectinload(Reparto.pedido).selectinload(Pedido.items),
            )
            .join(Pedido)
        )

        if estado:
            query = query.filter(Reparto.estado == estado)

        return query.order_by(Pedido.creado_en.desc()).all()

    def cambiar_estado(self, reparto_id: int, estado: str) -> Reparto:
        reparto = self.db.query(Reparto).get(reparto_id)
        reparto.estado = estado
        self.db.commit()
        self.db.refresh(reparto)
        return reparto

    def resumen_por_estado(self):
        resultados = (
            self.db.query(Reparto.estado, func.count(Reparto.id))
            .group_by(Reparto.estado)
            .all()
        )
        resumen = {"ASIGNADO": 0, "EN_RUTA": 0, "ENTREGADO": 0, "DEVUELTO": 0}
        for estado, cantidad in resultados:
            resumen[estado] = cantidad
        return resumen
