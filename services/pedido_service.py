# services/pedido_service.py
from sqlalchemy.orm import Session
from models.pedido import Pedido, PedidoItem
from models.pago import Pago
from datetime import datetime
import random


class PedidoService:
    """Servicio para crear, actualizar y cobrar pedidos."""
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------
    # 1. CREAR PEDIDO
    # ------------------------------
    def nuevo(self, usuario_id, canal="SALON", mesa=None):
        folio = f"TEMP-{random.randint(10000, 99999)}"

        pedido = Pedido(
            folio=folio,
            canal=canal,
            mesa=mesa,
            creado_por=usuario_id,
            creado_en=datetime.now(),
            subtotal=0,
            total=0,
            pagado=False
        )

        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)

        return pedido

    # ------------------------------
    # 2. AGREGAR ITEMS (AHORA ACEPTA ID Y PRECIO)
    # ------------------------------
    def agregar_item(self, pedido_id, producto_id, cantidad, precio_unit, notas=""):
        item = PedidoItem(
            pedido_id=pedido_id,
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unit=precio_unit,
            notas=notas
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

        subtotal = sum(i.precio_unit * i.cantidad for i in pedido.items)

        pedido.subtotal = subtotal
        pedido.total = subtotal   # SIN IVA PORQUE TU MODELO NO TIENE IVA

        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    # ------------------------------
    # 4. REGISTRAR PAGO (SPRINT 1)
    # ------------------------------
    def registrar_pago(self, pedido_id, monto_recibido):
        pedido = self.db.query(Pedido).filter_by(id=pedido_id).first()

        total = float(pedido.total)  # Convertir DECIMAL a float

        cambio = max(monto_recibido - total, 0)

        pago = Pago(
            pedido_id=pedido_id,
            metodo="EFECTIVO",
            importe=monto_recibido,
            cambio=cambio,
            registrado_por=None  # o self.usuario si quieres
        )

        pedido.pagado = 1  # como TinyInt en MySQL

        self.db.add(pago)
        self.db.commit()
        self.db.refresh(pago)

        return pago, cambio

    # ------------------------------
    # 5. FINALIZAR PEDIDO
    # ------------------------------
    def finalizar(self, pedido_id):
        pedido = self.db.query(Pedido).filter_by(id=pedido_id).first()
        pedido.pagado = True
        self.db.commit()
        return pedido
