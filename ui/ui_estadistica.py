# ui/ui_estadistica.py
import datetime

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.image import Image

import mat.mat_geometria as mat_geometria
import mat.mat_historia as mat_historia
from .ui_grafica_core import GraficaInteractiva
from resources.images import resolve_image

class EstadisticaScreen(Screen):
    """Envoltura de la pantalla principal"""
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))
        
        # Cabecera (reemplazar emoji por imagen si existe)
        header = BoxLayout(size_hint_y=None, height=dp(50))
        icon_path = resolve_image('grafica_icon.png')
        if icon_path:
            img = Image(source=icon_path, size_hint_x=None, width=dp(40))
            header.add_widget(img)
            header.add_widget(Label(text=" MAPA DE PROYECCIÓN FINANCIERA", font_size='16sp', color=(0, 1, 0.5, 1), bold=True))
        else:
            header.add_widget(Label(text="📈 MAPA DE PROYECCIÓN FINANCIERA", font_size='16sp', color=(0, 1, 0.5, 1), bold=True))
        self.layout.add_widget(header)
        
        # El Motor de Gráfica (importado desde ui_grafica_core)
        self.grafica = GraficaInteractiva(size_hint=(1, 1))
        self.layout.add_widget(self.grafica)
        
        # Botonera de utilidades
        controles = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        btn_reset = Button(text="Restablecer Vista", background_color=(0.2, 0.4, 0.6, 1), bold=True)
        btn_reset.bind(on_press=self.reset_zoom)
        controles.add_widget(btn_reset)
        self.layout.add_widget(controles)
        
        # Pie de página
        footer = BoxLayout(size_hint_y=None, height=dp(55))
        btn_volver = Button(text="VOLVER AL MENÚ", background_color=(0.3, 0.3, 0.3, 1), bold=True)
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'calculadora'))
        footer.add_widget(btn_volver)
        self.layout.add_widget(footer)
        
        self.add_widget(self.layout)

    def on_enter(self):
        # Inyección de dependencias en tiempo de ejecución
        app = App.get_running_app()
        linea_tiempo = mat_historia.generar_linea_tiempo(app.datos)
        productos = getattr(app.datos, 'productos', [])
        fecha_limite = getattr(app.datos, 'fecha_limite', "")
        
        # Alimentar el motor
        self.grafica.set_datos(linea_tiempo, productos, fecha_limite)

        # Asegurar que la vista por defecto (configurada en ui_config) se aplique al entrar.
        # Usamos la API pública del widget para restablecer la vista por defecto inmediatamente.
        try:
            self.grafica.reset_view_to_default()
        except Exception:
            # Fallback: comportamiento antiguo si el método no existe o falla
            self.grafica.view_x_min = self.grafica.world_x_min
            self.grafica.view_x_max = self.grafica.world_x_max
            self.grafica.view_y_min = self.grafica.world_y_min
            self.grafica.view_y_max = self.grafica.world_y_max

        # Forzar render con la vista por defecto aplicada
        self.grafica.actualizar_render()

    def reset_zoom(self, instance):
        # Usar la API pública del widget para restablecer la vista por defecto
        try:
            self.grafica.reset_view_to_default()
        except Exception:
            # Fallback: forzar los límites del mundo (comportamiento antiguo)
            self.grafica.view_x_min = self.grafica.world_x_min
            self.grafica.view_x_max = self.grafica.world_x_max
            self.grafica.view_y_min = self.grafica.world_y_min
            self.grafica.view_y_max = self.grafica.world_y_max
        finally:
            self.grafica.actualizar_render()