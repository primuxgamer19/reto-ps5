# ui_notificaciones.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty
import math

# ---------- TimePickerPopup: analog clock style ----------
class TimePickerPopup(Popup):
    """
    Popup that allows selecting hour (0-23) and minutes (0-59) using a circular dial.
    Mode flow: 'hour' -> 'minute'. Shows live preview of selected time.
    """
    selected_time = StringProperty("00:00")

    def __init__(self, initial_time="", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.7)
        self.title = "Selector de hora"
        self.auto_dismiss = False

        # parse initial_time if provided
        ih, im = "00", "00"
        if initial_time and ":" in initial_time:
            parts = initial_time.split(":")
            if len(parts) == 2:
                ih = parts[0].zfill(2)
                im = parts[1].zfill(2)

        self.hour = int(ih)
        self.minute = int(im)
        self.mode = 'hour'  # 'hour' or 'minute'

        root = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(12))

        # Live label
        self.preview_lbl = Label(text=f"Seleccionando: {self.hour:02d}:{self.minute:02d}", size_hint_y=None, height=dp(28))
        root.add_widget(self.preview_lbl)

        # Clock widget
        self.clock = _AnalogClockDial(self.hour, self.minute)
        self.clock.size_hint = (1, 1)
        root.add_widget(self.clock)

        # Mode hint
        self.mode_lbl = Label(text="Toca y arrastra para elegir la HORA (0-23). Luego pulsa Siguiente.", size_hint_y=None, height=dp(24), font_size='12sp', color=(0.8,0.8,0.8,1))
        root.add_widget(self.mode_lbl)

        # Buttons
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.btn_next = Button(text="Siguiente", background_color=(0.15, 0.6, 0.95, 1), background_normal='')
        self.btn_ok = Button(text="OK", background_color=(0.2, 0.7, 0.3, 1), background_normal='')
        self.btn_cancel = Button(text="CANCELAR", background_color=(0.8, 0.2, 0.2, 1), background_normal='')

        btns.add_widget(self.btn_cancel)
        btns.add_widget(self.btn_next)
        btns.add_widget(self.btn_ok)
        root.add_widget(btns)

        self.content = root

        # Bindings
        self.clock.bind(on_value_change=self._on_clock_change)
        self.btn_next.bind(on_press=self._on_next)
        self.btn_ok.bind(on_press=self._on_ok)
        self.btn_cancel.bind(on_press=lambda *a: self.dismiss())

        # initialize preview
        self._update_preview()

    def _on_clock_change(self, instance, value):
        # value is (hour, minute) depending on mode
        if self.mode == 'hour':
            self.hour = int(value)
        else:
            self.minute = int(value)
        self._update_preview()

    def _update_preview(self):
        self.preview_lbl.text = f"Seleccionando: {self.hour:02d}:{self.minute:02d}"

    def _on_next(self, *a):
        if self.mode == 'hour':
            # switch to minute selection
            self.mode = 'minute'
            self.mode_lbl.text = "Ahora selecciona los MINUTOS (0-59). Pulsa OK cuando termines."
            self.clock.set_mode('minute', self.hour, self.minute)
            self.btn_next.text = "Volver"
        else:
            # go back to hour
            self.mode = 'hour'
            self.mode_lbl.text = "Toca y arrastra para elegir la HORA (0-23). Luego pulsa Siguiente."
            self.clock.set_mode('hour', self.hour, self.minute)
            self.btn_next.text = "Siguiente"
        self._update_preview()

    def _on_ok(self, *a):
        self.selected_time = f"{self.hour:02d}:{self.minute:02d}"
        self.dismiss()


