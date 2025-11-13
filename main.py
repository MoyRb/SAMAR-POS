# main.py
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from utils.db_session import test_connection
from ui.login_window import LoginWindow

APP_TITLE = "SAMAR-POS — Punto de Venta y Operación"

def main():
    # --- Inicializa la aplicación Qt ---
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)

    # --- Carga el tema oscuro global ---
    try:
        with open("ui/theme_dark.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("[WARN] No se encontró el archivo de estilos 'theme_dark.qss'.")

    # --- Verifica conexión a la base de datos ---
    try:
        test_connection()
        print("✅ Conexión a la base de datos establecida.")
    except Exception as e:
        QMessageBox.critical(
            None,
            "Error de conexión",
            f"No se pudo conectar a la base de datos.\n\nDetalle:\n{e}",
        )
        sys.exit(1)

    # --- Muestra la ventana de login ---
    login_window = LoginWindow()
    login_window.show()

    # --- Ejecuta la app ---
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
