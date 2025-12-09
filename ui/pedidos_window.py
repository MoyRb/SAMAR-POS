from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QGridLayout, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QApplication
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

        self.tbl_items = QTableWidget(0, 4)
        self.tbl_items.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio", ""])
        self.tbl_items.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_panel.addWidget(self.tbl_items)

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

        print(">>> Cargando productos…")
        self.cargar_productos()
        print(">>> Productos cargados correctamente.")

        self.centrar_ventana()
        print(">>> PedidosWindow inicializado OK.")

    # -----------------------------------------------------------
    def centrar_ventana(self):
        screen = QApplication.primaryScreen().geometry()
        x = max(0, screen.width()//2 - self.width()//2)
        y = max(0, screen.height()//2 - self.height()//2)
        self.move(x, y)
        print(f">>> Ventana centrada en: {x}, {y}")

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

        self.total = total
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

        with get_session() as db:
            svc = PedidoService(db)
            pedido = svc.nuevo(self.usuario["id"])

            for p in self.items_pedido:
                svc.agregar_item(pedido.id, p["id"], 1, float(p["precio"]))

            pedido = svc.calcular_totales(pedido.id)

            pedido_dict = {
                "id": pedido.id,
                "folio": pedido.folio,
                "subtotal": float(pedido.subtotal),
                "total": float(pedido.total),
                "pagado": pedido.pagado
            }

        # Cerrar ventana actual
        self.close()

        # Abrir cobro SIN parent
        self.cobro = CobroWindow(pedido_dict)
        self.cobro.show()
        self.cobro.raise_()
        self.cobro.activateWindow()
