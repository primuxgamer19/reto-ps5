import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ['DEBUGGER_MODE'] = '1'

from main import RetoPS5App
from debug.debug_overlay import DebugOverlay
from debug.ui_debug_overlay import DebugMenu
from debug.init_debug import init_debug
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

app = RetoPS5App()
app.debug_mode = True

_original_build = app.build

def _build_and_inject():
    root = _original_build()
    # crear overlay y asegurar que ocupa todo el espacio
    app.debugger = DebugOverlay(app_ref=app)
    app.debugger.size_hint = (1, 1)
    # Intentar añadir overlay al final para que quede encima
    try:
        root.add_widget(app.debugger)
    except Exception:
        container = FloatLayout()
        try:
            root.size_hint = (1, 1)
        except Exception:
            pass
        container.add_widget(root)
        container.add_widget(app.debugger)
        root = container

    # Inicializar sistema de debug (excepthook, stdout/stderr)
    try:
        init_debug(app_ref=app)
    except Exception:
        pass

    # Añadir menu debug modular (botón que abre panel)
    try:
        app.debug_menu = DebugMenu(app_ref=app)
        try:
            root.add_widget(app.debug_menu)
        except Exception:
            # raíz podría ser un widget no permitiendo add_widget en cada caso: intentar contener
            from kivy.uix.floatlayout import FloatLayout
            container = FloatLayout()
            try:
                root.size_hint = (1, 1)
            except Exception:
                pass
            container.add_widget(root)
            container.add_widget(app.debugger)
            container.add_widget(app.debug_menu)
            root = container
    except Exception:
        pass

    return root

app.build = _build_and_inject

if __name__ == '__main__':
    app.run()
