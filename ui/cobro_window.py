from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from utils.db_session import get_session
from services.pedido_service import PedidoService
from ui.main_window import MainWindow


class CobroWindow(QWidget):
    """Ventana de cobro independiente."""
    def __init__(self, pedido_dict):
        super().__init__(None)  # ← Ventana independiente SIEMPRE
        self.pedido = pedido_dict

        self.setWindowFlag(Qt.Window)
        self.setWindowModality(Qt.NonModal)

        self.setWindowTitle("SAMAR-POS | Cobro")
        self.resize(500, 350)
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        self.lbl_total = QLabel(f"Total a pagar: <b>${self.pedido['total']:.2f}</b>")
        self.lbl_total.setAlignment(Qt.AlignCenter)
        self.lbl_total.setObjectName("logoTitle")
        layout.addWidget(self.lbl_total)

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

        self.close()

        from ui.main_window import MainWindow
        self.menu = MainWindow({"id": 1, "nombre": "Admin", "rol_id": 1})
        self.menu.show()
