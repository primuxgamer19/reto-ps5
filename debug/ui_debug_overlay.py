# debug/ui_debug_overlay.py
"""
Overlay/menú de debugging para la app (Kivy).
Contiene un botón visible que despliega un panel con acciones de debug.

Todas las operaciones afectan archivos dentro de debug/resources/data/ para
mantener el proyecto ordenado.
"""
import os
import json
import time
import datetime
from typing import Optional

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

try:
    from .notificaciones_debug import notif_debug
except Exception:
    notif_debug = None


def dump_state_to_file(app_ref, base_debug_dir: str = 'debug/resources/data') -> str:
    """Vuelca el __dict__ del app_ref a un archivo JSON para reproducir bugs.
    Devuelve la ruta del archivo generado.
    """
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs(base_debug_dir, exist_ok=True)
    filename = f'state_dump_{ts}.json'
    path = os.path.join(base_debug_dir, filename)
    try:
        # Intentar serializar de forma segura: omitir callables y objetos non-serializable
        state = {}
        for k, v in getattr(app_ref, '__dict__', {}).items():
            try:
                json.dumps(v)
                state[k] = v
            except Exception:
                try:
                    # intentar convertir objetos básicos a repr
                    state[k] = repr(v)
                except Exception:
                    state[k] = '<unserializable>'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return path
    except Exception as e:
        # fallback: escribir una mínima info
        fallback = os.path.join(base_debug_dir, f'state_dump_{ts}.txt')
        with open(fallback, 'w', encoding='utf-8') as f:
            f.write(f'Error dumping state: {e}')
        return fallback


class DebugMenu(FloatLayout):
    """Overlay simple con un botón para abrir/ocultar el panel de debug."""
    def __init__(self, app_ref: Optional[object] = None, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        # Botón flotante de acceso rápido
        self.debug_btn = Button(text='DEBUG', size_hint=(None, None), size=(80, 40), pos_hint={'right': 0.98, 'top': 0.98}, background_color=(0.9,0.1,0.1,0.9))
        self.debug_btn.bind(on_press=self._toggle_panel)
        self.add_widget(self.debug_btn)

        self.panel = None

    def _toggle_panel(self, *args):
        if self.panel and self.panel.parent:
            self.panel.dismiss()
            self.panel = None
        else:
            self._open_panel()

    def _open_panel(self):
        content = BoxLayout(orientation='vertical', spacing=8, padding=8)
        # Botones de acciones
        btn_logs = Button(text='Ver logs recientes', size_hint_y=None, height=44)
        btn_logs.bind(on_press=self._show_logs)
        content.add_widget(btn_logs)

        btn_clear = Button(text='Limpiar logs', size_hint_y=None, height=44)
        btn_clear.bind(on_press=self._clear_logs)
        content.add_widget(btn_clear)

        btn_dump = Button(text='Dump estado', size_hint_y=None, height=44)
        btn_dump.bind(on_press=self._dump_state)
        content.add_widget(btn_dump)

        btn_export = Button(text='Exportar respaldo de ejemplo', size_hint_y=None, height=44)
        btn_export.bind(on_press=self._export_example)
        content.add_widget(btn_export)

        btn_close = Button(text='Cerrar', size_hint_y=None, height=44)
        btn_close.bind(on_press=lambda inst: self._close_panel())
        content.add_widget(btn_close)

        self.panel = Popup(title='Menu Debug', content=content, size_hint=(0.9, 0.6))
        self.panel.open()

    def _close_panel(self):
        if self.panel:
            self.panel.dismiss()
            self.panel = None

    def _show_logs(self, instance):
        try:
            logs = notif_debug.get_recent_logs(200) if notif_debug else ['No hay debug disponible.']
        except Exception:
            logs = ['Error leyendo logs.']
        text = '\n'.join([l.rstrip() for l in logs])
        self._show_text_popup('Logs recientes', text)

    def _clear_logs(self, instance):
        try:
            if notif_debug:
                notif_debug.clear_log()
            self._show_simple_popup('Logs', 'Logs limpiados.')
        except Exception as e:
            self._show_simple_popup('Error', f'No se pudo limpiar logs: {e}')

    def _dump_state(self, instance):
        if not self.app_ref:
            self._show_simple_popup('Dump estado', 'Referencia a app no disponible.')
            return
        try:
            path = dump_state_to_file(self.app_ref)
            self._show_simple_popup('Dump estado', f'Estado volcado en:\n{path}')
            if notif_debug:
                notif_debug.log_info('Estado volcado desde DebugMenu', {'path': path})
        except Exception as e:
            self._show_simple_popup('Error', f'No se pudo volcar estado: {e}')

    def _export_example(self, instance):
        if not self.app_ref:
            self._show_simple_popup('Export', 'Referencia a app no disponible.')
            return
        try:
            nombre = f'DebugExport_{time.strftime("%Y%m%d_%H%M%S")}'
            success, msg = self.app_ref.datos.exportar_json(nombre)
            self._show_simple_popup('Export', msg)
            if notif_debug:
                notif_debug.log_info('Export desde DebugMenu', {'success': success, 'msg': msg})
        except Exception as e:
            self._show_simple_popup('Error', f'No se pudo exportar: {e}')

    def _show_text_popup(self, title, text):
        scroll = ScrollView()
        label = Label(text=text or '', size_hint_y=None)
        # Ajustar tamaño del label en función del texto
        label.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1]))
        scroll.add_widget(label)
        popup = Popup(title=title, content=scroll, size_hint=(0.9, 0.8))
        popup.open()

    def _show_simple_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()


if __name__ == '__main__':
    print('Este módulo define DebugMenu y utilidades de dump_state. Se importa desde debug/main_debug.py')
