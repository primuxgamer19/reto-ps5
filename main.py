import datetime
import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

# IMPORTAMOS TUS MÓDULOS
from audio import AudioManager
from ui_screens import CalculadoraScreen, PresupuestoScreen, PecadoScreen

class RetoPS5App(App):
    def build(self):
        Window.softinput_mode = "pan"
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.audio = AudioManager()
        self.data_file = "ahorro_data.json"
        self.load_data()
        
        sm = ScreenManager()
        # Calculadora es ahora la pantalla principal
        sm.add_widget(CalculadoraScreen(name='calculadora'))
        sm.add_widget(PresupuestoScreen(name='presupuesto'))
        sm.add_widget(PecadoScreen(name='pecado'))
        return sm

    def on_pause(self):
        # Retornar True le dice a Android: "Pausa la app, no la mates"
        return True

    def on_resume(self):
        # Al volver a abrir la app desde segundo plano, checamos eventos diarios
        self.check_daily_events()
        return True

    def on_start(self):
        # Al abrir la app desde cero, checamos eventos diarios
        self.check_daily_events()
        # PRECARGAMOS LA LETANÍA DEL 13 PARA EVITAR EL CUELLO DE BOTELLA DEL AUDIO
        try:
            if not getattr(self.audio, 'music_13', None):
                self.audio.load_13_music('letania13.mp3')
        except Exception:
            pass

    def check_daily_events(self):
        hoy_str = datetime.date.today().strftime("%Y-%m-%d")
        
        # 1. Resetear el pecado si ya es otro día (y acumular lo de ayer)
        if getattr(self, 'fecha_gasto', "") != hoy_str:
            # Sumar lo que se gastó exactamente en la lista del día anterior al acumulado
            gasto_ayer = sum(p.get('precio', 0) for p in getattr(self, 'pecados_hoy', []))
            self.gasto_acumulado = getattr(self, 'gasto_acumulado', 0.0) + gasto_ayer
            
            # Limpiamos la bandeja para un nuevo día
            self.pecados_hoy = []
            self.gasto_hoy = 0.0
            self.fecha_gasto = hoy_str
            self.save_data()

        # 2. Notificaciones de saludo
        if self.is_first_run:
            self.is_first_run = False
            self.last_notif_date = hoy_str
            self.save_data()
            return

        if self.last_notif_date != hoy_str:
            self.show_notif_popup()
            self.last_notif_date = hoy_str
            self.save_data()

    def show_notif_popup(self):
        monto = self.ahorrado_guardado if self.ahorrado_guardado else "0"
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=f"Cuéntame cuánto tienes hoy...\n¿O acaso sigues con ${monto}? -_-", halign="center"))
        btn = Button(text="¡Ya voy, ya voy!", size_hint_y=None, height=50)

        popup = Popup(title='¡RECORDATORIO DEL RETO!', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
        self.audio.play_fx('alerta.wav')

    # --- EASTER EGG REPARADO Y OPTIMIZADO ---
    def trigger_13_logic(self):
        # Bloqueo para evitar múltiples clics
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
                # Limpiar binds antiguos para no crashear
                self.audio.music_13.unbind(on_stop=self._reset_13_flag)
                self.audio.music_13.bind(on_stop=self._reset_13_flag)
                self.audio.music_13.play()
            else:
                self._reset_13_flag()
        except Exception:
            self._reset_13_flag()

    def _reset_13_flag(self, *args):
        self.audio.is_playing_13 = False

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.productos = data.get('productos', [])
                    self.ahorrado_guardado = data.get('ahorrado', "")
                    self.fecha_limite = data.get('fecha_limite', "2026-11-19")
                    self.last_notif_date = data.get('last_notif_date', "")
                    self.is_first_run = data.get('is_first_run', True)
                    self.salario = data.get('salario', 0.0)
                    self.arriendo = data.get('arriendo', 0.0)
                    self.gasto_hoy = data.get('gasto_hoy', 0.0)
                    self.fecha_gasto = data.get('fecha_gasto', "")
                    self.fecha_salario = data.get('fecha_salario', "")
                    self.gasto_acumulado = data.get('gasto_acumulado', 0.0)
                    self.pecados_hoy = data.get('pecados_hoy', [])
            except (FileNotFoundError, json.JSONDecodeError): 
                self.set_defaults()
        else: 
            self.set_defaults()

    def set_defaults(self):
        self.productos = [
            {'nombre': 'PS5 Slim', 'precio': 550.0},
            {'nombre': 'Regulador', 'precio': 60.0},
            {'nombre': 'Monitor 1080p', 'precio': 280.0},
            {'nombre': 'GTA 6', 'precio': 150.0}
        ]
        self.ahorrado_guardado = ""
        self.fecha_limite = "2026-11-19"
        self.last_notif_date = ""
        self.is_first_run = True
        self.salario = 0.0
        self.arriendo = 0.0
        self.gasto_hoy = 0.0
        self.fecha_gasto = ""
        self.fecha_salario = ""
        self.gasto_acumulado = 0.0
        self.pecados_hoy = []

    def save_data(self):
        data = {
            'productos': self.productos, 
            'ahorrado': self.ahorrado_guardado, 
            'fecha_limite': self.fecha_limite,
            'last_notif_date': self.last_notif_date,
            'is_first_run': self.is_first_run,
            'salario': self.salario,
            'arriendo': self.arriendo,
            'gasto_hoy': self.gasto_hoy,
            'fecha_gasto': self.fecha_gasto,
            'fecha_salario': self.fecha_salario,
            'gasto_acumulado': self.gasto_acumulado,
            'pecados_hoy': self.pecados_hoy
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def on_stop(self):
        self.save_data()

if __name__ == '__main__':
    RetoPS5App().run()
