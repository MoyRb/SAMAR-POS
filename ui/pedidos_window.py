# ui/pedidos_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QGridLayout, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from utils.db_session import get_session
from services.catalogo_service import CatalogoService
from services.pedido_service import PedidoService


class PedidosWindow(QWidget):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario

        self.setWindowTitle("SAMAR-POS | Nueva Orden")
        self.resize(1200, 700)
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())

        # ⬛ Corrección CRÍTICA: layout sin self
        layout = QHBoxLayout()
        self.setLayout(layout)

        # === PANEL IZQUIERDO ===
        left_panel = QVBoxLayout()

        lbl_buscar = QLabel("Buscar producto:")
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Ejemplo: pizza, bebida...")
        self.input_buscar.textChanged.connect(self.buscar_producto)

        left_panel.addWidget(lbl_buscar)
        left_panel.addWidget(self.input_buscar)

        # Scroll de productos
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)

        self.scroll.setWidget(self.grid_widget)
        left_panel.addWidget(self.scroll)

        # === PANEL DERECHO ===
        right_panel = QVBoxLayout()

        self.lbl_pedido = QLabel("Pedido temporal")
        self.lbl_pedido.setAlignment(Qt.AlignCenter)
        self.lbl_pedido.setObjectName("logoTitle")
        right_panel.addWidget(self.lbl_pedido)

        self.tbl_items = QTableWidget(0, 3)
        self.tbl_items.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio"])
        self.tbl_items.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_panel.addWidget(self.tbl_items)

        self.lbl_total = QLabel("Total: $0.00")
        self.lbl_total.setAlignment(Qt.AlignRight)
        right_panel.addWidget(self.lbl_total)

        self.btn_guardar = QPushButton("💾 Guardar Pedido (F5)")
        self.btn_guardar.setObjectName("btnPrimary")
        self.btn_guardar.clicked.connect(self.guardar_pedido)
        right_panel.addWidget(self.btn_guardar)

        layout.addLayout(left_panel, 2)
        layout.addLayout(right_panel, 1)

        # Datos internos
        self.productos = []
        self.items_pedido = []
        self.total = 0.0

        # Centrar la ventana
        self._center_on_screen()

        self.cargar_productos()

    # === Centrado ===
    def _center_on_screen(self):
        screen = self.screen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

    # === Productos ===
    def cargar_productos(self):
        """Carga todos los productos activos de la base."""
        with get_session() as db:
            svc = CatalogoService(db)
            self.productos = svc.listar()

        # Limpia grid
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                item.widget().deleteLater()

        # Muestra productos
        for i, prod in enumerate(self.productos):
            card = self.crear_tarjeta_producto(prod)
            self.grid_layout.addWidget(card, i // 3, i % 3)

    def crear_tarjeta_producto(self, producto):
        """Crea una tarjeta visual para cada producto."""
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

    # === Buscar ===
    def buscar_producto(self):
        texto = self.input_buscar.text().strip().lower()
        for i, prod in enumerate(self.productos):
            card = self.grid_layout.itemAt(i).widget()
            visible = texto in prod["nombre"].lower() or texto == ""
            card.setVisible(visible)

    # === Agregar item ===
    def agregar_item(self, producto):
        self.items_pedido.append(producto)

        row = self.tbl_items.rowCount()
        self.tbl_items.insertRow(row)

        self.tbl_items.setItem(row, 0, QTableWidgetItem(producto["nombre"]))
        self.tbl_items.setItem(row, 1, QTableWidgetItem("1"))
        self.tbl_items.setItem(row, 2, QTableWidgetItem(f"${float(producto['precio']):.2f}"))

        self.total += float(producto["precio"])
        self.lbl_total.setText(f"Total: ${self.total:.2f}")

    # === Guardar ===
    def guardar_pedido(self):
        if not self.items_pedido:
            QMessageBox.warning(self, "Pedido vacío", "Agrega al menos un producto.")
            return

        with get_session() as db:
            svc = PedidoService(db)
            pedido = svc.nuevo(self.usuario["id"])

            for p in self.items_pedido:
                svc.agregar_item(pedido.id, p["id"], 1, p["precio"])

            svc.calcular_totales(pedido.id)

        QMessageBox.information(self, "Guardado", "Pedido registrado correctamente.")
        self.tbl_items.setRowCount(0)
        self.items_pedido.clear()
        self.total = 0.0
        self.lbl_total.setText("Total: $0.00")
