## ui/kds_window.py
"""Panel Kitchen Display System (KDS) para cocina."""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt

from utils.db_session import get_session
from services.kds_service import KDSService
from services.pedido_service import PedidoService
from ui.components.kds_card import KDSCard


class KDSWindow(QWidget):
    """Tablero de tickets en cocina con flujo EN_COLA → PREPARACION → LISTO."""

    def __init__(self, usuario):
        super().__init__(None)
        self.usuario = usuario

        self.setWindowFlag(Qt.Window)
        self.setWindowTitle("SAMAR-POS | Cocina")
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())
        self.resize(1200, 720)

        main = QVBoxLayout(self)
        header = QHBoxLayout()
        titulo = QLabel("🍳 KDS - Cocina")
        titulo.setObjectName("logoTitle")
        header.addWidget(titulo)
        header.addStretch()

        btn_refrescar = QPushButton("🔄 Actualizar")
        btn_refrescar.setObjectName("btnSecondary")
        btn_refrescar.clicked.connect(self.cargar_pedidos)
        header.addWidget(btn_refrescar)

        main.addLayout(header)

        columnas = QHBoxLayout()
        columnas.setSpacing(16)

        self.col_cola = self._crear_columna("En cola")
        self.col_preparacion = self._crear_columna("En preparación")
        self.col_listos = self._crear_columna("Listo")

        columnas.addWidget(self.col_cola["container"], 1)
        columnas.addWidget(self.col_preparacion["container"], 1)
        columnas.addWidget(self.col_listos["container"], 1)

        main.addLayout(columnas)

        self.cargar_pedidos()

    # ------------------------------------------------------------------
    def _crear_columna(self, titulo):
        caja = QWidget()
        layout = QVBoxLayout(caja)
        layout.setSpacing(10)

        header = QLabel(titulo)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-weight: 700; font-size: 15px;")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenido = QWidget()
        contenido_layout = QVBoxLayout(contenido)
        contenido_layout.setSpacing(12)
        contenido_layout.addStretch()
        scroll.setWidget(contenido)

        layout.addWidget(scroll)

        return {
            "container": caja,
            "layout": contenido_layout,
        }

    # ------------------------------------------------------------------
    def limpiar_columna(self, columna):
        layout = columna["layout"]
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    # ------------------------------------------------------------------
    def cargar_pedidos(self):
        self.limpiar_columna(self.col_cola)
        self.limpiar_columna(self.col_preparacion)
        self.limpiar_columna(self.col_listos)

        try:
            with get_session() as db:
                svc = KDSService(db)
                pedidos = svc.pedidos_pendientes()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar pedidos:\n{exc}")
            return

        if not pedidos:
            self.col_cola["layout"].addWidget(QLabel("Sin pedidos en cola"))
            self.col_preparacion["layout"].addWidget(QLabel("Nada en preparación"))
            self.col_listos["layout"].addWidget(QLabel("Sin tickets listos"))
            return

        for pedido in pedidos:
            if pedido.estado == "EN_COLA":
                card = KDSCard(pedido, self.avanzar_estado)
                self.col_cola["layout"].insertWidget(self.col_cola["layout"].count() - 1, card)
            elif pedido.estado in {"PREPARACION", "EN_HORNO"}:
                card = KDSCard(pedido, self.avanzar_estado, self.regresar_cola)
                self.col_preparacion["layout"].insertWidget(self.col_preparacion["layout"].count() - 1, card)
            elif pedido.estado == "LISTO":
                card = KDSCard(pedido, self.avanzar_estado)
                self.col_listos["layout"].insertWidget(self.col_listos["layout"].count() - 1, card)

    # ------------------------------------------------------------------
    def avanzar_estado(self, pedido):
        nuevo_estado = "PREPARACION" if pedido.estado == "EN_COLA" else "LISTO"
        try:
            with get_session() as db:
                svc = PedidoService(db)
                svc.cambiar_estado(pedido.id, nuevo_estado)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el pedido:\n{exc}")
            return

        self.cargar_pedidos()

    # ------------------------------------------------------------------
    def regresar_cola(self, pedido):
        try:
            with get_session() as db:
                svc = PedidoService(db)
                svc.cambiar_estado(pedido.id, "EN_COLA")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo regresar el pedido:\n{exc}")
            return

        self.cargar_pedidos()

