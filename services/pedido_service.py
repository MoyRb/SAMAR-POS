# services/pedido_service.py
from sqlalchemy.orm import Session
from datetime import datetime
import random

from models.pedido import Pedido, PedidoItem, Reparto
from models.pago import Pago
from models.producto import Producto, Tamano
from utils.logger import log_event


class PedidoService:
    """Servicio para crear, actualizar y cobrar pedidos."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------
    # 1. CREAR PEDIDO
    # ------------------------------
    def nuevo(
        self,
        usuario_id,
        canal="SALON",
        mesa=None,
        cliente_id=None,
        envio=0,
        propina=0,
        direccion_entrega=None,
        telefono_contacto=None,
    ):
        folio = f"PED-{random.randint(10000, 99999)}"

        pedido = Pedido(
            folio=folio,
            canal=canal,
            mesa=mesa,
            cliente_id=cliente_id,
            envio=envio,
            propina=propina,
            direccion_entrega=direccion_entrega,
            telefono_contacto=telefono_contacto,
            creado_por=usuario_id,
            creado_en=datetime.now(),
            subtotal=0,
            total=0,
            pagado=False,
        )

        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        log_event(usuario_id, "PEDIDO_NUEVO", f"Se creó el pedido {pedido.folio}")
        return pedido

    # ------------------------------
    # 2. AGREGAR ITEMS (ACEPTA TAMAÑO Y PRECIO)
    # ------------------------------
    def agregar_item(self, pedido_id, producto_id, cantidad, precio_unit=None, notas="", tamano_id=None):
        producto = self.db.query(Producto).get(producto_id)
        tamano = self.db.query(Tamano).get(tamano_id) if tamano_id else None
        if precio_unit is None:
            precio_unit = producto.precio_base
            if tamano and tamano.factor_precio:
                precio_unit = float(precio_unit) * float(tamano.factor_precio)

        item = PedidoItem(
            pedido_id=pedido_id,
            producto_id=producto_id,
            tamano_id=tamano_id,
            cantidad=cantidad,
            precio_unit=precio_unit,
            notas=notas,
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item

    # ------------------------------
    # 3. CALCULAR TOTALES
    # ------------------------------
    def calcular_totales(self, pedido_id):
        pedido = self.db.query(Pedido).filter_by(id=pedido_id).first()

        subtotal = sum(float(i.precio_unit) * i.cantidad for i in pedido.items)

        pedido.subtotal = subtotal
        pedido.total = subtotal + float(pedido.envio or 0) + float(pedido.propina or 0)

        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    # ------------------------------
    # 4. REGISTRAR PAGO
    # ------------------------------
    def registrar_pago(self, pedido_id, monto_recibido, metodo="EFECTIVO", referencia=None, usuario_id=None):
        pedido = self.db.query(Pedido).filter_by(id=pedido_id).first()
        total = float(pedido.total)  # Convertir DECIMAL a float

        cambio = max(monto_recibido - total, 0)

        pago = Pago(
            pedido_id=pedido_id,
            metodo=metodo,
            importe=monto_recibido,
            cambio=cambio,
            referencia=referencia,
            registrado_por=usuario_id,
            propina=pedido.propina,
        )

        pedido.pagado = True
        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)

        log_event(usuario_id, "PAGO_REGISTRADO", f"Pago de {monto_recibido} para pedido {pedido.folio}")
        return pago, cambio

    # ------------------------------
    # 5. CAMBIAR ESTADO DEL PEDIDO (KDS)
    # ------------------------------
    def cambiar_estado(self, pedido_id, estado):
        pedido = self.db.query(Pedido).filter_by(id=pedido_id).first()
        pedido.estado = estado
        pedido.actualizado_en = datetime.now()
        self.db.commit()
        log_event(pedido.creado_por, "PEDIDO_ESTADO", f"{pedido.folio} -> {estado}")
        return pedido

    # ------------------------------
    # 6. REPARTO
    # ------------------------------
    def asignar_reparto(self, pedido_id, repartidor, notas=""):
        reparto = Reparto(pedido_id=pedido_id, repartidor=repartidor, notas=notas)
        self.db.add(reparto)
        self.db.commit()
        self.db.refresh(reparto)
        log_event(None, "REPARTO_ASIGNADO", f"Pedido {pedido_id} asignado a {repartidor}")
        return reparto

    def marcar_entregado(self, reparto_id):
        reparto = self.db.query(Reparto).get(reparto_id)
        reparto.estado = "ENTREGADO"
        reparto.entregado_en = datetime.now()
        self.db.commit()
        return reparto

    # ------------------------------
    # 7. FINALIZAR PEDIDO
    # ------------------------------
    def finalizar(self, pedido_id):
        pedido = self.db.query(Pedido).filter_by(id=pedido_id).first()
        pedido.pagado = True
        pedido.estado = "EN_COLA"
        pedido.actualizado_en = datetime.now()
        self.db.commit()
        return pedido

    def totales_por_estado(self):
        """Resumen rápido para KDS / dashboard."""
        resultados = (
            self.db.query(Pedido.estado, Pedido.total)
            .all()
        )
        totales = {}
        for estado, total in resultados:
            totales.setdefault(estado, 0)
            totales[estado] += float(total or 0)
        return totales
