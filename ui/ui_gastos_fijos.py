# /ui/ui_gastos_fijos.py
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from collections import defaultdict
from .ui_widgets import PecadoRow, DateEditPopup, PresupuestoRow, GastoFijoRow
from logic.filtro_nombres import FiltroNombres
import logic.motor_matematico as motor_matematico
from ui.ui_historial import GenericHistorialScreen

class GastosFijosScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows_fijos = []
        self.rows_necesarios = []
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.titulo = Label(text="--- GASTOS FIJOS Y NECESARIOS ---", font_size='22sp', color=(0, 1, 0.4, 1), size_hint_y=None, height=50, bold=True)
        self.main_layout.add_widget(self.titulo)

        self.main_layout.add_widget(Label(text="GASTOS FIJOS MENSUALES", size_hint_y=None, height=40, color=(0, 1, 0.8, 1), bold=True))
        self.total_fijos_label = Label(text="Total mensual: $0.00", size_hint_y=None, height=30, color=(1, 0.8, 0, 1), bold=True)
        self.main_layout.add_widget(self.total_fijos_label)
        
        self.scroll_fijos = ScrollView(size_hint=(1, None), height=220)
        self.lista_fijos = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.lista_fijos.bind(minimum_height=self.lista_fijos.setter('height'))
        self.scroll_fijos.add_widget(self.lista_fijos)
        self.main_layout.add_widget(self.scroll_fijos)
        
        btn_add_fijo = Button(text="AÑADIR GASTO FIJO MENSUAL", background_color=(0, 0.7, 0, 1), size_hint_y=None, height=50, bold=True)
        btn_add_fijo.bind(on_press=self.añadir_gasto_fijo_vacio)
        self.main_layout.add_widget(btn_add_fijo)

        btn_historial = Button(
            text="VER HISTORIAL DE GASTOS NECESARIOS E INVERSIONES", 
            size_hint_y=None, 
            height=55, 
            background_color=(0, 0.5, 0.5, 1),
            bold=True
        )
        btn_historial.bind(on_press=self.ir_al_historial)
        self.main_layout.add_widget(btn_historial)

        self.main_layout.add_widget(Label(text="GASTOS NECESARIOS E INVERSIONES DE HOY", size_hint_y=None, height=40, color=(1, 0.5, 0, 1), bold=True))
        
        self.scroll_necesarios = ScrollView(size_hint=(1, 1))
        self.lista_necesarios = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15)
        self.lista_necesarios.bind(minimum_height=self.lista_necesarios.setter('height'))
        self.scroll_necesarios.add_widget(self.lista_necesarios)
        self.main_layout.add_widget(self.scroll_necesarios)
        
        self.res_feedback = Label(text="", color=(0, 0.8, 0.8, 1), halign="center", size_hint_y=None, height=110, font_size='16sp')
        self.res_feedback.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, w[1])))
        self.main_layout.add_widget(self.res_feedback)
        
        botones_accion = BoxLayout(size_hint_y=None, height=65, spacing=12)
        btn_add_nec = Button(text="NUEVO GASTO/INVERSIÓN", background_color=(0.8, 0.4, 0, 1), bold=True)
        btn_add_nec.bind(on_press=self.añadir_necesario_vacio)
        
        btn_procesar = Button(text="GUARDAR GASTOS DE HOY", background_color=(0, 0.5, 0.8, 1), bold=True)
        btn_procesar.bind(on_press=self.procesar_gastos_necesarios)
        
        botones_accion.add_widget(btn_add_nec)
        botones_accion.add_widget(btn_procesar)
        self.main_layout.add_widget(botones_accion)
        
        btn_volver = Button(text="VOLVER AL PRESUPUESTO", size_hint_y=None, height=60, background_color=(0.2, 0.2, 0.2, 1), bold=True)
        btn_volver.bind(on_press=self.volver_al_presupuesto)
        self.main_layout.add_widget(btn_volver)
        
        self.add_widget(self.main_layout)

    def ir_al_historial(self, instance):
        self.guardar_estado_fijos()
        if 'historial_gastos_necesarios' not in self.manager.screen_names:
            self.manager.add_widget(HistorialGastosNecesariosScreen(name='historial_gastos_necesarios'))
        self.manager.current = 'historial_gastos_necesarios'

    def on_enter(self):
        self.res_feedback.text = "Registra gastos necesarios e inversiones de hoy..."
        self.refrescar_todo()

    def actualizar_total_fijos(self, *args):
        total_fijos = 0.0
        for row in self.rows_fijos:
            data = row.get_data()
            total_fijos += data['monto']
        self.total_fijos_label.text = f"Total mensual: ${total_fijos:.2f}"

    def guardar_estado_fijos(self):
        app = App.get_running_app()
        app.datos.gastos_fijos = [r.get_data() for r in self.rows_fijos]
        app.datos.save_data()

    def volver_al_presupuesto(self, instance):
        self.guardar_estado_fijos()
        app = App.get_running_app()
        app.datos.gastos_necesarios_hoy = [r.get_data() for r in self.rows_necesarios]
        app.datos.save_data()
        self.manager.current = 'presupuesto'

    def refrescar_todo(self):
        app = App.get_running_app()
        
        self.lista_fijos.clear_widgets()
        self.rows_fijos = []
        for g in getattr(app.datos, 'gastos_fijos', []):
            self.crear_fila_fija(g['nombre'], g['monto'], g.get('fecha_inicio', 'S/F'))
            
        self.actualizar_total_fijos()
        
        self.lista_necesarios.clear_widgets()
        self.rows_necesarios = []
        for g in getattr(app.datos, 'gastos_necesarios_hoy', []):
            self.crear_fila_necesario(g['nombre'], g.get('precio', 0))

    def crear_fila_fija(self, nombre, monto, fecha_inicio):
        row = GastoFijoRow(
            nombre, monto, fecha_inicio,
            on_delete=lambda x: self.eliminar_gasto_fijo(row),
            on_edit_date=lambda x: self.editar_fecha_gasto_fijo(row),
            on_change=self.actualizar_total_fijos
        )
        self.rows_fijos.append(row)
        self.lista_fijos.add_widget(row)

    def añadir_gasto_fijo_vacio(self, instance):
        fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
        self.crear_fila_fija('', '', fecha_hoy)
        self.actualizar_total_fijos()
        self.guardar_estado_fijos()

    def eliminar_gasto_fijo(self, row):
        if row in self.rows_fijos:
            self.rows_fijos.remove(row)
            self.lista_fijos.remove_widget(row)
            self.actualizar_total_fijos()
            self.guardar_estado_fijos()

    def editar_fecha_gasto_fijo(self, row):
        def guardar_nueva_fecha(date_str):
            row.fecha_inicio = date_str
            row.txt_fecha.text = date_str
            self.guardar_estado_fijos()
        DateEditPopup(target="meta", initial_date=row.fecha_inicio, on_save=guardar_nueva_fecha).open()

    def añadir_necesario_vacio(self, instance):
        self.crear_fila_necesario("", "")

    def crear_fila_necesario(self, nombre, precio):
        row = PecadoRow(
            nombre, precio,
            on_delete=lambda x: self.eliminar_necesario(row),
            on_archive=lambda x: self.archivar_necesario_manual(row)
        )
        self.rows_necesarios.append(row)
        self.lista_necesarios.add_widget(row)

    def eliminar_necesario(self, row):
        if row in self.rows_necesarios:
            self.rows_necesarios.remove(row)
            self.lista_necesarios.remove_widget(row)

    def archivar_necesario_manual(self, row):
        data = row.get_data()
        if data['precio'] <= 0: return

        def confirmar_archivo(fecha_seleccionada):
            app = App.get_running_app()
            data['fecha'] = fecha_seleccionada
            app.datos.historial_gastos_necesarios.append(data)
            app.datos.gasto_necesario_acumulado += data['precio']
            app.datos.save_data()
            self.eliminar_necesario(row)
            self.res_feedback.text = f"Gasto archivado el {fecha_seleccionada}"
        DateEditPopup(target="pecado", on_save=confirmar_archivo).open()

    def procesar_gastos_necesarios(self, instance):
        self.guardar_estado_fijos()
        
        app = App.get_running_app()
        app.datos.gastos_necesarios_hoy = [r.get_data() for r in self.rows_necesarios]
        app.datos.fecha_gasto_necesario = datetime.date.today().strftime("%Y-%m-%d")
        app.datos.save_data()
        
        gasto_hoy = sum(g.get('precio', 0) for g in app.datos.gastos_necesarios_hoy)
        
        filtro = FiltroNombres()
        analysis = filtro.analizar_lista(app.datos.gastos_necesarios_hoy)
        
        mensaje = f"Hoy gastaste ${gasto_hoy:.2f} en necesarios/inversiones.\n"
        
        hay_inversion = any(a['es_inversion'] for a in analysis)
        hay_imprevisto = any(a['es_imprevisto'] for a in analysis)
        hay_fraude = any(a['es_pecado_fraude'] for a in analysis)
        
        if hay_fraude:
            mensaje += "¡PILLADO! Algunos gastos parecen pendejos. Deberían ir en Pecados -_-"
        elif hay_inversion:
            if app.datos.salario <= 0:
                mensaje += "¡POR FIN TE DIGNAS A INVERTIR! Sigue camellando."
            else:
                mensaje += "¡Buena inversión! Esto suma para la meta."
        elif hay_imprevisto:
            mensaje += "Espero te recuperes pronto bro :)"
        else:
            mensaje += "Gastos necesarios registrados correctamente."
        
        self.res_feedback.text = mensaje
        try:
            app.audio.play_fx('acierto.mp3' if hay_inversion else 'alerta.wav')
        except:
            pass


# Wrapper
class HistorialGastosNecesariosScreen(GenericHistorialScreen):
    def __init__(self, **kw):
        super().__init__(
            data_attr='historial_gastos_necesarios',
            total_label_template="TOTAL GASTADO: ${:.2f}",
            title_text="--- HISTORIAL DE GASTOS ---\n (NESESARIOS E INVERSIONES)",
            back_target='gastos_fijos',
            color_header=(1, 0.5, 0, 1),
            value_prefix='',
            mode='gasto',
            **kw
        )