class _AnalogClockDial(Widget):
    """
    Internal widget that draws a circular dial and handles touch to set hour/minute.
    Emits on_value_change with the current selected value (hour or minute).
    """
    def __init__(self, init_hour=0, init_minute=0, **kwargs):
        super().__init__(**kwargs)
        self.mode = 'hour'  # 'hour' or 'minute'
        self.hour = init_hour % 24
        self.minute = init_minute % 60
        self.knob_angle = 0
        self.bind(size=self._redraw, pos=self._redraw)
        self._value_listeners = []
        # initial angle from hour
        self._compute_knob_from_values()

    def on_value_change(self, *args):
        # placeholder for event binding
        pass

    def set_mode(self, mode, hour=None, minute=None):
        self.mode = mode
        if hour is not None:
            self.hour = hour % 24
        if minute is not None:
            self.minute = minute % 60
        self._compute_knob_from_values()
        self._redraw()

    def _compute_knob_from_values(self):
        if self.mode == 'hour':
            # map 0..23 to angle (0 at top, clockwise)
            self.knob_angle = (self.hour / 24.0) * 360.0
        else:
            self.knob_angle = (self.minute / 60.0) * 360.0

    def _redraw(self, *a):
        self.canvas.clear()
        cx, cy = self.center
        r = min(self.width, self.height) * 0.4
        with self.canvas:
            # background circle
            Color(0.12, 0.12, 0.12, 1)
            Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))
            # ticks
            if self.mode == 'hour':
                steps = 24
                tick_color = (0.9, 0.6, 0.1, 1)
            else:
                steps = 60
                tick_color = (0.6, 0.8, 0.95, 1)
            Color(*tick_color)
            for i in range(steps):
                ang = math.radians(i * (360.0 / steps) - 90)
                x1 = cx + (r * 0.85) * math.cos(ang)
                y1 = cy + (r * 0.85) * math.sin(ang)
                x2 = cx + (r * 0.95) * math.cos(ang)
                y2 = cy + (r * 0.95) * math.sin(ang)
                Line(points=[x1, y1, x2, y2], width=1.2)
            # knob
            ang_knob = math.radians(self.knob_angle - 90)
            kx = cx + (r * 0.6) * math.cos(ang_knob)
            ky = cy + (r * 0.6) * math.sin(ang_knob)
            Color(0.95, 0.3, 0.3, 1)
            Ellipse(pos=(kx - dp(10), ky - dp(10)), size=(dp(20), dp(20)))
            # center
            Color(0.95, 0.95, 0.95, 1)
            Ellipse(pos=(cx - dp(6), cy - dp(6)), size=(dp(12), dp(12)))

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._update_from_touch(touch.pos)
        return True

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._update_from_touch(touch.pos)
        return True

    def _update_from_touch(self, pos):
        cx, cy = self.center
        dx = pos[0] - cx
        dy = pos[1] - cy
        angle = math.degrees(math.atan2(dy, dx)) + 90
        if angle < 0:
            angle += 360
        self.knob_angle = angle
        # convert angle to value
        if self.mode == 'hour':
            val = int(round((angle / 360.0) * 24)) % 24
            self.hour = val
            self._emit_value_change(self.hour)
        else:
            val = int(round((angle / 360.0) * 60)) % 60
            self.minute = val
            self._emit_value_change(self.minute)
        self._redraw()

    def _emit_value_change(self, v):
        # call bound listeners
        for cb in getattr(self, "_listeners", []):
            try:
                cb(self, v)
            except:
                pass
        # also update parent via property if exists
        try:
            self.dispatch('on_value_change', v)
        except:
            pass

    # simple binding API
    def bind(self, **kwargs):
        # support on_value_change binding
        if 'on_value_change' in kwargs:
            self._listeners = kwargs['on_value_change'] if isinstance(kwargs['on_value_change'], list) else [kwargs['on_value_change']]
            del kwargs['on_value_change']
        return super().bind(**kwargs)


