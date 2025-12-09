## ui/main_window.py
# Ventana principal que agrupa accesos rápidos a los módulos del sistema.
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
import traceback

import ui.window_manager as wm


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

        btn_envios = QPushButton("🚚 Envíos (F4)")
        btn_envios.setObjectName("btnPrimary")
        btn_envios.clicked.connect(self.abrir_envios)
        botones.addWidget(btn_envios)

        layout.addLayout(botones)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def abrir_pedidos(self):
        try:
            print("\n=== Intentando abrir PedidosWindow ===\n")

            wm.show_pedidos_window()

            print(">>> PedidosWindow se abrió correctamente.\n")

        except Exception as e:
            print("\n🔥 ERROR AL ABRIR PEDIDOS 🔥\n")
            print(e)


        except Exception:
            print("\n🔥🔥🔥 ERROR AL ABRIR PEDIDOS 🔥🔥🔥\n")
            traceback.print_exc()
            print("\n---------------------------------------\n")

    def abrir_corte(self):
        try:
            print("\n=== Intentando abrir CorteWindow ===\n")

            wm.show_corte_window()

            print(">>> CorteWindow se abrió correctamente.\n")

        except Exception as e:
            print("\n🔥 ERROR AL ABRIR CORTE 🔥\n")
            print(e)

        except Exception:
            print("\n🔥🔥🔥 ERROR AL ABRIR CORTE 🔥🔥🔥\n")
            traceback.print_exc()
            print("\n---------------------------------------\n")

    def abrir_envios(self):
        try:
            print("\n=== Intentando abrir EnviosWindow ===\n")

            wm.show_envios_window()

            print(">>> EnviosWindow se abrió correctamente.\n")

        except Exception as e:
            print("\n🔥 ERROR AL ABRIR ENVIOS 🔥\n")
            print(e)

        except Exception:
            print("\n🔥🔥🔥 ERROR AL ABRIR ENVIOS 🔥🔥🔥\n")
            traceback.print_exc()
            print("\n---------------------------------------\n")

    def abrir_kds(self):
        try:
            print("\n=== Intentando abrir KDSWindow ===\n")

            wm.show_kds_window()

            print(">>> KDSWindow se abrió correctamente.\n")

        except Exception as e:
            print("\n🔥 ERROR AL ABRIR KDS 🔥\n")
            print(e)

        except Exception:
            print("\n🔥🔥🔥 ERROR AL ABRIR KDS 🔥🔥🔥\n")
            traceback.print_exc()
            print("\n---------------------------------------\n")
