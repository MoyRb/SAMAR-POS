# ui/window_manager.py
"""Administrador de ventanas y atajos globales.

Se encarga de:
- Mantener referencias a las ventanas principales.
- Crear ventanas bajo demanda reutilizando la sesión del usuario.
- Instalar un filtro de eventos para que los atajos F1/F2 funcionen en
  cualquier pantalla.
"""

from functools import partial
from typing import Optional

from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QApplication, QWidget


MAIN_WINDOW: Optional[QWidget] = None
PEDIDOS_WINDOW: Optional[QWidget] = None
KDS_WINDOW: Optional[QWidget] = None
CURRENT_USER = None
_SHORTCUT_FILTER: Optional[QObject] = None


def set_user(usuario: dict):
    """Guarda la sesión activa para reutilizarla al crear ventanas."""

    global CURRENT_USER
    CURRENT_USER = usuario


def _clear_reference(name: str):
    globals()[name] = None


def _attach_lifecycle(window: QWidget, attr_name: str):
    window.destroyed.connect(partial(_clear_reference, attr_name))


def _focus_window(target: QWidget):
    """Muestra la ventana destino y oculta las demás conocidas."""

    for win in [MAIN_WINDOW, PEDIDOS_WINDOW, KDS_WINDOW]:
        if win is None or win is target:
            continue
        win.hide()

    target.show()
    target.raise_()
    target.activateWindow()


def get_or_create_main_window():
    global MAIN_WINDOW
    if MAIN_WINDOW is None:
        from ui.main_window import MainWindow

        MAIN_WINDOW = MainWindow(CURRENT_USER)
        _attach_lifecycle(MAIN_WINDOW, "MAIN_WINDOW")
    return MAIN_WINDOW


def get_or_create_pedidos_window():
    global PEDIDOS_WINDOW
    if PEDIDOS_WINDOW is None:
        from ui.pedidos_window import PedidosWindow

        PEDIDOS_WINDOW = PedidosWindow(CURRENT_USER)
        _attach_lifecycle(PEDIDOS_WINDOW, "PEDIDOS_WINDOW")
    return PEDIDOS_WINDOW


def get_or_create_kds_window():
    global KDS_WINDOW
    if KDS_WINDOW is None:
        from ui.kds_window import KDSWindow

        KDS_WINDOW = KDSWindow(CURRENT_USER)
        _attach_lifecycle(KDS_WINDOW, "KDS_WINDOW")
    return KDS_WINDOW


def show_main_window():
    _focus_window(get_or_create_main_window())


def show_pedidos_window():
    _focus_window(get_or_create_pedidos_window())


def show_kds_window():
    _focus_window(get_or_create_kds_window())


class _ShortcutFilter(QObject):
    """Filtro de eventos global para atajos de teclado."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.modifiers() == Qt.NoModifier:
            if event.key() == Qt.Key_F1:
                show_pedidos_window()
                return True
            if event.key() == Qt.Key_F2:
                show_kds_window()
                return True
        return super().eventFilter(obj, event)


def install_global_shortcuts(app: QApplication):
    """Instala el filtro de atajos solo una vez."""

    global _SHORTCUT_FILTER
    if _SHORTCUT_FILTER is not None:
        return

    _SHORTCUT_FILTER = _ShortcutFilter()
    app.installEventFilter(_SHORTCUT_FILTER)