# ---------- Main NotificacionesScreen (UI improved) ----------
class NotificacionesScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()

        # Main container
        self.main = BoxLayout(orientation='vertical', padding=[dp(12), dp(12), dp(12), dp(12)], spacing=dp(12))

        # Header
        header = Label(text="--- CONFIGURAR NOTIFICACIONES ---", size_hint_y=None, height=dp(44), bold=True)
        self.main.add_widget(header)

        # Configuration card (only enabled switch)
        cfg_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(88),
                             padding=[dp(10), dp(8), dp(10), dp(8)], spacing=dp(8))
        cfg_box = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(40))
        cfg_box.add_widget(Label(text="Notificaciones activas:", size_hint_x=None, width=dp(180)))
        self.switch_enabled = Switch(active=False, size_hint_x=None, width=dp(60))
        cfg_box.add_widget(self.switch_enabled)
        cfg_card.add_widget(cfg_box)

        help_lbl = Label(text="Activa para recibir recordatorios; crea varias entradas.", font_size='12sp',
                         size_hint_y=None, height=dp(20), color=(0.8, 0.8, 0.8, 1))
        cfg_card.add_widget(help_lbl)

        self.main.add_widget(cfg_card)

        # Entries header
        self.main.add_widget(Label(text="Entradas programadas (HH:MM - Mensaje):", size_hint_y=None, height=dp(28)))

        # Scrollable list of entries
        self.scroll = ScrollView(size_hint=(1, 1))
        self.entries_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8),
                                     padding=[0, dp(6), 0, dp(6)])
        self.entries_box.bind(minimum_height=self.entries_box.setter('height'))
        self.scroll.add_widget(self.entries_box)
        self.main.add_widget(self.scroll)

        # Controls area (flat, compact buttons)
        controls = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        btn_add = Button(text="AÑADIR ENTRADA", size_hint=(0.45, 1), background_normal='', background_color=(0.06, 0.5, 0.9, 1))
        btn_add.bind(on_press=self._open_add_entry)
        btn_save = Button(text="GUARDAR", size_hint=(0.27, 1), background_normal='', background_color=(0.15, 0.7, 0.3, 1))
        btn_save.bind(on_press=self._save_and_back)
        btn_back = Button(text="VOLVER", size_hint=(0.28, 1), background_normal='', background_color=(0.45, 0.45, 0.45, 1))
        btn_back.bind(on_press=self._volver)
        controls.add_widget(btn_add)
        controls.add_widget(btn_save)
        controls.add_widget(btn_back)
        self.main.add_widget(controls)

        # Empty state label (hidden when entries exist)
        self.empty_label = Label(text="No hay entradas programadas. Pulsa 'AÑADIR ENTRADA' para crear una.",
                                 size_hint_y=None, height=dp(40), color=(0.7, 0.7, 0.7, 1))
        self.main.add_widget(self.empty_label)

        self.add_widget(self.main)

    def on_enter(self):
        app = App.get_running_app()
        cfg = app.datos.get_config()
        self.switch_enabled.active = cfg.get("enabled", False)
        self._refresh_entries()
        try:
            self.scroll.scroll_y = 1
        except:
            pass

    def _refresh_entries(self):
        self.entries_box.clear_widgets()
        app = App.get_running_app()
        entries = app.datos.get_entries()
        if not entries:
            self.empty_label.opacity = 1
        else:
            self.empty_label.opacity = 0

        for e in entries:
            row = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(8), padding=[dp(8), dp(6), dp(8), dp(6)])
            lbl = Label(text=f"[b]{e.get('hora')}[/b]  -  {e.get('mensaje')}", markup=True,
                        halign='left', valign='middle')
            lbl.text_size = (Window.width * 0.62, None)
            btns = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(150), spacing=dp(6))
            btn_edit = Button(text="Editar", size_hint_y=None, height=dp(28), background_normal='', background_color=(0.95, 0.8, 0.2, 1))
            btn_remove = Button(text="Eliminar", size_hint_y=None, height=dp(28), background_normal='', background_color=(0.9, 0.2, 0.2, 1))
            hora_val = e.get('hora')
            btn_edit.bind(on_press=lambda inst, hora=hora_val: self._open_edit_entry(hora))
            btn_remove.bind(on_press=lambda inst, hora=hora_val: self._confirm_remove_entry(hora))
            btns.add_widget(btn_edit)
            btns.add_widget(btn_remove)

            row.add_widget(lbl)
            row.add_widget(btns)
            self.entries_box.add_widget(row)

    # ---------- Entry creation / edit with analog time picker ----------
    def _open_add_entry(self, instance):
        self._open_entry_popup()

    def _open_edit_entry(self, hora):
        app = App.get_running_app()
        entry = None
        for e in app.datos.get_entries():
            if e.get("hora") == hora:
                entry = e
                break
        if entry:
            self._open_entry_popup(initial_hora=entry.get("hora"), initial_msg=entry.get("mensaje"))

    def _open_entry_popup(self, initial_hora="", initial_msg=""):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(12), dp(12), dp(12), dp(12)])

        # Hora display (button opens analog picker)
        hora_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(44), spacing=dp(8))
        hora_label = Label(text="Hora (HH:MM):", size_hint_x=None, width=dp(120), valign='middle')
        hora_btn = Button(text=initial_hora or "Seleccionar hora", size_hint=(1, None), height=dp(44), background_normal='', background_color=(0.12,0.12,0.12,1))
        hora_box.add_widget(hora_label)
        hora_box.add_widget(hora_btn)

        msg_input = TextInput(text=initial_msg, multiline=False, hint_text="Mensaje", size_hint_y=None, height=dp(80))

        btn_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        btn_ok = Button(text="OK", background_normal='', background_color=(0.2, 0.7, 0.3, 1))
        btn_cancel = Button(text="CANCELAR", background_normal='', background_color=(0.8, 0.2, 0.2, 1))
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cancel)

        content.add_widget(hora_box)
        content.add_widget(Label(text="Mensaje:", size_hint_y=None, height=dp(20)))
        content.add_widget(msg_input)
        content.add_widget(btn_box)

        popup = Popup(title="Añadir / Editar entrada", content=content, size_hint=(0.9, 0.6), auto_dismiss=False)

        def _on_ok(inst):
            hora = (hora_btn.text or "").strip()
            msg = (msg_input.text or "").strip()
            if not hora or hora == "Seleccionar hora":
                # feedback: simple visual shake could be added; keep minimal
                return
            ok = App.get_running_app().datos.add_entry(hora, msg)
            if ok:
                App.get_running_app().datos.save_data()
                self._refresh_entries()
            popup.dismiss()

        def _on_cancel(inst):
            popup.dismiss()

        btn_ok.bind(on_press=_on_ok)
        btn_cancel.bind(on_press=_on_cancel)

        def _open_picker(inst):
            tp = TimePickerPopup(initial_time=hora_btn.text if hora_btn.text and hora_btn.text != "Seleccionar hora" else "")
            def _on_dismiss(*a):
                if tp.selected_time:
                    hora_btn.text = tp.selected_time
            tp.bind(on_dismiss=_on_dismiss)
            tp.open()

        hora_btn.bind(on_press=_open_picker)
        popup.open()

    # ---------- Remove with confirmation ----------
    def _confirm_remove_entry(self, hora):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(12))
        content.add_widget(Label(text=f"¿Eliminar la entrada {hora}?", size_hint_y=None, height=dp(40)))
        btns = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        btn_yes = Button(text="Eliminar", background_normal='', background_color=(0.9, 0.2, 0.2, 1))
        btn_no = Button(text="Cancelar", background_normal='', background_color=(0.6, 0.6, 0.6, 1))
        btns.add_widget(btn_yes)
        btns.add_widget(btn_no)
        content.add_widget(btns)
        popup = Popup(title="Confirmar eliminación", content=content, size_hint=(0.8, 0.35))

        def _do_delete(inst):
            App.get_running_app().datos.remove_entry(hora)
            App.get_running_app().datos.save_data()
            self._refresh_entries()
            popup.dismiss()

        def _cancel(inst):
            popup.dismiss()

        btn_yes.bind(on_press=_do_delete)
        btn_no.bind(on_press=_cancel)
        popup.open()

    def _remove_entry(self, hora):
        App.get_running_app().datos.remove_entry(hora)
        App.get_running_app().datos.save_data()
        self._refresh_entries()

    # ---------- Save and navigation ----------
    def _save_and_back(self, instance):
        app = App.get_running_app()
        enabled = bool(self.switch_enabled.active)
        app.datos.set_notificaciones_enabled(enabled)
        app.datos.save_data()
        try:
            self.manager.current = 'presupuesto'
        except:
            pass

    def _volver(self, instance):
        try:
            self.manager.current = 'presupuesto'
        except:
            pass