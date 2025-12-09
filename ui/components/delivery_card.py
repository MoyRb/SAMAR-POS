from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt


class DeliveryCard(QFrame):
    def __init__(self, reparto, on_cambiar_estado=None):
        super().__init__()
        self.reparto = reparto
        self.pedido = reparto.pedido
        self.on_cambiar_estado = on_cambiar_estado
        self.setObjectName("card")

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.addWidget(self._pill(self.pedido.estado, "#7c3aed"))
        header.addWidget(self._pill(self.reparto.estado, self._estado_color()))
        header.addStretch()
        layout.addLayout(header)

        layout.addWidget(self._label_line(f"#{self.pedido.folio or self.pedido.id}", bold=True, size=16))
        layout.addWidget(self._label_line(self._direccion_text()))
        layout.addWidget(self._label_line(self._canal_text()))

        extra = QHBoxLayout()
        extra.addWidget(self._label_line(f"Repartidor: {self.reparto.repartidor or 'Sin asignar'}"))
        extra.addStretch()
        extra.addWidget(self._pill(self._pago_texto(), "#fb923c", text_color="#0f172a"))
        layout.addLayout(extra)

        footer = QHBoxLayout()
        envio_text = self._envio_text()
        if envio_text:
            footer.addWidget(self._label_line(envio_text))
        else:
            footer.addStretch()
        footer.addStretch()
        footer.addWidget(self._label_line(self._total_texto(), bold=True))
        layout.addLayout(footer)

        acciones = self._acciones_layout()
        if acciones:
            layout.addLayout(acciones)

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

    def _canal_text(self):
        canal = getattr(self.pedido, "canal", "SALON") or "SALON"
        return f"Canal: {canal.title()}"

    def _direccion_text(self):
        direccion = self.pedido.direccion_entrega
        return f"Dirección: {direccion or 'No especificada'}"

    def _total_texto(self):
        total = float(self.pedido.total or 0)
        return f"Total: ${total:,.2f}"

    def _pago_texto(self):
        return "Pagado" if self.pedido.pagado else "Pendiente"

    def _envio_text(self):
        try:
            costo_envio = float(self.pedido.envio or 0)
        except (TypeError, ValueError):
            return ""

        if costo_envio <= 0:
            return ""
        return f"Envío: ${costo_envio:,.2f}"

    def _estado_color(self):
        colores = {
            "ASIGNADO": "#2563eb",
            "EN_RUTA": "#10b981",
            "ENTREGADO": "#22c55e",
            "DEVUELTO": "#ef4444",
        }
        return colores.get(self.reparto.estado, "#475569")

    def _acciones_layout(self):
        if not self.on_cambiar_estado:
            return None

        acciones = QHBoxLayout()
        estado = self.reparto.estado

        def add_btn(texto, destino, estilo="btnPrimary"):
            btn = QPushButton(texto)
            btn.setObjectName(estilo)
            btn.clicked.connect(lambda: self.on_cambiar_estado(self.reparto, destino))
            acciones.addWidget(btn)

        if estado == "ASIGNADO":
            add_btn("🚚 En ruta", "EN_RUTA")
        elif estado == "EN_RUTA":
            add_btn("✅ Entregado", "ENTREGADO")
            add_btn("↩️ Devuelto", "DEVUELTO", "btnSecondary")
        elif estado == "ENTREGADO":
            add_btn("↩️ En ruta", "EN_RUTA", "btnSecondary")
        elif estado == "DEVUELTO":
            add_btn("🚚 Reintentar", "EN_RUTA")

        acciones.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        return acciones
