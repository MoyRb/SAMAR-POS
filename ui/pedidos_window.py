## ui/pedidos_window.py
# Ventana para capturar y gestionar pedidos dentro del flujo de ventas.
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QGridLayout, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QApplication,
    QRadioButton, QButtonGroup, QFormLayout
)
from PySide6.QtCore import Qt

from utils.db_session import get_session
from services.catalogo_service import CatalogoService
from services.pedido_service import PedidoService
from ui.components.add_product_dialog import AddProductDialog


class PedidosWindow(QWidget):
    """Pantalla principal de pedidos."""

    def __init__(self, usuario):
        super().__init__(None)  # ← SIN PARENT, independiente SIEMPRE
        self.usuario = usuario

        print(">>> INICIANDO PedidosWindow...")

        # Eliminar la instancia cuando se cierre para evitar reutilizar datos viejos
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Ventana real independiente
        self.setWindowFlag(Qt.Window)
        self.setWindowModality(Qt.NonModal)

        self.setWindowTitle("SAMAR-POS | Nueva Orden")
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())
        self.resize(1200, 700)
        self.setMinimumSize(900, 600)

        layout = QHBoxLayout(self)

        # ============================
        # PANEL IZQUIERDO
        # ============================
        left_panel = QVBoxLayout()

        header_row = QHBoxLayout()
        lbl_buscar = QLabel("Buscar producto:")
        header_row.addWidget(lbl_buscar, 1)

        self.btn_nuevo_producto = QPushButton("➕ Añadir producto")
        self.btn_nuevo_producto.setObjectName("btnSecondary")
        self.btn_nuevo_producto.clicked.connect(self.abrir_dialogo_producto)
        header_row.addWidget(self.btn_nuevo_producto)

        left_panel.addLayout(header_row)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Escribe para filtrar por nombre…")
        self.input_buscar.textChanged.connect(self.buscar_producto)
        left_panel.addWidget(self.input_buscar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)

        self.scroll.setWidget(self.grid_widget)
        left_panel.addWidget(self.scroll)

        # ============================
        # PANEL DERECHO
        # ============================
        right_panel = QVBoxLayout()

        self.lbl_pedido = QLabel("Pedido temporal")
        self.lbl_pedido.setAlignment(Qt.AlignCenter)
        self.lbl_pedido.setObjectName("logoTitle")
        right_panel.addWidget(self.lbl_pedido)

        tipo_layout = QHBoxLayout()
        tipo_layout.addWidget(QLabel("Tipo de pedido:"))
        self.radio_salon = QRadioButton("Salón")
        self.radio_domicilio = QRadioButton("Domicilio")
        self.radio_salon.setChecked(True)

        self.canal_group = QButtonGroup(self)
        self.canal_group.addButton(self.radio_salon)
        self.canal_group.addButton(self.radio_domicilio)
        self.radio_salon.toggled.connect(self.actualizar_tipo_pedido)
        self.radio_domicilio.toggled.connect(self.actualizar_tipo_pedido)

        tipo_layout.addWidget(self.radio_salon)
        tipo_layout.addWidget(self.radio_domicilio)
        tipo_layout.addStretch()
        right_panel.addLayout(tipo_layout)

        self.panel_domicilio = QFrame()
        self.panel_domicilio.setObjectName("card")
        layout_domicilio = QFormLayout(self.panel_domicilio)
        layout_domicilio.setLabelAlignment(Qt.AlignLeft)

        self.input_calle = QLineEdit()
        self.input_calle.setPlaceholderText("Ej. Calle Reforma")
        layout_domicilio.addRow("Calle:", self.input_calle)

        self.input_localidad = QLineEdit()
        self.input_localidad.setPlaceholderText("Colonia o localidad")
        layout_domicilio.addRow("Localidad:", self.input_localidad)

        self.input_numero = QLineEdit()
        self.input_numero.setPlaceholderText("Número exterior")
        layout_domicilio.addRow("No. exterior:", self.input_numero)

        self.input_referencias = QLineEdit()
        self.input_referencias.setPlaceholderText("Referencias para encontrar la dirección")
        layout_domicilio.addRow("Referencias:", self.input_referencias)

        self.input_repartidor = QLineEdit()
        self.input_repartidor.setPlaceholderText("Nombre del repartidor")
        layout_domicilio.addRow("Repartidor:", self.input_repartidor)

        self.input_envio = QLineEdit()
        self.input_envio.setPlaceholderText("Costo de envío")
        self.input_envio.textChanged.connect(self.recalcular_total)
        layout_domicilio.addRow("Envío:", self.input_envio)

        right_panel.addWidget(self.panel_domicilio)

        self.tbl_items = QTableWidget(0, 4)
        self.tbl_items.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio", ""])
        self.tbl_items.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_panel.addWidget(self.tbl_items)

        self.lbl_envio = QLabel("Envío: $0.00")
        self.lbl_envio.setAlignment(Qt.AlignRight)
        self.lbl_envio.setVisible(False)
        right_panel.addWidget(self.lbl_envio)

        self.lbl_total = QLabel("Total: $0.00")
        self.lbl_total.setAlignment(Qt.AlignRight)
        right_panel.addWidget(self.lbl_total)

        btn_guardar = QPushButton("💾 Guardar Pedido (F5)")
        btn_guardar.setObjectName("btnPrimary")
        btn_guardar.clicked.connect(self.guardar_pedido)
        right_panel.addWidget(btn_guardar)

        layout.addLayout(left_panel, 2)
        layout.addLayout(right_panel, 1)

        # ESTADO INTERNO
        self.productos = []
        self.items_pedido = []
        self.total = 0.0
        self.envio = 0.0

        print(">>> Cargando productos…")
        self.cargar_productos()
        print(">>> Productos cargados correctamente.")

        self.actualizar_tipo_pedido()

        self.centrar_ventana()
        print(">>> PedidosWindow inicializado OK.")

    # -----------------------------------------------------------
    def resetear_formulario(self):
        """Limpia todos los campos para iniciar un nuevo pedido."""
        self.items_pedido.clear()
        self.tbl_items.setRowCount(0)

        self.input_buscar.clear()
        self.input_calle.clear()
        self.input_localidad.clear()
        self.input_numero.clear()
        self.input_referencias.clear()
        self.input_repartidor.clear()
        self.input_envio.clear()

        self.radio_salon.setChecked(True)

        self.envio = 0.0
        self.total = 0.0
        self.lbl_envio.setText("Envío: $0.00")
        self.lbl_total.setText("Total: $0.00")
        self.lbl_pedido.setText("Pedido temporal")

        self.actualizar_tipo_pedido()

    # -----------------------------------------------------------
    def centrar_ventana(self):
        screen = QApplication.primaryScreen().geometry()
        x = max(0, screen.width()//2 - self.width()//2)
        y = max(0, screen.height()//2 - self.height()//2)
        self.move(x, y)
        print(f">>> Ventana centrada en: {x}, {y}")

    # -----------------------------------------------------------
    def es_domicilio(self):
        return self.radio_domicilio.isChecked()

    # -----------------------------------------------------------
    def actualizar_tipo_pedido(self):
        es_envio = self.es_domicilio()
        self.panel_domicilio.setVisible(es_envio)
        self.lbl_envio.setVisible(es_envio)
        self.recalcular_total()

    # -----------------------------------------------------------
    def obtener_envio(self):
        if not self.es_domicilio():
            return 0.0

        try:
            return float(self.input_envio.text() or 0)
        except ValueError:
            return 0.0

    # -----------------------------------------------------------
    def cargar_productos(self):
        with get_session() as db:
            svc = CatalogoService(db)
            self.productos = svc.listar()

        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        for i, prod in enumerate(self.productos):
            card = self.crear_tarjeta_producto(prod)
            self.grid_layout.addWidget(card, i // 3, i % 3)

        self.buscar_producto()

    # -----------------------------------------------------------
    def crear_tarjeta_producto(self, producto):
        card = QFrame()
        card.setObjectName("card")
        vbox = QVBoxLayout(card)

        lbl_nombre = QLabel(f"<b>{producto['nombre']}</b>")
        lbl_precio = QLabel(f"${float(producto['precio']):.2f}")

        btn_add = QPushButton("+ Agregar")
        btn_add.setObjectName("btnPrimary")
        btn_add.clicked.connect(lambda: self.agregar_item(producto))

        vbox.addWidget(lbl_nombre)
        vbox.addWidget(lbl_precio)
        vbox.addWidget(btn_add)
        return card

    # -----------------------------------------------------------
    def buscar_producto(self):
        texto = self.input_buscar.text().lower()
        for i, prod in enumerate(self.productos):
            card = self.grid_layout.itemAt(i).widget()
            card.setVisible(texto in prod["nombre"].lower() or not texto)

    # -----------------------------------------------------------
    def agregar_item(self, producto):
        self.items_pedido.append(producto)

        row = self.tbl_items.rowCount()
        self.tbl_items.insertRow(row)
        self.tbl_items.setItem(row, 0, QTableWidgetItem(producto["nombre"]))
        self.tbl_items.setItem(row, 1, QTableWidgetItem("1"))
        self.tbl_items.setItem(row, 2, QTableWidgetItem(f"${float(producto['precio']):.2f}"))

        btn_quitar = QPushButton("🗑 Quitar")
        btn_quitar.setObjectName("btnSecondary")
        btn_quitar.clicked.connect(lambda _, b=btn_quitar: self.eliminar_item_desde_boton(b))
        self.tbl_items.setCellWidget(row, 3, btn_quitar)

        self.recalcular_total()

    # -----------------------------------------------------------
    def eliminar_item_desde_boton(self, boton):
        index = self.tbl_items.indexAt(boton.parent().pos())
        if not index.isValid():
            return

        row = index.row()

        if 0 <= row < len(self.items_pedido):
            eliminado = self.items_pedido.pop(row)
            self.tbl_items.removeRow(row)
            self.recalcular_total()

    # -----------------------------------------------------------
    def recalcular_total(self):
        total = 0.0
        for i, producto in enumerate(self.items_pedido):
            cantidad_item = self.tbl_items.item(i, 1)
            try:
                cantidad = int(cantidad_item.text()) if cantidad_item else 1
            except ValueError:
                cantidad = 1

            total += float(producto["precio"]) * cantidad

        self.envio = self.obtener_envio()
        total_con_envio = total + self.envio

        self.total = total_con_envio
        self.lbl_envio.setText(f"Envío: ${self.envio:.2f}")
        self.lbl_total.setText(f"Total: ${self.total:.2f}")

    # -----------------------------------------------------------
    def abrir_dialogo_producto(self):
        dialog = AddProductDialog(self)
        if not dialog.exec():
            return

        data = dialog.obtener_datos()
        try:
            with get_session() as db:
                svc = CatalogoService(db)
                svc.crear_producto(
                    nombre=data["nombre"],
                    precio=data["precio"],
                    categoria_nombre=data["categoria"],
                )

            QMessageBox.information(
                self,
                "Producto guardado",
                f"{data['nombre']} agregado al catálogo.",
            )
            self.cargar_productos()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error al guardar",
                f"No se pudo crear el producto.\n{exc}",
            )

    # -----------------------------------------------------------
    def guardar_pedido(self):
        if not self.items_pedido:
            QMessageBox.warning(self, "Pedido vacío", "Agrega al menos un producto.")
            return

        from ui.cobro_window import CobroWindow

        canal = "DOMICILIO" if self.es_domicilio() else "SALON"
        envio = self.obtener_envio()

        direccion = None
        repartidor = None

        if canal == "DOMICILIO":
            calle = self.input_calle.text().strip()
            localidad = self.input_localidad.text().strip()
            numero = self.input_numero.text().strip()
            referencias = self.input_referencias.text().strip()
            repartidor = self.input_repartidor.text().strip()

            if not all([calle, localidad, numero, repartidor]):
                QMessageBox.warning(
                    self,
                    "Faltan datos",
                    "Completa calle, localidad, número exterior y repartidor para el envío.",
                )
                return

            direccion_parts = [f"{calle} #{numero}", localidad]
            if referencias:
                direccion_parts.append(f"Ref: {referencias}")
            direccion = " | ".join(direccion_parts)

        with get_session() as db:
            svc = PedidoService(db)
            pedido = svc.nuevo(
                self.usuario["id"],
                canal=canal,
                envio=envio,
                direccion_entrega=direccion,
            )

            for p in self.items_pedido:
                svc.agregar_item(pedido.id, p["id"], 1, float(p["precio"]))

            pedido = svc.calcular_totales(pedido.id)

            if repartidor:
                reparto = svc.asignar_reparto(pedido.id, repartidor, notas=direccion)
            else:
                reparto = None

            pedido_dict = {
                "id": pedido.id,
                "folio": pedido.folio,
                "subtotal": float(pedido.subtotal),
                "total": float(pedido.total),
                "pagado": pedido.pagado,
                "canal": canal,
                "envio": float(pedido.envio or 0),
                "direccion": direccion,
                "repartidor": reparto.repartidor if reparto else None,
            }

        # Ocultar ventana actual mientras se realiza el cobro
        self.hide()

        # Abrir cobro SIN parent y enlazar para limpiar el formulario al terminar
        self.cobro = CobroWindow(pedido_dict, pedidos_window=self)
        self.cobro.show()
        self.cobro.raise_()
        self.cobro.activateWindow()
