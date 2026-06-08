# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import os
import datetime

from audio.audio import AudioManager
from logic.motor_datos import MotorDatos

from ui.ui_calculadora import CalculadoraScreen
from ui.ui_presupuesto import PresupuestoScreen
from ui.ui_pecado import PecadoScreen, HistorialPecadosScreen
from ui.ui_regalo import RegaloScreen, HistorialRegalosScreen
from ui.ui_gastos_fijos import GastosFijosScreen
from ui.ui_estadistica import EstadisticaScreen
from ui.ui_notificaciones import NotificacionesScreen

try:
    from plyer import notification as plyer_notification
except Exception:
    plyer_notification = None

class RetoPS5App(App):
    def build(self):
        Window.softinput_mode = "pan"
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        try:
            self.audio = AudioManager()
        except Exception:
            class _AudioFallback:
                def __init__(self):
                    self.music_13 = None
                    self.is_playing_13 = False
                def load_13_music(self, *a, **k): pass
                def stop_bg(self): pass
                def play_fx(self, *a, **k): pass
            self.audio = _AudioFallback()

        self.datos = MotorDatos() 
        
        sm = ScreenManager()
        sm.add_widget(CalculadoraScreen(name='calculadora'))
        sm.add_widget(PresupuestoScreen(name='presupuesto'))
        sm.add_widget(PecadoScreen(name='pecado'))
        sm.add_widget(HistorialPecadosScreen(name='historial_pecados'))
        sm.add_widget(RegaloScreen(name='regalo'))
        sm.add_widget(HistorialRegalosScreen(name='historial_regalos'))
        sm.add_widget(GastosFijosScreen(name='gastos_fijos'))
        sm.add_widget(EstadisticaScreen(name='estadistica'))
        sm.add_widget(NotificacionesScreen(name='notificaciones'))

        # Scheduler para notificaciones programadas (cada 30s)
        Clock.schedule_interval(self._check_scheduled_notifications, 30)

        return sm

    def on_pause(self):
        return True

    def on_resume(self):
        self.check_daily_events()
        return True

    def on_start(self):
        self.check_daily_events()
        try:
            if not getattr(self.audio, 'music_13', None):
                self.audio.load_13_music('letania13.mp3')
        except Exception:
            pass

    def check_daily_events(self):
        mostrar_popup = self.datos.procesar_eventos_diarios()
        if mostrar_popup:
            self.show_notif_popup()

    def show_notif_popup(self, title='¡ATENCIÓN CARLOS!', message=None):
        monto = getattr(self.datos, 'ahorrado_guardado', "0")
        if message is None:
            message = f"¿Ya vas a actualizar tu ahorro?\nO te vas a quedar en ${monto} para siempre..."
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message, halign="center"))
        btn = Button(text="Ya voy, no me presiones", size_hint_y=None, height=50)
        popup = Popup(title=title, content=content, size_hint=(0.9, 0.45))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
        try:
            self.audio.play_fx('alerta.wav')
        except:
            pass

    def trigger_13_logic(self):
        if getattr(self.audio, 'is_playing_13', False): return
        self.audio.is_playing_13 = True
        try: self.audio.stop_bg()
        except: pass
        try: self.audio.play_fx('pum.mp3')
        except: pass
        Clock.schedule_once(self.play_letania, 0.8)

    def play_letania(self, dt):
        try:
            if not getattr(self.audio, 'music_13', None):
                self.audio.load_13_music('letania13.mp3')
            if getattr(self.audio, 'music_13', None):
                try: self.audio.music_13.unbind(on_stop=self._reset_13_flag)
                except: pass
                try: self.audio.music_13.bind(on_stop=self._reset_13_flag)
                except: pass
                try: self.audio.music_13.play()
                except: self._reset_13_flag()
            else:
                self._reset_13_flag()
        except Exception:
            self._reset_13_flag()

    def _reset_13_flag(self, *args):
        self.audio.is_playing_13 = False

    def _is_compiled_android(self):
        return 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ

    def _check_scheduled_notifications(self, dt):
        """
        Comprueba las entradas programadas con tolerancia temporal.
        - Ventana de tolerancia: 1 minuto antes y 1 minuto después.
        - Actualiza last_sent cuando se envía.
        """
        try:
            cfg = self.datos.get_config()
            if not cfg.get("enabled", False):
                return

            ahora_dt = datetime.datetime.now()
            ahora_hm = ahora_dt.strftime("%H:%M")
            hoy_str = ahora_dt.strftime("%Y-%m-%d")

            for e in self.datos.get_entries():
                hora = e.get("hora")
                if not hora:
                    continue
                try:
                    hh, mm = map(int, hora.split(":"))
                except:
                    continue
                target_dt = ahora_dt.replace(hour=hh, minute=mm, second=0, microsecond=0)
                delta = abs((ahora_dt - target_dt).total_seconds())
                # tolerancia 60 segundos
                if delta <= 60:
                    titulo = "Recordatorio"
                    mensaje = e.get("mensaje") or "Tienes un recordatorio programado."
                    if self._is_compiled_android() and plyer_notification is not None:
                        try:
                            plyer_notification.notify(title=titulo, message=mensaje)
                        except Exception:
                            self.show_notif_popup(title=titulo, message=mensaje)
                    else:
                        self.show_notif_popup(title=titulo, message=mensaje)
                    # actualizar last_sent
                    self.datos.set_last_sent_date(hoy_str)
                    self.datos.save_data()
                    break
        except Exception:
            # No queremos que el scheduler rompa la app
            pass

    def on_stop(self):
        try:
            self.datos.save_data()
        except:
            pass

if __name__ == '__main__':
    RetoPS5App().run()