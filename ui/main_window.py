# ui/main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

from ui.pedidos_window import PedidosWindow
import traceback


class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario

        self.setWindowTitle(f"SAMAR-POS | Bienvenido {usuario['nombre']}")
        self.setFixedSize(800, 500)
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())

        # --- Contenedor principal ---
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        # --- Título ---
        titulo = QLabel("🍕 Panel Principal SAMAR-POS")
        titulo.setObjectName("logoTitle")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # --- Subtítulo con nombre ---
        subtitulo = QLabel(f"Usuario activo: {usuario['nombre']}  |  Rol ID: {usuario['rol_id']}")
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)

        # --- Botones ---
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(30)

        btn_pedidos = QPushButton("🧾 Pedidos (F1)")
        btn_pedidos.setObjectName("btnPrimary")
        btn_pedidos.clicked.connect(self.abrir_pedidos)  # 👈 EXISTE
        botones_layout.addWidget(btn_pedidos)

        btn_kds = QPushButton("🍳 Cocina (F2)")
        btn_kds.setObjectName("btnPrimary")
        btn_kds.clicked.connect(lambda: print("Abrir KDS (por implementar)"))
        botones_layout.addWidget(btn_kds)

        btn_corte = QPushButton("💵 Corte Diario (F3)")
        btn_corte.setObjectName("btnPrimary")
        btn_corte.clicked.connect(lambda: print("Abrir Corte Diario (por implementar)"))
        botones_layout.addWidget(btn_corte)

        layout.addLayout(botones_layout)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # --- Atajos ---
        QShortcut(QKeySequence("F1"), self, activated=self.abrir_pedidos)
        QShortcut(QKeySequence("F2"), self, activated=lambda: print("Abrir KDS (por implementar)"))
        QShortcut(QKeySequence("F3"), self, activated=lambda: print("Abrir Corte Diario (por implementar)"))

    # ---------------------------------------------------
    # 👇 AQUI ESTABA EL PROBLEMA: NO EXISTÍA / MAL INDENTADO
    # ---------------------------------------------------
    def abrir_pedidos(self):
        """Abre la ventana de pedidos evitando ocultar la ventana hija."""
        try:
            print("\n=== Intentando abrir PedidosWindow ===\n")

            # ❗ SIN parent, para que no desaparezca cuando se oculte esta ventana
            self.pedidos_window = PedidosWindow(self.usuario)
            self.pedidos_window.show()
            self.pedidos_window.raise_()

            print(">>> PedidosWindow se abrió correctamente.\n")

            # Ocultamos el menú después de mostrar la ventana nueva
            self.hide()

        except Exception as e:
            print("\n🔥🔥🔥 ERROR AL ABRIR PEDIDOS 🔥🔥🔥\n")
            traceback.print_exc()
            print("\n---------------------------------------\n")
            self.show()
