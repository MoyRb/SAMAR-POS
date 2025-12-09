from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class CorteWindow(QWidget):
    """Vista sencilla para corte diario."""

    def __init__(self, usuario, on_close=None):
        super().__init__(None)
        self.usuario = usuario
        self.on_close = on_close

        self.setWindowFlag(Qt.Window)
        self.setWindowTitle("SAMAR-POS | Corte Diario")
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())
        self.resize(700, 500)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        titulo = QLabel("💵 Corte Diario")
        titulo.setObjectName("logoTitle")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel(
            f"Usuario: {usuario['nombre']}  |  Rol ID: {usuario['rol_id']}  |  Acceso rápido: F3"
        )
        subtitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitulo)

        placeholder = QLabel("En construcción: aquí podrás generar y revisar el corte.")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)

    def closeEvent(self, event):
        if self.on_close:
            self.on_close()
        event.accept()
