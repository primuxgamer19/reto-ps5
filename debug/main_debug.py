import os
import sys

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ['DEBUGGER_MODE'] = '1'

from main import RetoPS5App
from debug.debug_overlay import DebugOverlay
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
        return root
    except Exception:
        container = FloatLayout()
        try:
            root.size_hint = (1, 1)
        except Exception:
            pass
        container.add_widget(root)
        container.add_widget(app.debugger)
        return container

app.build = _build_and_inject

if __name__ == '__main__':
    app.run()
