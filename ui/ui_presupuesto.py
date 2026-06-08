# /ui/ui_presupuesto.py
import datetime
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

from ui.ui_widgets import PresupuestoRow, DateEditPopup, ExportDialog, ImportDialog, InfoPopup
import logic.motor_matematico as motor_matematico
from data.io_utils import compartir_json_nativo

class PresupuestoScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows = []
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.main_layout.add_widget(Label(text="--- CONFIGURAR PRESUPUESTO ---", size_hint_y=None, height=40))
        
        self.scroll = ScrollView()
        self.lista_ui = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.lista_ui.bind(minimum_height=self.lista_ui.setter('height'))
        
        self.finanzas_box = BoxLayout(orientation='vertical', size_hint_y=None, height=430, spacing=5)
        self.finanzas_box.add_widget(Label(text="--- FINANZAS ---", color=(0, 1, 0.8, 1), size_hint_y=None, height=30))
        
        salario_label_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=35, spacing=5)
        salario_label_box.add_widget(Label(text="Tu Salario Mensual ($):"))
        btn_edit_fecha = Button(text="!", size_hint_x=None, width=35, background_color=(0.8, 0.6, 0, 1))
        btn_edit_fecha.bind(on_press=self.abrir_popup_fecha_salario)
        salario_label_box.add_widget(btn_edit_fecha)
        
        self.finanzas_box.add_widget(salario_label_box)
        
        self.salario_input = TextInput(text="0", multiline=False, input_filter='float', size_hint_y=None, height=45)
        self.finanzas_box.add_widget(self.salario_input)
        
        # El viejo input de arriendo ahora es botón a la nueva pantalla
        self.finanzas_box.add_widget(Label(text="Gastos Fijos Mensuales y Necesarios:", size_hint_y=None, height=20))
        self.btn_gastos_fijos = Button(
            text="GESTIONAR GASTOS FIJOS Y NECESARIOS", 
            background_color=(0.8, 0.4, 0, 1), 
            bold=True, 
            size_hint_y=None, 
            height=55
        )
        self.btn_gastos_fijos.bind(on_press=self.ir_a_gastos_fijos)
        self.finanzas_box.add_widget(self.btn_gastos_fijos)

        self.finanzas_box.add_widget(Label(text="Ingresos Extra/Regalos Totales ($):", size_hint_y=None, height=20))
        
        # BOTÓN QUE REEMPLAZA AL TEXTINPUT
        self.btn_ingresos_extra = Button(
            text="GESTIONAR REGALOS: $0.00", 
            background_color=(0.1, 0.8, 0.3, 1), 
            bold=True, 
            size_hint_y=None, 
            height=45
        )
        self.btn_ingresos_extra.bind(on_press=self.ir_a_regalos)
        self.finanzas_box.add_widget(self.btn_ingresos_extra)
        
        # ============== BOTONES DE GESTIÓN DE BASE DE DATOS ==============
        datos_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        btn_export = Button(text="EXPORTAR JSON", background_color=(0.3, 0.3, 0.3, 1))
        btn_export.bind(on_press=self.abrir_exportar)
        btn_import = Button(text="IMPORTAR JSON", background_color=(0.3, 0.3, 0.3, 1))
        btn_import.bind(on_press=self.abrir_importar)
        
        datos_box.add_widget(btn_export)
        datos_box.add_widget(btn_import)
        
        datos_container = BoxLayout(orientation='vertical', size_hint_y=None, height=60, padding=[0, 10, 0, 0])
        datos_container.add_widget(datos_box)
        self.finanzas_box.add_widget(datos_container)
        
        # --- AÑADIDO: botón de notificaciones (única modificación solicitada) ---
        self.btn_notificaciones = Button(
            text="CONFIGURAR NOTIFICACIONES",
            background_color=(0.6, 0.2, 0.8, 1),
            bold=False,
            size_hint_y=None,
            height=45
        )
        self.btn_notificaciones.bind(on_press=self.ir_a_notificaciones)
        self.finanzas_box.add_widget(self.btn_notificaciones)
        # --- FIN ADICIÓN ---
        
        self.fecha_box = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=5)
        self.fecha_box.add_widget(Label(text="META (AAAA-MM-DD):", size_hint_y=None, height=30))
        self.date_input = TextInput(
            multiline=False, size_hint_y=None, height=60, font_size='18sp',
            hint_text="YYYY-MM-DD", hint_text_color=(0.5, 0.5, 0.5, 1),
            readonly=True, 
            background_color=(0.95, 0.95, 0.95, 1)
        )
        self.date_input.bind(on_touch_down=self._on_date_input_touch)
        self.fecha_box.add_widget(self.date_input)
        
        self.scroll.add_widget(self.lista_ui)
        self.main_layout.add_widget(self.scroll)

        botones = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_add = Button(text="AÑADIR PRODUCTO", background_color=(0, 0.7, 0, 1))
        btn_add.bind(on_press=self.añadir_item_vacio)
        btn_ok = Button(text="ACEPTAR / GUARDAR", background_color=(0, 0.5, 1, 1))
        btn_ok.bind(on_press=self.guardar_y_volver)
        botones.add_widget(btn_add)
        botones.add_widget(btn_ok)
        self.main_layout.add_widget(botones)
        
        self.add_widget(self.main_layout)

    def ir_a_gastos_fijos(self, instance):
        if 'gastos_fijos' in self.manager.screen_names:
            self.manager.current = 'gastos_fijos'

    def ir_a_regalos(self, instance):
        if 'regalo' in self.manager.screen_names:
            self.manager.current = 'regalo'

    # --- AÑADIDO: handler mínimo y seguro para el botón de notificaciones ---
    def ir_a_notificaciones(self, instance):
        try:
            mgr = getattr(self, "manager", None)
            if mgr is None:
                InfoPopup(mensaje="No puedo abrir notificaciones: manager no disponible.", title="Error").open()
                return
            if 'notificaciones' in mgr.screen_names:
                mgr.current = 'notificaciones'
            else:
                InfoPopup(mensaje="La pantalla de notificaciones no está registrada.", title="Error").open()
        except Exception as e:
            try:
                InfoPopup(mensaje=f"Error al abrir notificaciones: {e}", title="Error").open()
            except:
                print("Error al abrir notificaciones:", e)
    # --- FIN ADICIÓN ---

    # =============== INTELIGENCIA PARA PYDROID VS APK COMPILADO ===============
    def _es_android_compilado(self):
        """Si detecta ANDROID_ARGUMENT o ANDROID_PRIVATE, es un APK oficial (Buildozer)."""
        return 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE' in os.environ

    # =============== FUNCIONES DE EXPORTAR E IMPORTAR ===============
    def abrir_exportar(self, instance):
        app = App.get_running_app()
        self.guardar_estado_actual()
        
        if self._es_android_compilado():
            # Método Nuevo: Compartir directo por WhatsApp/Drive
            exito, msg = compartir_json_nativo(app.datos.data_file)
            InfoPopup(mensaje=msg, title="Compartir Respaldo").open()
        else:
            # Método Viejo: Para Pydroid 3 o PC
            popup = ExportDialog(on_export_callback=self.ejecutar_exportacion)
            popup.open()

    def ejecutar_exportacion(self, nombre_archivo):
        app = App.get_running_app()
        self.guardar_estado_actual() 
        exito, mensaje = app.datos.exportar_json(nombre_archivo)
        InfoPopup(mensaje=mensaje, title="Resultado de Exportación").open()

    def abrir_importar(self, instance):
        if self._es_android_compilado():
            # Método Nuevo: Abrir explorador nativo de Android
            try:
                from plyer import filechooser
                filechooser.open_file(on_selection=self._seleccionar_archivo_nativo, filters=["*.json"])
            except Exception as e:
                # Si falla algo raro, volvemos al viejo confiable
                self._abrir_importar_viejo()
        else:
            # Método Viejo: Para Pydroid 3 o PC
            self._abrir_importar_viejo()

    def _abrir_importar_viejo(self):
        app = App.get_running_app()
        directorio = app.datos.obtener_ruta_exportacion()
        popup = ImportDialog(directory=directorio, on_import_callback=self.ejecutar_importacion)
        popup.open()

    def _seleccionar_archivo_nativo(self, selection):
        if selection:
            ruta = selection[0]
            self.ejecutar_importacion(ruta)

    def ejecutar_importacion(self, ruta_archivo):
        app = App.get_running_app()
        exito, mensaje = app.datos.importar_json(ruta_archivo)
        if exito:
            self.on_enter()
            InfoPopup(mensaje=mensaje, title="Importación Exitosa").open()
        else:
            InfoPopup(mensaje=mensaje, title="Error de Importación").open()
            
    # =============== MANEJO DE FECHAS ===============
    def _on_date_input_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            app = App.get_running_app()
            popup = DateEditPopup(
                target="meta",
                initial_date=app.datos.fecha_limite,
                on_save=lambda date_str: self._update_meta_date(date_str)
            )
            popup.open()

    def _update_meta_date(self, date_str):
        self.date_input.text = date_str
        app = App.get_running_app()
        app.datos.fecha_limite = date_str
        app.datos.save_data()

    def abrir_popup_fecha_salario(self, instance):
        app = App.get_running_app()
        popup = DateEditPopup(
            target="salario",
            initial_date=getattr(app.datos, 'fecha_salario', datetime.date.today().strftime("%Y-%m-%d")),
            on_save=lambda date_str: self._update_salario_date(date_str)
        )
        popup.open()

    def _update_salario_date(self, date_str):
        app = App.get_running_app()
        app.datos.fecha_salario = date_str
        app.datos.save_data()

    # =============== MANEJO DE VISTA ===============
    def on_enter(self):
        app = App.get_running_app()
        self.date_input.text = app.datos.fecha_limite
        self.salario_input.text = str(app.datos.salario)
        
        # ACTUALIZAR EL TEXTO DEL BOTÓN DE REGALOS
        total_ingresos = getattr(app.datos, 'ingresos_extra', 0.0)
        self.btn_ingresos_extra.text = f"GESTIONAR REGALOS: ${total_ingresos:.2f}"
        
        self.refrescar_lista()

    def refrescar_lista(self):
        self.lista_ui.clear_widgets()
        self.rows = []
        app = App.get_running_app()
        self.lista_ui.add_widget(self.finanzas_box)
        for prod in app.datos.productos:
            self.crear_fila(prod['nombre'], prod['precio'])
        self.lista_ui.add_widget(self.fecha_box)

    def crear_fila(self, nombre, precio):
        row = PresupuestoRow(nombre, precio, on_delete=lambda x: self.eliminar_fila(row))
        self.rows.append(row)
        self.lista_ui.add_widget(row)

    def eliminar_fila(self, row):
        if row in self.rows:
            self.rows.remove(row)
            self.lista_ui.remove_widget(row)

    def añadir_item_vacio(self, instance):
        self.lista_ui.remove_widget(self.fecha_box)
        self.crear_fila("Nuevo", 0.0)
        self.lista_ui.add_widget(self.fecha_box)

    def guardar_estado_actual(self):
        app = App.get_running_app()
        app.datos.productos = [r.get_data() for r in self.rows]
        app.datos.fecha_limite = self.date_input.text
        try:
            nuevo_salario = float(self.salario_input.text or 0)
            if getattr(app.datos, 'salario', 0) == 0 and nuevo_salario > 0:
                if not getattr(app.datos, 'fecha_salario', ""):
                    app.datos.fecha_salario = datetime.date.today().strftime("%Y-%m-%d")
            app.datos.salario = nuevo_salario
        except:
            pass
        app.datos.save_data()

    def guardar_y_volver(self, instance):
        app = App.get_running_app()
        self.guardar_estado_actual()
        
        ahorrado = float(app.datos.ahorrado_guardado or 0)
        reporte = motor_matematico.analizar_reporte(app.datos, ahorrado)
        
        falta = reporte.get("falta", 0)
        if reporte.get("error"):
            try:
                app.audio.play_fx('erro.mp3')
            except:
                pass
        elif falta > 0 and reporte.get('disponible_mes', 0) < reporte.get('cuota', 0):
            try:
                app.audio.play_fx('pum.mp3')
            except:
                pass
        else:
            try:
                app.audio.play_fx('acierto.mp3')
            except:
                pass

        self.manager.current = 'calculadora'