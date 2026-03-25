import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.uix.popup import Popup

from feedback_logic import obtener_feedback_msg

class PresupuestoRow(BoxLayout):
    def __init__(self, nombre, precio, on_delete, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=60, spacing=5, **kwargs)
        self.txt_nombre = TextInput(text=nombre, multiline=False)
        self.txt_precio = TextInput(text=str(precio), multiline=False, input_filter='float')
        btn_del = Button(text="X", size_hint_x=None, width=40, background_color=(1, 0, 0, 1))
        btn_del.bind(on_press=on_delete)
        
        self.add_widget(self.txt_nombre)
        self.add_widget(self.txt_precio)
        self.add_widget(btn_del)

    def get_data(self):
        try: p = float(self.txt_precio.text)
        except: p = 0.0
        return {'nombre': self.txt_nombre.text, 'precio': p}

class PecadoRow(BoxLayout):
    def __init__(self, nombre, precio, on_delete, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=60, spacing=5, **kwargs)
        self.txt_nombre = TextInput(text=nombre, multiline=False, hint_text="¿Qué compraste?")
        self.txt_precio = TextInput(text=str(precio), multiline=False, input_filter='float', hint_text="$$$")
        btn_del = Button(text="X", size_hint_x=None, width=40, background_color=(1, 0, 0, 1))
        btn_del.bind(on_press=on_delete)
        
        self.add_widget(self.txt_nombre)
        self.add_widget(self.txt_precio)
        self.add_widget(btn_del)

    def get_data(self):
        try: p = float(self.txt_precio.text)
        except: p = 0.0
        return {'nombre': self.txt_nombre.text, 'precio': p}

class CalculadoraScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        app = App.get_running_app()
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.layout.add_widget(Label(text="--- CALCULADORA DEL RETO PS5 2.0 ---", font_size='20sp', color=(1, 0, 0, 1)))
        self.layout.add_widget(Label(text="¿Cuanto tienes ahorrado? ($)"))
        
        self.money_input = TextInput(text=app.ahorrado_guardado, multiline=False, input_filter='float', size_hint_y=None, height=100)
        self.layout.add_widget(self.money_input)

        btn_calc = Button(text='CALCULAR REPORTE', background_color=(0, 1, 0, 1), size_hint_y=None, height=100)
        btn_calc.bind(on_press=self.actualizar_reporte)
        self.layout.add_widget(btn_calc)

        nav_box = BoxLayout(size_hint_y=None, height=60, spacing=10)
        btn_meta = Button(text="PRESUPUESTO", background_color=(0.2, 0.6, 1, 1))
        btn_meta.bind(on_press=lambda x: setattr(self.manager, 'current', 'presupuesto'))
        
        btn_pecado = Button(text="PECADO MORTAL", background_color=(0.8, 0, 0, 1))
        btn_pecado.bind(on_press=lambda x: setattr(self.manager, 'current', 'pecado'))
        
        nav_box.add_widget(btn_meta)
        nav_box.add_widget(btn_pecado)
        self.layout.add_widget(nav_box)

        self.res_meta = Label(text="Meta Total: $---", font_size='16sp')
        self.res_tiempo = Label(text="Tiempo: ---", color=(0, 0.8, 1, 1))
        self.res_falta = Label(text="Te falta: $---", color=(1, 0.5, 0, 1))
        self.res_cuota = Label(text="Cuota limite mensual: $---")
        
        self.res_posible = Label(text="Libre tras arriendo: $---", color=(0.5, 1, 0.5, 1), halign="center")
        self.res_posible.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, None)))
        
        self.res_estado = Label(text="Estado: Esperando datos...", italic=True, halign="center")
        self.res_estado.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, None))) 
        
        for widget in [self.res_meta, self.res_tiempo, self.res_falta, self.res_cuota, self.res_posible, self.res_estado]:
            self.layout.add_widget(widget)

        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        app.audio.play_bg('ps5.mp3')
        
        meta = sum(p['precio'] for p in app.productos)
        self.res_meta.text = f"Meta Total: ${meta:.2f}"

        if getattr(app, 'gasto_hoy', 0) > 0 and self.money_input.text:
            self.actualizar_reporte(None)

    def actualizar_reporte(self, instance):
        app = App.get_running_app()
        try:
            ahorrado = float(self.money_input.text or 0)
            app.ahorrado_guardado = str(ahorrado)
            app.save_data()
            
            meta = sum(p['precio'] for p in app.productos)
            if meta <= 0:
                self.res_estado.text = "¡Presupuesto vacio!\nAñade algo."
                app.audio.play_fx('erro.mp3')
                return

            try:
                fecha_limite = datetime.datetime.strptime(app.fecha_limite, "%Y-%m-%d").date()
            except ValueError:
                self.res_estado.text = "¡Fecha límite INVÁLIDA!\nVe a presupuesto y corrígela."
                app.audio.play_fx('erro.mp3')
                return
                
            hoy = datetime.date.today()
            delta = fecha_limite - hoy
            total_dias = delta.days  
            meses_aprox = max(1, total_dias // 30) 
            
            falta = meta - ahorrado
            cuota = falta / meses_aprox
            porcentaje = (ahorrado / meta) * 100
            
            disponible_mes = app.salario - app.arriendo

            self.res_tiempo.text = f"Faltan: {meses_aprox} meses ({total_dias} dias)"
            self.res_falta.text = f"Te faltan: ${falta:.2f}"
            self.res_cuota.text = f"Cuota limite mensual: ${cuota:.2f}"
            
            if disponible_mes > 0 and falta > 0:
                meses_rapidos = falta / disponible_mes
                self.res_posible.text = f"Dinero libre al mes: ${disponible_mes:.2f}\n(Podrias ganar en {meses_rapidos:.1f} meses)"
            else:
                self.res_posible.text = f"Dinero libre al mes: ${disponible_mes:.2f}\n(Estas frito con los gastos)"

            if ahorrado == 13:
                self.res_estado.text = "entre más me la mamas\nmás me crece"
                app.trigger_13_logic()
                return

            app.audio.stop_13()
            app.audio.play_bg('ps5.mp3')

            msg, sound = obtener_feedback_msg(app, ahorrado, meta, total_dias, porcentaje, cuota)
            self.res_estado.text = msg
            if sound: app.audio.play_fx(sound)
                
        except ValueError:
            self.res_estado.text = "¡Pon un numero valido! xD"
            app.audio.play_fx('erro.mp3')

class PecadoScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows = []
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.main_layout.add_widget(Label(text="--- EL CONFESIONARIO ---", font_size='22sp', color=(1, 0, 0, 1), size_hint_y=None, height=40))
        self.main_layout.add_widget(Label(text="¿Qué compraste hoy que no debías?", halign="center", size_hint_y=None, height=30))
        
        self.scroll = ScrollView()
        self.lista_ui = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.lista_ui.bind(minimum_height=self.lista_ui.setter('height'))
        
        self.scroll.add_widget(self.lista_ui)
        self.main_layout.add_widget(self.scroll)
        
        self.res_castigo = Label(text="", color=(1, 0.5, 0, 1), halign="center", valign="middle", size_hint_y=None, height=140)
        self.res_castigo.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, w[1])))
        self.main_layout.add_widget(self.res_castigo)
        
        botones_accion = BoxLayout(size_hint_y=None, height=60, spacing=10)
        btn_add = Button(text="AÑADIR PECADO", background_color=(0.8, 0.4, 0, 1))
        btn_add.bind(on_press=self.añadir_item_vacio)
        btn_confesar = Button(text="CONFESAR PECADO", background_color=(0.8, 0, 0, 1))
        btn_confesar.bind(on_press=self.procesar_pecado)
        botones_accion.add_widget(btn_add)
        botones_accion.add_widget(btn_confesar)
        
        self.main_layout.add_widget(botones_accion)
        
        btn_volver = Button(text="VOLVER AL REPORTE", size_hint_y=None, height=60, background_color=(0.2, 0.6, 1, 1))
        btn_volver.bind(on_press=lambda x: setattr(self.manager, 'current', 'calculadora'))
        self.main_layout.add_widget(btn_volver)
        
        self.add_widget(self.main_layout)

    def on_enter(self):
        self.res_castigo.text = "Confiesa tus gastos innecesarios de hoy..."
        self.refrescar_lista()

    def refrescar_lista(self):
        self.lista_ui.clear_widgets()
        self.rows = []
        app = App.get_running_app()
        for prod in getattr(app, 'pecados_hoy', []):
            self.crear_fila(prod['nombre'], prod['precio'])

    def crear_fila(self, nombre, precio):
        row = PecadoRow(nombre, precio, on_delete=lambda x: self.eliminar_fila(row))
        self.rows.append(row)
        self.lista_ui.add_widget(row)

    def eliminar_fila(self, row):
        if row in self.rows:
            self.rows.remove(row)
            self.lista_ui.remove_widget(row)

    def añadir_item_vacio(self, instance):
        self.crear_fila("Gasto pendejo", 0.0)

    def procesar_pecado(self, instance):
        app = App.get_running_app()
        app.pecados_hoy = [r.get_data() for r in self.rows]
        app.gasto_hoy = sum(p['precio'] for p in app.pecados_hoy)
        app.fecha_gasto = datetime.date.today().strftime("%Y-%m-%d")
        app.save_data()
        
        gasto_total_historico = getattr(app, 'gasto_acumulado', 0.0) + app.gasto_hoy
        
        if gasto_total_historico <= 0:
            self.res_castigo.text = "No has pecado... vas por buen camino, más te vale."
            return

        disponible = app.salario - app.arriendo
        if disponible > 0:
            ahorro_diario = disponible / 30.0
            dias_retraso = gasto_total_historico / ahorro_diario
            self.res_castigo.text = f"Hoy: ${app.gasto_hoy:.2f} | Total Perdido: ${gasto_total_historico:.2f}\nTe atrasaste {dias_retraso:.1f} dias de la meta en total.\nTe pasas de verga -_-"
        else:
            self.res_castigo.text = f"Hoy: ${app.gasto_hoy:.2f} | Total Perdido: ${gasto_total_historico:.2f}\nRetraso: INFINITO. ¡Quedaras calvo!"
            
        try:
            app.audio.play_fx('pum.mp3')
        except:
            pass

class PresupuestoScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.rows = []
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.main_layout.add_widget(Label(text="--- CONFIGURAR PRESUPUESTO ---", size_hint_y=None, height=40))
        
        self.scroll = ScrollView()
        self.lista_ui = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.lista_ui.bind(minimum_height=self.lista_ui.setter('height'))
        
        self.finanzas_box = BoxLayout(orientation='vertical', size_hint_y=None, height=220, spacing=5)
        self.finanzas_box.add_widget(Label(text="--- FINANZAS ---", color=(0, 1, 0.8, 1), size_hint_y=None, height=30))
        
        # --- AQUÍ ESTÁ EL BOTÓN QUE PEDISTE PARA EDITAR LA FECHA ---
        salario_label_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=35, spacing=5)
        salario_label_box.add_widget(Label(text="Tu Salario Mensual ($):"))
        btn_edit_fecha = Button(text="!", size_hint_x=None, width=35, background_color=(0.8, 0.6, 0, 1))
        btn_edit_fecha.bind(on_press=self.abrir_popup_fecha)
        salario_label_box.add_widget(btn_edit_fecha)
        
        self.finanzas_box.add_widget(salario_label_box)
        
        self.salario_input = TextInput(text="0", multiline=False, input_filter='float', size_hint_y=None, height=45)
        self.finanzas_box.add_widget(self.salario_input)
        
        self.finanzas_box.add_widget(Label(text="Pago de Arriendo/Gastos ($):", size_hint_y=None, height=20))
        self.arriendo_input = TextInput(text="0", multiline=False, input_filter='float', size_hint_y=None, height=45)
        self.finanzas_box.add_widget(self.arriendo_input)
        
        self.fecha_box = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=5)
        self.fecha_box.add_widget(Label(text="META (AAAA-MM-DD):", size_hint_y=None, height=30))
        self.date_input = TextInput(
            multiline=False, size_hint_y=None, height=60, font_size='18sp',
            hint_text="YYYY-MM-DD", hint_text_color=(0.5, 0.5, 0.5, 1)
        )
        self.date_input.bind(text=self.auto_format_date)
        self.fecha_box.add_widget(self.date_input)
        
        self.scroll.add_widget(self.lista_ui)
        self.main_layout.add_widget(self.scroll)

        botones = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_add = Button(text="AÑADIR", background_color=(0, 0.7, 0, 1))
        btn_add.bind(on_press=self.añadir_item_vacio)
        btn_ok = Button(text="ACEPTAR", background_color=(0, 0.5, 1, 1))
        btn_ok.bind(on_press=self.guardar_y_volver)
        botones.add_widget(btn_add)
        botones.add_widget(btn_ok)
        self.main_layout.add_widget(botones)
        
        self.add_widget(self.main_layout)

    def abrir_popup_fecha(self, instance):
        app = App.get_running_app()
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text="Modificar fecha de\ninicio del salario (AAAA-MM-DD):", halign='center'))
        
        fecha_input = TextInput(text=getattr(app, 'fecha_salario', ""), multiline=False, size_hint_y=None, height=50)
        content.add_widget(fecha_input)
        
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_guardar = Button(text="Guardar", background_color=(0, 1, 0, 1))
        btn_cancelar = Button(text="Cancelar", background_color=(1, 0, 0, 1))
        
        btn_box.add_widget(btn_guardar)
        btn_box.add_widget(btn_cancelar)
        content.add_widget(btn_box)
        
        popup = Popup(title='Editar Fecha Salario', content=content, size_hint=(0.85, 0.4))
        
        def guardar_fecha(btn):
            app.fecha_salario = fecha_input.text
            app.save_data()
            popup.dismiss()
            
        btn_guardar.bind(on_press=guardar_fecha)
        btn_cancelar.bind(on_press=popup.dismiss)
        
        popup.open()

    def auto_format_date(self, instance, value):
        clean_text = "".join([c for c in value if c.isdigit()])
        new_text = ""
        if len(clean_text) > 0:
            new_text = clean_text[:4]
            if len(clean_text) > 4:
                new_text += "-" + clean_text[4:6]
                if len(clean_text) > 6:
                    new_text += "-" + clean_text[6:8]
        
        if value != new_text:
            instance.text = new_text
            instance.cursor = (len(new_text), 0)

    def on_enter(self):
        app = App.get_running_app()
        self.date_input.text = app.fecha_limite
        self.salario_input.text = str(app.salario)
        self.arriendo_input.text = str(app.arriendo)
        self.refrescar_lista()

    def refrescar_lista(self):
        self.lista_ui.clear_widgets()
        self.rows = []
        app = App.get_running_app()
        self.lista_ui.add_widget(self.finanzas_box)
        for prod in app.productos:
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

    def guardar_y_volver(self, instance):
        app = App.get_running_app()
        
        fecha_texto = self.date_input.text
        try:
            datetime.datetime.strptime(fecha_texto, "%Y-%m-%d")
        except ValueError:
            app.audio.play_fx('erro.mp3')
            self.date_input.text = "ERROR FECHA"
            return 

        app.productos = [r.get_data() for r in self.rows]
        app.fecha_limite = fecha_texto
        
        try:
            nuevo_salario = float(self.salario_input.text or 0)
            nuevo_arriendo = float(self.arriendo_input.text or 0)
            
            if getattr(app, 'salario', 0) == 0 and nuevo_salario > 0:
                # Solo poner fecha si estaba vacío para no dañar la que pusiste manual
                if not getattr(app, 'fecha_salario', ""):
                    app.fecha_salario = datetime.date.today().strftime("%Y-%m-%d")
                
            app.salario = nuevo_salario
            app.arriendo = nuevo_arriendo
        except:
            app.salario = 0
            app.arriendo = 0

        meta = sum(p['precio'] for p in app.productos)
        ahorrado = float(app.ahorrado_guardado or 0)
        falta = meta - ahorrado
        
        fecha_limite_obj = datetime.datetime.strptime(app.fecha_limite, "%Y-%m-%d").date()
        hoy = datetime.date.today()
        meses = max(1, (fecha_limite_obj - hoy).days // 30)
        
        cuota = falta / meses
        disponible = app.salario - app.arriendo

        if app.salario <= 0 or disponible < cuota:
            app.audio.play_fx('pum.mp3')
        else:
            app.audio.play_fx('acierto.mp3')

        app.save_data()
        self.manager.current = 'calculadora'
