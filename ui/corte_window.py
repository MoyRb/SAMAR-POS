from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt

from utils.db_session import get_session
from services.corte_service import CorteService


class CorteWindow(QWidget):
    """Ventana sencilla para consultar el corte diario en curso."""

    def __init__(self, usuario):
        super().__init__(None)
        self.usuario = usuario

        self.setWindowFlag(Qt.Window)
        self.setWindowModality(Qt.NonModal)
        self.setWindowTitle("SAMAR-POS | Corte diario")
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(15)

        titulo = QLabel("💵 Corte diario")
        titulo.setObjectName("logoTitle")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        self.lbl_salon = QLabel()
        self.lbl_salon.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_salon)

        self.lbl_total_general = QLabel()
        self.lbl_total_general.setAlignment(Qt.AlignCenter)
        self.lbl_total_general.setObjectName("highlightText")
        layout.addWidget(self.lbl_total_general)

        self.tabla_repartidores = QTableWidget(0, 2)
        self.tabla_repartidores.setHorizontalHeaderLabels(["Repartidor", "Total cobrado"])
        self.tabla_repartidores.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_repartidores)

        btn_refrescar = QPushButton("🔄 Actualizar datos")
        btn_refrescar.setObjectName("btnPrimary")
        btn_refrescar.clicked.connect(self.cargar_resumen)
        layout.addWidget(btn_refrescar)

        self.cargar_resumen()

    def cargar_resumen(self):
        """Consulta los totales actuales y refresca los widgets."""
        with get_session() as db:
            resumen = CorteService(db).resumen_repartidores_y_salon()

        salon_total = resumen.get("salon", 0.0)
        self.lbl_salon.setText(f"Ventas en salón: ${salon_total:,.2f}")

        repartidores = resumen.get("repartidores", {})
        self.tabla_repartidores.setRowCount(len(repartidores))

        for row, (nombre, total) in enumerate(repartidores.items()):
            self.tabla_repartidores.setItem(row, 0, QTableWidgetItem(nombre or "Sin nombre"))
            self.tabla_repartidores.setItem(row, 1, QTableWidgetItem(f"${float(total):,.2f}"))

        total_general = salon_total + sum(float(t or 0) for t in repartidores.values())
        self.lbl_total_general.setText(f"Total general: ${total_general:,.2f}")
