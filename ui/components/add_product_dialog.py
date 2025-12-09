from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox,
    QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class AddProductDialog(QDialog):
    """Formulario simple para dar de alta productos desde la pantalla de ventas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir producto")
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)

        header = QLabel("Captura rápida de producto")
        header.setObjectName("logoTitle")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del producto")
        form.addRow("Nombre", self.nombre_input)

        self.categoria_input = QLineEdit()
        self.categoria_input.setPlaceholderText("Categoría (ej. Pizzas)")
        form.addRow("Categoría", self.categoria_input)

        self.precio_input = QDoubleSpinBox()
        self.precio_input.setPrefix("$")
        self.precio_input.setMaximum(1_000_000)
        self.precio_input.setDecimals(2)
        self.precio_input.setValue(99.00)
        form.addRow("Precio", self.precio_input)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_cancel)

        btn_save = QPushButton("Guardar")
        btn_save.setObjectName("btnPrimary")
        btn_save.clicked.connect(self._on_save)
        buttons.addWidget(btn_save)

        layout.addLayout(buttons)

    def _on_save(self):
        if not self.nombre_input.text().strip():
            QMessageBox.warning(self, "Falta nombre", "Captura el nombre del producto.")
            return

        if self.precio_input.value() <= 0:
            QMessageBox.warning(self, "Precio inválido", "El precio debe ser mayor a cero.")
            return

        self.accept()

    def obtener_datos(self):
        return {
            "nombre": self.nombre_input.text().strip(),
            "categoria": self.categoria_input.text().strip() or None,
            "precio": float(self.precio_input.value()),
        }
