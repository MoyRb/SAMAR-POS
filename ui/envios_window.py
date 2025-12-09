## ui/envios_window.py
# Ventana dedicada a la asignación y seguimiento de envíos y repartidores.
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QMessageBox,
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

        btn_refrescar = QPushButton("🔄 Actualizar")
        btn_refrescar.setObjectName("btnSecondary")
        btn_refrescar.clicked.connect(self.refrescar_tablero)
        header.addWidget(btn_refrescar)
        root.addLayout(header)

        self.resumen_label = QLabel("Cargando envíos…")
        root.addWidget(self.resumen_label)

        columnas_layout = QHBoxLayout()
        columnas_layout.setSpacing(16)

        self.columnas = {
            "ASIGNADO": self._crear_columna("Asignado"),
            "EN_RUTA": self._crear_columna("En ruta"),
            "ENTREGADO": self._crear_columna("Entregado"),
            "DEVUELTO": self._crear_columna("Devuelto"),
        }

        for columna in self.columnas.values():
            columnas_layout.addWidget(columna["container"], 1)

        root.addLayout(columnas_layout)

        self.refrescar_tablero()

    # ------------------------------------------------------------------
    def _crear_columna(self, titulo):
        caja = QFrame()
        layout = QVBoxLayout(caja)
        layout.setSpacing(10)

        header = QLabel(titulo)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-weight: 700; font-size: 15px;")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenido = QFrame()
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
    def refrescar_tablero(self):
        try:
            self.cargar_datos()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los envíos:\n{exc}")
            return

        self.pintar_resumen()
        self.construir_tarjetas()

    # ------------------------------------------------------------------
    def cargar_datos(self):
        with get_session() as db:
            svc = RepartoService(db)
            self.repartos = svc.listar()
            self.resumen = svc.resumen_por_estado()

    # ------------------------------------------------------------------
    def pintar_resumen(self):
        total = sum(self.resumen.values())
        resumen_txt = (
            f"Total envíos: {total} | "
            f"Asignados: {self.resumen.get('ASIGNADO', 0)} | "
            f"En ruta: {self.resumen.get('EN_RUTA', 0)} | "
            f"Entregados: {self.resumen.get('ENTREGADO', 0)} | "
            f"Devueltos: {self.resumen.get('DEVUELTO', 0)}"
        )
        self.resumen_label.setText(resumen_txt)

    # ------------------------------------------------------------------
    def construir_tarjetas(self):
        for columna in self.columnas.values():
            self.limpiar_columna(columna)

        if not self.repartos:
            for columna in self.columnas.values():
                columna["layout"].insertWidget(
                    columna["layout"].count() - 1,
                    QLabel("Sin envíos en esta sección"),
                )
            return

        for reparto in self.repartos:
            columna = self.columnas.get(reparto.estado)
            if not columna:
                continue

            tarjeta = DeliveryCard(reparto, on_cambiar_estado=self.cambiar_estado_reparto)
            columna["layout"].insertWidget(columna["layout"].count() - 1, tarjeta)

    # ------------------------------------------------------------------
    def cambiar_estado_reparto(self, reparto, nuevo_estado):
        try:
            with get_session() as db:
                svc = RepartoService(db)
                svc.cambiar_estado(reparto.id, nuevo_estado)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el envío:\n{exc}")
            return

        self.refrescar_tablero()
