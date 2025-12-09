from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from utils.db_session import get_session
from services.pedido_service import PedidoService


class CobroWindow(QWidget):
    """Ventana de cobro independiente."""
    def __init__(self, pedido_dict, pedidos_window=None):
        super().__init__(None)  # ← Ventana independiente SIEMPRE
        self.pedido = pedido_dict
        self.pedidos_window = pedidos_window
        self.pagado = False

        self.setWindowFlag(Qt.Window)
        self.setWindowModality(Qt.NonModal)

        self.setWindowTitle("SAMAR-POS | Cobro")
        self.resize(500, 350)
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        canal = pedido_dict.get("canal", "SALON")
        if canal == "DOMICILIO":
            direccion = pedido_dict.get("direccion") or "Sin dirección"
            repartidor = pedido_dict.get("repartidor") or "Sin asignar"

            lbl_canal = QLabel(f"Canal: Domicilio • Repartidor: {repartidor}")
            lbl_canal.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_canal)

            lbl_direccion = QLabel(f"Entrega: {direccion}")
            lbl_direccion.setWordWrap(True)
            layout.addWidget(lbl_direccion)

        self.lbl_total = QLabel(f"Total a pagar: <b>${self.pedido['total']:.2f}</b>")
        self.lbl_total.setAlignment(Qt.AlignCenter)
        self.lbl_total.setObjectName("logoTitle")
        layout.addWidget(self.lbl_total)

        if canal == "DOMICILIO" and pedido_dict.get("envio"):
            lbl_envio = QLabel(f"Incluye envío de ${float(pedido_dict['envio']):.2f}")
            lbl_envio.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl_envio)

        layout.addWidget(QLabel("Efectivo recibido:"))
        self.input_efectivo = QLineEdit()
        self.input_efectivo.textChanged.connect(self.calcular_cambio)
        layout.addWidget(self.input_efectivo)

        self.lbl_cambio = QLabel("Cambio: $0.00")
        self.lbl_cambio.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_cambio)

        btns = QHBoxLayout()

        btn_confirmar = QPushButton("💵 Confirmar Pago")
        btn_confirmar.clicked.connect(self.confirmar_pago)
        btns.addWidget(btn_confirmar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.close)
        btns.addWidget(btn_cancelar)

        layout.addLayout(btns)

    # --------------------
    def calcular_cambio(self):
        t = self.input_efectivo.text().strip()
        if not t.replace('.', '', 1).isdigit():
            self.lbl_cambio.setText("Cambio: $0.00")
            return
        recibido = float(t)
        cambio = max(recibido - self.pedido["total"], 0)
        self.lbl_cambio.setText(f"Cambio: ${cambio:.2f}")

    # --------------------
    def confirmar_pago(self):
        t = self.input_efectivo.text().strip()

        if not t.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Monto inválido", "Ingresa un número válido.")
            return

        recibido = float(t)

        if recibido < self.pedido["total"]:
            QMessageBox.warning(self, "Falta dinero", "El monto recibido es menor al total.")
            return

        with get_session() as db:
            svc = PedidoService(db)
            svc.registrar_pago(self.pedido["id"], recibido)
            svc.finalizar(self.pedido["id"])

        QMessageBox.information(self, "Listo", "Pago registrado correctamente.")
        self.pagado = True
        self._volver_a_pedidos(resetear=True)
        self.close()

    # --------------------
    def _volver_a_pedidos(self, resetear=False):
        if not self.pedidos_window:
            return

        if resetear and hasattr(self.pedidos_window, "resetear_formulario"):
            self.pedidos_window.resetear_formulario()

        self.pedidos_window.show()
        self.pedidos_window.raise_()
        self.pedidos_window.activateWindow()

    # --------------------
    def closeEvent(self, event):
        # Si se canceló el pago, regresa a la pantalla de pedidos con los datos intactos.
        if not self.pagado:
            self._volver_a_pedidos(resetear=False)
        super().closeEvent(event)
