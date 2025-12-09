from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class KdsWindow(QWidget):
    """Tablero simple de cocina para seguir pedidos."""

    def __init__(self, usuario, on_close=None):
        super().__init__(None)
        self.usuario = usuario
        self.on_close = on_close

        self.setWindowFlag(Qt.Window)
        self.setWindowTitle("SAMAR-POS | Cocina")
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        titulo = QLabel("🍳 Tablero de Cocina")
        titulo.setObjectName("logoTitle")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel(
            f"Usuario: {usuario['nombre']}  |  Rol ID: {usuario['rol_id']}  |  Acceso rápido: F2"
        )
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)

        placeholder = QLabel("En construcción: aquí se listarán los pedidos en preparación.")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)

    def closeEvent(self, event):
        if self.on_close:
            self.on_close()
        event.accept()
