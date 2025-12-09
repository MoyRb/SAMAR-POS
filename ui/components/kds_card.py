"""Tarjeta visual para representar pedidos en el KDS."""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy


class KDSCard(QFrame):
    """Widget compacto que muestra la información de un pedido y acciones KDS."""

    STATUS_COLORS = {
        "EN_COLA": "#94a3b8",       # Gris
        "PREPARACION": "#fb923c",  # Naranja
        "EN_HORNO": "#fb923c",     # Naranja
        "LISTO": "#22c55e",        # Verde
    }

    STATUS_LABELS = {
        "EN_COLA": "En cola",
        "PREPARACION": "En preparación",
        "EN_HORNO": "En preparación",
        "LISTO": "Listo",
    }

    def __init__(self, pedido, on_avanzar, on_regresar=None):
        super().__init__()
        self.pedido = pedido
        self.on_avanzar = on_avanzar
        self.on_regresar = on_regresar

        self.setObjectName("kdsCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setLayout(self._build_layout())
        self._apply_status_style()

    # ------------------------------------------------------------------
    def _build_layout(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        header = QHBoxLayout()
        folio = QLabel(f"#{self.pedido.folio or self.pedido.id}")
        folio.setObjectName("kdsFolio")
        header.addWidget(folio)

        canal = QLabel(self._canal_text())
        canal.setObjectName("kdsBadge")
        header.addWidget(canal)

        header.addStretch()

        status = QLabel(self.STATUS_LABELS.get(self.pedido.estado, self.pedido.estado))
        status.setObjectName("kdsStatus")
        header.addWidget(status)

        layout.addLayout(header)

        if getattr(self.pedido, "mesa", None):
            mesa_lbl = QLabel(f"Mesa: <b>{self.pedido.mesa}</b>")
            layout.addWidget(mesa_lbl)

        items_layout = QVBoxLayout()
        items_layout.setSpacing(2)
        items_layout.addWidget(QLabel("Items:"))
        for item in getattr(self.pedido, "items", []):
            nombre = getattr(item.producto, "nombre", "Producto")
            cantidad = getattr(item, "cantidad", 1)
            items_layout.addWidget(QLabel(f"• {cantidad} x {nombre}"))
        layout.addLayout(items_layout)

        if getattr(self.pedido, "notas", None):
            notas = QLabel(f"📝 {self.pedido.notas}")
            notas.setWordWrap(True)
            layout.addWidget(notas)

        actions = QHBoxLayout()
        if self.pedido.estado != "LISTO":
            btn_avanzar = QPushButton(self._avanzar_text())
            btn_avanzar.setObjectName("btnPrimary")
            btn_avanzar.clicked.connect(lambda: self.on_avanzar(self.pedido))
            actions.addWidget(btn_avanzar)

        if self.on_regresar and self.pedido.estado in {"PREPARACION", "EN_HORNO"}:
            btn_regresar = QPushButton("↩️ Regresar a Cola")
            btn_regresar.setObjectName("btnSecondary")
            btn_regresar.clicked.connect(lambda: self.on_regresar(self.pedido))
            actions.addWidget(btn_regresar)

        actions.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(actions)

        return layout

    # ------------------------------------------------------------------
    def _avanzar_text(self):
        if self.pedido.estado == "EN_COLA":
            return "🧑‍🍳 Marcar preparación"
        return "✅ Marcar listo"

    # ------------------------------------------------------------------
    def _canal_text(self):
        canal = getattr(self.pedido, "canal", "")
        if canal == "DOMICILIO":
            return "Domicilio"
        if canal == "PARA_LLEVAR":
            return "Para llevar"
        return "Salón"

    # ------------------------------------------------------------------
    def _apply_status_style(self):
        border = self.STATUS_COLORS.get(self.pedido.estado, "#334155")
        text_color = "#0f172a" if self.pedido.estado in {"PREPARACION", "EN_HORNO", "LISTO"} else "#0f172a"
        self.setStyleSheet(
            f"""
            QFrame#kdsCard {{
                background-color: #0b1220;
                border: 2px solid {border};
                border-radius: 12px;
                padding: 8px 10px;
            }}
            QLabel#kdsBadge {{
                background-color: #1e293b;
                color: #e2e8f0;
                border-radius: 10px;
                padding: 2px 8px;
                font-size: 12px;
            }}
            QLabel#kdsStatus {{
                background-color: {border};
                color: {text_color};
                border-radius: 10px;
                padding: 2px 8px;
                font-weight: 700;
            }}
            QLabel#kdsFolio {{
                font-weight: 800;
                color: #f8fafc;
            }}
            """
        )

