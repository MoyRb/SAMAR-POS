from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt


class DeliveryCard(QFrame):
    def __init__(self, reparto):
        super().__init__()
        self.reparto = reparto
        self.pedido = reparto.pedido
        self.cliente = getattr(self.pedido, "cliente", None)
        self.setObjectName("card")

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.addWidget(self._pill(self.pedido.estado, "#7c3aed"))
        header.addWidget(self._pill(self.reparto.estado, self._estado_color()))
        header.addStretch()
        layout.addLayout(header)

        layout.addWidget(self._label_line(f"#{self.pedido.folio or self.pedido.id}", bold=True, size=16))
        layout.addWidget(self._label_line(self._cliente_text()))
        layout.addWidget(self._label_line(self._direccion_text()))

        extra = QHBoxLayout()
        extra.addWidget(self._label_line(f"Repartidor: {self.reparto.repartidor or 'Sin asignar'}"))
        extra.addStretch()
        extra.addWidget(self._pill(self._pago_texto(), "#fb923c", text_color="#0f172a"))
        layout.addLayout(extra)

        footer = QHBoxLayout()
        footer.addWidget(self._label_line(self._telefono_text()))
        footer.addStretch()
        footer.addWidget(self._label_line(self._total_texto(), bold=True))
        layout.addLayout(footer)

    # helpers -------------------------------------------------
    def _pill(self, text, color, text_color="#f8fafc"):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"background-color: {color}; color: {text_color}; padding: 4px 8px; border-radius: 12px; font-weight: 600;"
        )
        return lbl

    def _label_line(self, text, bold=False, size=12):
        lbl = QLabel(text)
        font = lbl.font()
        font.setPointSize(size)
        font.setBold(bold)
        lbl.setFont(font)
        return lbl

    def _cliente_text(self):
        if self.cliente:
            return f"Cliente: {self.cliente.nombre}"
        return "Cliente: Sin datos"

    def _telefono_text(self):
        if self.cliente and self.cliente.telefono:
            return f"Tel: {self.cliente.telefono}"
        return "Tel: -"

    def _direccion_text(self):
        direccion = self.pedido.direccion_entrega or (self.cliente.direccion if self.cliente else None)
        return f"Dirección: {direccion or 'No especificada'}"

    def _total_texto(self):
        total = float(self.pedido.total or 0)
        return f"Total: ${total:,.2f}"

    def _pago_texto(self):
        return "Pagado" if self.pedido.pagado else "Pendiente"

    def _estado_color(self):
        colores = {
            "ASIGNADO": "#2563eb",
            "EN_RUTA": "#10b981",
            "ENTREGADO": "#22c55e",
            "DEVUELTO": "#ef4444",
        }
        return colores.get(self.reparto.estado, "#475569")
