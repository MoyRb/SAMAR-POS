# ui/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
import traceback

from ui.pedidos_window import PedidosWindow
from ui.kds_window import KdsWindow
from ui.corte_window import CorteWindow


class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario

        self.setWindowTitle(f"SAMAR-POS | Bienvenido {usuario['nombre']}")
        self.setFixedSize(800, 500)
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        titulo = QLabel("🍕 Panel Principal SAMAR-POS")
        titulo.setObjectName("logoTitle")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel(f"Usuario activo: {usuario['nombre']}  |  Rol ID: {usuario['rol_id']}")
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)

        botones = QHBoxLayout()
        botones.setSpacing(30)

        btn_pedidos = QPushButton("🧾 Pedidos (F1)")
        btn_pedidos.setObjectName("btnPrimary")
        btn_pedidos.clicked.connect(self.abrir_pedidos)
        botones.addWidget(btn_pedidos)

        btn_kds = QPushButton("🍳 Cocina (F2)")
        btn_kds.setObjectName("btnPrimary")
        btn_kds.clicked.connect(self.abrir_kds)
        botones.addWidget(btn_kds)

        btn_corte = QPushButton("💵 Corte Diario (F3)")
        btn_corte.setObjectName("btnPrimary")
        btn_corte.clicked.connect(self.abrir_corte)
        botones.addWidget(btn_corte)

        layout.addLayout(botones)
        central.setLayout(layout)
        self.setCentralWidget(central)

        QShortcut(QKeySequence("F1"), self, activated=self.abrir_pedidos)
        QShortcut(QKeySequence("F2"), self, activated=self.abrir_kds)
        QShortcut(QKeySequence("F3"), self, activated=self.abrir_corte)

    def abrir_pedidos(self):
        try:
            print("\n=== Intentando abrir PedidosWindow ===\n")

            self.pedidos_window = PedidosWindow(self.usuario, on_close=self.show)
            self.pedidos_window.show()
            self.pedidos_window.raise_()
            self.pedidos_window.activateWindow()

            print(">>> PedidosWindow se abrió correctamente.\n")

            self.hide()

        except Exception as e:
            print("\n🔥 ERROR AL ABRIR PEDIDOS 🔥\n")
            print(e)
            self.show()


        except Exception:
            print("\n🔥🔥🔥 ERROR AL ABRIR PEDIDOS 🔥🔥🔥\n")
            traceback.print_exc()
            print("\n---------------------------------------\n")
            self.show()

    def abrir_kds(self):
        try:
            print("\n=== Intentando abrir KdsWindow ===\n")

            self.kds_window = KdsWindow(self.usuario, on_close=self.show)
            self.kds_window.show()
            self.kds_window.raise_()
            self.kds_window.activateWindow()

            print(">>> KdsWindow se abrió correctamente.\n")

            self.hide()

        except Exception:
            print("\n🔥🔥🔥 ERROR AL ABRIR KDS 🔥🔥🔥\n")
            traceback.print_exc()
            print("\n---------------------------------------\n")
            self.show()

    def abrir_corte(self):
        try:
            print("\n=== Intentando abrir CorteWindow ===\n")

            self.corte_window = CorteWindow(self.usuario, on_close=self.show)
            self.corte_window.show()
            self.corte_window.raise_()
            self.corte_window.activateWindow()

            print(">>> CorteWindow se abrió correctamente.\n")

            self.hide()

        except Exception:
            print("\n🔥🔥🔥 ERROR AL ABRIR CORTE 🔥🔥🔥\n")
            traceback.print_exc()
            print("\n---------------------------------------\n")
            self.show()
