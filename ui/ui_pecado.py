# /ui/ui_pecado.py
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from collections import defaultdict

from ui.ui_widgets import PecadoRow, DateEditPopup
import logic.motor_matematico as motor_matematico
from ui.ui_historial import GenericHistorialScreen

class PecadoScreen(Screen):
    # ... (todo el código de PecadoScreen se mantiene exactamente igual, solo agrego el historial abajo)
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows = []
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.titulo = Label(
            text="--- EL CONFESIONARIO ---", 
            font_size='22sp', 
            color=(1, 0, 0, 1), 
            size_hint_y=None, 
            height=50,
            bold=True
        )
        self.main_layout.add_widget(self.titulo)
        
        btn_hist = Button(
            text="VER HISTORIAL Y ESTADÍSTICAS", 
            size_hint_y=None, 
            height=55, 
            background_color=(0, 0.5, 0.5, 1),
            bold=True
        )
        btn_hist.bind(on_press=self.ir_al_historial)
        self.main_layout.add_widget(btn_hist)

        self.subtitulo = Label(
            text="¿Qué compraste hoy que no debías?", 
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
        
        self.res_castigo = Label(
            text="", 
            color=(1, 0.5, 0, 1), 
            halign="center", 
            valign="middle", 
            size_hint_y=None, 
            height=120,
            font_size='16sp'
        )
        self.res_castigo.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, w[1])))
        self.main_layout.add_widget(self.res_castigo)
        
        botones_accion = BoxLayout(size_hint_y=None, height=65, spacing=12)
        
        btn_add = Button(text="AÑADIR FILA", background_color=(0.8, 0.4, 0, 1), bold=True)
        btn_add.bind(on_press=self.añadir_item_vacio)
        
        btn_confesar = Button(text="CONFESAR TODO", background_color=(0.8, 0, 0, 1), bold=True)
        btn_confesar.bind(on_press=self.procesar_pecado)
        
        botones_accion.add_widget(btn_add)
        botones_accion.add_widget(btn_confesar)
        self.main_layout.add_widget(botones_accion)
        
        btn_volver = Button(
            text="VOLVER AL REPORTE", 
            size_hint_y=None, 
            height=60, 
            background_color=(0.2, 0.6, 1, 1),
            bold=True
        )
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'calculadora'))
        self.main_layout.add_widget(btn_volver)
        
        self.add_widget(self.main_layout)

    def on_enter(self):
        self.res_castigo.text = "Confiesa tus gastos innecesarios de hoy..."
        self.refrescar_lista()

    def ir_al_historial(self, instance):
        if 'historial_pecados' not in self.manager.screen_names:
            # Wrapper que reutiliza la pantalla genérica
            self.manager.add_widget(HistorialPecadosScreen(name='historial_pecados'))
        self.manager.current = 'historial_pecados'

    def refrescar_lista(self):
        self.lista_ui.clear_widgets()
        self.rows = []
        app = App.get_running_app()
        for prod in getattr(app.datos, 'pecados_hoy', []):
            self.crear_fila(prod['nombre'], prod['precio'])

    def crear_fila(self, nombre, precio):
        row = PecadoRow(
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
            app.datos.historial_pecados.append(data)
            app.datos.gasto_acumulado += data['precio']
            app.datos.save_data()
            self.eliminar_fila(row)
            self.res_castigo.text = f"Pecado de {fecha_seleccionada} archivado."

        DateEditPopup(target="pecado", on_save=confirmar_archivo).open()

    def procesar_pecado(self, instance):
        app = App.get_running_app()
        app.datos.pecados_hoy = [r.get_data() for r in self.rows]
        app.datos.gasto_hoy = sum(p['precio'] for p in app.datos.pecados_hoy)
        app.datos.fecha_gasto = datetime.date.today().strftime("%Y-%m-%d")
        app.datos.save_data()
        
        gasto_total_historico = getattr(app.datos, 'gasto_acumulado', 0.0) + app.datos.gasto_hoy
        
        if gasto_total_historico <= 0:
            self.res_castigo.text = "No has pecado... vas por buen camino."
            return

        dias_retraso = motor_matematico.calcular_impacto_pecado(app.datos, gasto_total_historico)
        
        if dias_retraso != float('inf'):
            self.res_castigo.text = f"Hoy: ${app.datos.gasto_hoy:.2f} | Total: ${gasto_total_historico:.2f}\nRetraso en meta: {dias_retraso:.1f} días."
        else:
            self.res_castigo.text = f"Hoy: ${app.datos.gasto_hoy:.2f} | Total: ${gasto_total_historico:.2f}\nRetraso: INFINITO."
            
        try:
            app.audio.play_fx('pum.mp3')
        except:
            pass


# Wrapper que mantiene el nombre de clase original pero reutiliza GenericHistorialScreen
class HistorialPecadosScreen(GenericHistorialScreen):
    def __init__(self, **kw):
        super().__init__(
            data_attr='historial_pecados',
            total_label_template="GASTO TOTAL: ${:.2f}",
            title_text="--- REGISTRO DE PECADOS ---",
            back_target='pecado',
            color_header=(1, 0, 0, 1),
            value_prefix='',
            mode='pecado',
            **kw
        )