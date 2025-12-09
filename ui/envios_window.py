from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QGridLayout,
    QFrame,
)
from PySide6.QtCore import Qt

from utils.db_session import get_session
from services.reparto_service import RepartoService
from ui.components.delivery_card import DeliveryCard


class EnviosWindow(QWidget):
    """Panel para monitorear los envíos y su estado actual."""

    def __init__(self, usuario):
        super().__init__(None)
        self.usuario = usuario
        self.repartos = []
        self.estado_actual = None

        self.setWindowFlag(Qt.Window)
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle("SAMAR-POS | Gestión de envíos")
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())
        self.resize(1200, 720)
        self.setMinimumSize(1000, 640)

        root = QVBoxLayout(self)
        root.setSpacing(12)

        header = QHBoxLayout()
        titulo = QLabel("🚚 Panel de envíos")
        titulo.setObjectName("logoTitle")
        header.addWidget(titulo)
        header.addStretch()
        root.addLayout(header)

        self.btn_filtros = {}
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(8)
        for texto, estado in [
            ("Todos", None),
            ("En ruta", "EN_RUTA"),
            ("Entregado", "ENTREGADO"),
            ("Devuelto", "DEVUELTO"),
        ]:
            btn = QPushButton(texto)
            btn.setCheckable(True)
            btn.setObjectName("btnSecondary")
            btn.clicked.connect(lambda checked, e=estado: self.cambiar_filtro(e))
            filtros_layout.addWidget(btn)
            self.btn_filtros[estado] = btn
        filtros_layout.addStretch()
        root.addLayout(filtros_layout)

        self.resumen_label = QLabel("Cargando envíos…")
        root.addWidget(self.resumen_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QFrame()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(12)
        self.scroll.setWidget(self.scroll_content)
        root.addWidget(self.scroll, 1)

        self.cambiar_filtro(None)

    # ------------------------------------------------------------------
    def cambiar_filtro(self, estado):
        for est, btn in self.btn_filtros.items():
            btn.setChecked(est == estado)
        self.estado_actual = estado
        self.refrescar_tablero()

    # ------------------------------------------------------------------
    def refrescar_tablero(self):
        self.cargar_datos()
        self.pintar_resumen()
        self.construir_tarjetas()

    # ------------------------------------------------------------------
    def cargar_datos(self):
        with get_session() as db:
            svc = RepartoService(db)
            self.repartos = svc.listar(self.estado_actual)
            self.resumen = svc.resumen_por_estado()

    # ------------------------------------------------------------------
    def pintar_resumen(self):
        total = sum(self.resumen.values())
        resumen_txt = (
            f"Total envíos: {total} | "
            f"En ruta: {self.resumen.get('EN_RUTA', 0)} | "
            f"Entregados: {self.resumen.get('ENTREGADO', 0)} | "
            f"Devueltos: {self.resumen.get('DEVUELTO', 0)}"
        )
        self.resumen_label.setText(resumen_txt)

    # ------------------------------------------------------------------
    def construir_tarjetas(self):
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if not self.repartos:
            vacio = QLabel("No hay envíos con este filtro.")
            vacio.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(vacio, 0, 0)
            return

        columnas = 3
        for idx, reparto in enumerate(self.repartos):
            fila = idx // columnas
            col = idx % columnas
            tarjeta = DeliveryCard(reparto)
            self.grid.addWidget(tarjeta, fila, col)
