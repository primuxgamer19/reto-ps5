# /ui/ui_regalo.py
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from collections import defaultdict
from ui.ui_widgets import RegaloRow, DateEditPopup
import logic.motor_matematico as motor_matematico
from ui.ui_historial import GenericHistorialScreen

class RegaloScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows = []
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.titulo = Label(
            text="--- CENTRO DE BENDICIONES ---", 
            font_size='22sp', 
            color=(0, 1, 0.4, 1), 
            size_hint_y=None, 
            height=50,
            bold=True
        )
        self.main_layout.add_widget(self.titulo)
        
        btn_hist = Button(
            text="VER HISTORIAL DE REGALOS", 
            size_hint_y=None, 
            height=55, 
            background_color=(0, 0.6, 0.2, 1),
            bold=True
        )
        btn_hist.bind(on_press=self.ir_al_historial)
        self.main_layout.add_widget(btn_hist)

        self.subtitulo = Label(
            text="¿Quién se portó guapo con la plata hoy?", 
            halign="center", 
            size_hint_y=None, 
            height=40
        )
        self.main_layout.add_widget(self.subtitulo)
        
        self.scroll = ScrollView(size_hint=(1, 1))
        self.lista_ui = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        self.lista_ui.bind(minimum_height=self.lista_ui.setter('height'))
        self.scroll.add_widget(self.lista_ui)
        self.main_layout.add_widget(self.scroll)
        
        self.res_bendicion = Label(
            text="", 
            color=(0, 0.8, 0.8, 1), 
            halign="center", 
            valign="middle", 
            size_hint_y=None, 
            height=120,
            font_size='16sp'
        )
        self.res_bendicion.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, w[1])))
        self.main_layout.add_widget(self.res_bendicion)
        
        botones_accion = BoxLayout(size_hint_y=None, height=65, spacing=12)
        
        btn_add = Button(text="AÑADIR REGALO", background_color=(0.2, 0.6, 0.2, 1), bold=True)
        btn_add.bind(on_press=self.añadir_item_vacio)
        
        btn_guardar = Button(text="GUARDAR INGRESOS", background_color=(0, 0.5, 0.8, 1), bold=True)
        btn_guardar.bind(on_press=self.procesar_regalo)
        
        botones_accion.add_widget(btn_add)
        botones_accion.add_widget(btn_guardar)
        self.main_layout.add_widget(botones_accion)
        
        btn_volver = Button(
            text="VOLVER AL PRESUPUESTO", 
            size_hint_y=None, 
            height=60, 
            background_color=(0.4, 0.4, 0.4, 1),
            bold=True
        )
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'presupuesto'))
        self.main_layout.add_widget(btn_volver)
        
        self.add_widget(self.main_layout)

    def on_enter(self):
        self.res_bendicion.text = "Registra los billetes que te cayeron del cielo..."
        self.refrescar_lista()

    def ir_al_historial(self, instance):
        if 'historial_regalos' not in self.manager.screen_names:
            self.manager.add_widget(HistorialRegalosScreen(name='historial_regalos'))
        self.manager.current = 'historial_regalos'

    def refrescar_lista(self):
        self.lista_ui.clear_widgets()
        self.rows = []
        app = App.get_running_app()
        for prod in getattr(app.datos, 'regalos_hoy', []):
            self.crear_fila(prod['nombre'], prod['precio'])

    def crear_fila(self, nombre, precio):
        row = RegaloRow(
            nombre, precio, 
            on_delete=lambda x: self.eliminar_fila(row),
            on_archive=lambda x: self.archivar_manual(row)
        )
        self.rows.append(row)
        self.lista_ui.add_widget(row)

    def eliminar_fila(self, row):
        if row in self.rows:
            self.rows.remove(row)
            self.lista_ui.remove_widget(row)

    def añadir_item_vacio(self, instance):
        self.crear_fila("", "")

    def archivar_manual(self, row):
        data = row.get_data()
        if data['precio'] <= 0: return

        def confirmar_archivo(fecha_seleccionada):
            app = App.get_running_app()
            data['fecha'] = fecha_seleccionada
            app.datos.historial_regalos.append(data)
            app.datos.ingresos_acumulados += data['precio']
            app.datos.ingresos_extra = app.datos.ingresos_acumulados + getattr(app.datos, 'ingresos_hoy', 0.0)
            app.datos.save_data()
            self.eliminar_fila(row)
            self.res_bendicion.text = f"Regalo de {fecha_seleccionada} guardado en el historial."

        DateEditPopup(target="regalo", on_save=confirmar_archivo).open()

    def procesar_regalo(self, instance):
        app = App.get_running_app()
        app.datos.regalos_hoy = [r.get_data() for r in self.rows]
        app.datos.ingresos_hoy = sum(p['precio'] for p in app.datos.regalos_hoy)
        app.datos.fecha_regalo = datetime.date.today().strftime("%Y-%m-%d")
        
        app.datos.ingresos_extra = getattr(app.datos, 'ingresos_acumulados', 0.0) + app.datos.ingresos_hoy
        app.datos.save_data()
        
        if app.datos.ingresos_extra <= 0:
            self.res_bendicion.text = "Aún no te regalan nada... toca camellar duro."
            return

        self.res_bendicion.text = f"¡Coronaste hoy con: ${app.datos.ingresos_hoy:.2f}!\nTotal extra reunido: ${app.datos.ingresos_extra:.2f}"
            
        try:
            app.audio.play_fx('acierto.mp3')
        except:
            pass


# Wrapper que mantiene el nombre de clase original pero reutiliza GenericHistorialScreen
class HistorialRegalosScreen(GenericHistorialScreen):
    def __init__(self, **kw):
        super().__init__(
            data_attr='historial_regalos',
            total_label_template="TOTAL RECIBIDO: ${:.2f}",
            title_text="--- HISTORIAL DE BENDICIONES ---",
            back_target='regalo',
            color_header=(0, 1, 0.4, 1),
            value_prefix='+',
            mode='regalo',
            **kw
        )