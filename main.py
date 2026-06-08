# main.py (versión mejorada)
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
from logic.notificaciones_debug import notif_debug

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
        
        # Log inicial
        notif_debug.log_info("App iniciada")
        notif_debug.log_info(f"Compilada en Android: {self._is_compiled_android()}")
        
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
        notif_debug.log_info("App reanudada (on_resume)")
        self.check_daily_events()
        return True

    def on_start(self):
        notif_debug.log_info("App iniciada (on_start)")
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
        """Muestra un popup de notificación (solo mientras app está abierta)"""
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
        """Detecta si la app está compilada para Android o se ejecuta en Pydroid/desarrollo"""
        return 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ

    def _check_scheduled_notifications(self, dt):
        """
        Comprueba las entradas programadas cada 30 segundos.
        
        Lógica:
        - Si es Android compilado: usa notificaciones nativas (plyer)
        - Si es Pydroid/desarrollo: usa popups dentro de la app
        - Tolerance window: 60 segundos antes/después de la hora
        - Solo envía una notificación por día
        """
        try:
            cfg = self.datos.get_config()
            if not cfg.get("enabled", False):
                return

            ahora_dt = datetime.datetime.now()
            hoy_str = ahora_dt.strftime("%Y-%m-%d")
            
            # Si ya se envió una notificación hoy, no enviar más
            if cfg.get("last_sent") == hoy_str:
                return

            # Obtener la próxima notificación a enviar
            proxima_entry, delta = self.datos.get_next_notification_entry(ahora_dt)
            
            if proxima_entry is None:
                return
            
            # Determinar tipo de notificación según la configuración de la entrada
            tipo_notif = proxima_entry.get("tipo", "popup")
            titulo = "Recordatorio"
            mensaje = proxima_entry.get("mensaje") or "Tienes un recordatorio programado."
            
            # Loguear el evento
            notif_debug.log_info(f"Enviando notificación [{tipo_notif}]", {
                "hora": proxima_entry.get("hora"),
                "mensaje": mensaje,
                "delta_segundos": delta,
                "ambiente": "Android compilado" if self._is_compiled_android() else "Pydroid/Desarrollo"
            })
            
            # NOTIFICACIÓN TIPO ANDROID (nativa)
            if tipo_notif == "android" and self._is_compiled_android() and plyer_notification is not None:
                try:
                    plyer_notification.notify(title=titulo, message=mensaje)
                    notif_debug.log_info("✓ Notificación Android enviada correctamente")
                except Exception as e:
                    notif_debug.log_error(f"Error enviando notificación Android: {str(e)}")
                    # Fallback a popup
                    self.show_notif_popup(title=titulo, message=mensaje)
            
            # NOTIFICACIÓN TIPO POPUP (solo app abierta)
            else:
                self.show_notif_popup(title=titulo, message=mensaje)
                notif_debug.log_info("✓ Notificación POPUP enviada")
            
            # Actualizar last_sent
            self.datos.set_last_sent_date(hoy_str)
            self.datos.save_data()
            notif_debug.log_info(f"✓ last_sent actualizado a {hoy_str}")
            
        except Exception as e:
            notif_debug.log_error(f"Error en _check_scheduled_notifications: {str(e)}")

    def on_stop(self):
        try:
            self.datos.save_data()
            notif_debug.log_info("App cerrada - datos guardados")
        except:
            pass

if __name__ == '__main__':
    RetoPS5App().run()
