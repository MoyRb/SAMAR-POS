# ui/login_window.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from services.auth_service import AuthService
from utils.db_session import get_session

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAMAR-POS | Inicio de Sesión")
        self.setFixedSize(380, 320)
        self.setStyleSheet(open("ui/theme_dark.qss", "r", encoding="utf-8").read())

        # Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(15)

        # Título o logo
        titulo = QLabel("🍕 SAMAR-POS")
        titulo.setObjectName("logoTitle")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Campo de usuario
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Usuario o correo electrónico")
        layout.addWidget(self.input_user)

        # Campo de contraseña
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Contraseña")
        self.input_pass.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_pass)

        # Recordarme
        self.remember_me = QCheckBox("Recordarme")
        layout.addWidget(self.remember_me)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.btn_login = QPushButton("Entrar")
        self.btn_login.setObjectName("btnPrimary")
        self.btn_login.clicked.connect(self.login)
        btn_layout.addWidget(self.btn_login)

        self.btn_exit = QPushButton("Salir")
        self.btn_exit.setObjectName("btnSecondary")
        self.btn_exit.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_exit)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Campos vacíos", "Ingresa usuario y contraseña.")
            return

        with get_session() as db:
            service = AuthService(db)
            user = service.autenticar(username, password)

        if user:
            QMessageBox.information(self, "Bienvenido", f"Acceso correcto: {user.nombre}")
            # TODO: abrir ventana principal (main_window)
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")
