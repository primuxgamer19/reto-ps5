from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

def _time_str():
    import time
    return time.strftime("%H:%M:%S")

class DebugOverlay(FloatLayout):
    def __init__(self, app_ref=None, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.size_hint = (1, 1)

        # Consola preparada pero NO añadida al árbol hasta que se muestre
        self.console_box = BoxLayout(orientation='vertical',
                                     size_hint=(1, 0.40),
                                     pos_hint={'x': 0, 'y': 0})
        self.console_scroll = ScrollView(size_hint=(1, 1))
        self.log_text = Label(text="[DEBUG CONSOLE]\n", markup=True,
                              size_hint_y=None)
        self.log_text.bind(texture_size=self._update_log_height)
        self.console_scroll.add_widget(self.log_text)
        self.console_box.add_widget(self.console_scroll)

        # Botones de control dentro de la consola
        btns = BoxLayout(size_hint=(1, None), height=40)
        clear_btn = Button(text="Clear", size_hint=(0.18, 1))
        clear_btn.bind(on_release=lambda *_: self._clear_logs())
        btns.add_widget(clear_btn)
        btns.add_widget(Label())  # espacio flexible
        self.console_box.add_widget(btns)

        # Toggle pequeño en esquina superior izquierda (siempre activo)
        self.toggle_btn = Button(text="DBG", size_hint=(0.12, 0.08),
                                 pos_hint={'x': 0, 'top': 1})
        self.toggle_btn.bind(on_release=self._toggle_console)
        # FPS label en esquina superior derecha
        self.fps_label = Label(text="FPS: 0", size_hint=(0.18, 0.08),
                               pos_hint={'right': 1, 'top': 1})

        # Añadir primero la consola NO (se añadirá dinámicamente),
        # luego añadir toggle y fps para que queden siempre encima.
        self.add_widget(self.toggle_btn)
        self.add_widget(self.fps_label)

        self.console_visible = False

        # Frame counter para FPS
        self._frames = 0
        self._last = Clock.get_time()
        Clock.schedule_interval(self._frame_tick, 0)

    def _update_log_height(self, instance, value):
        # ajustar altura del label para que ScrollView funcione
        self.log_text.height = max(self.log_text.texture_size[1], self.console_scroll.height)

    def _frame_tick(self, dt):
        self._frames += 1
        now = Clock.get_time()
        if now - self._last >= 1.0:
            fps = self._frames / (now - self._last)
            self.fps_label.text = f"FPS: {int(fps)}"
            self._frames = 0
            self._last = now

    def _toggle_console(self, *args):
        # Mostrar: añadir console_box debajo de toggle/fps (index 0)
        if not self.console_visible:
            # preparar fondo opaco dentro de la propia console_box
            with self.console_box.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0, 0, 0, 0.95)
                self._console_bg = Rectangle(pos=self.console_box.pos, size=self.console_box.size)
            # bind para mantener el rectángulo actualizado
            self.console_box.bind(pos=self._update_console_bg, size=self._update_console_bg)
            # añadir la consola al overlay en la posición 0 (debajo de toggle/fps)
            try:
                self.add_widget(self.console_box, index=0)
            except TypeError:
                # fallback si la versión de Kivy no soporta index
                self.add_widget(self.console_box)
            self.console_visible = True
        else:
            # Ocultar: quitar bindings y eliminar widget para que no bloquee toques
            try:
                self.console_box.unbind(pos=self._update_console_bg, size=self._update_console_bg)
            except Exception:
                pass
            try:
                # eliminar el rectángulo de fondo si existe
                if hasattr(self, "_console_bg"):
                    # borrar instrucciones asociadas al canvas.before de console_box
                    self.console_box.canvas.before.clear()
                    del self._console_bg
            except Exception:
                pass
            try:
                self.remove_widget(self.console_box)
            except Exception:
                pass
            self.console_visible = False

    def _update_console_bg(self, *a):
        try:
            self._console_bg.pos = self.console_box.pos
            self._console_bg.size = self.console_box.size
        except Exception:
            pass

    def add_log(self, message):
        ts = _time_str()
        self.log_text.text += f"\n[{ts}] {message}"
        # forzar scroll al final
        self.console_scroll.scroll_y = 0

    def _clear_logs(self):
        self.log_text.text = "[DEBUG CONSOLE]\n"