# ui/ui_calculadora.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image

import logic.motor_matematico as motor_matematico
from logic.feedback_logic import obtener_feedback_msg
from logic.filtro_nombres import FiltroNombres

from resources.images import resolve_image

class CalculadoraScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        app = App.get_running_app()
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.layout.add_widget(Label(text="--- CALCULADORA DEL RETO PS5 beta ---", font_size='20sp', color=(1, 0, 0, 1)))
        
        # NUEVO: Layout horizontal para la pregunta y el botón de gráfica (imagen en lugar de emoji)
        header_ahorro = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        header_ahorro.add_widget(Label(text="¿Cuanto tienes ahorrado? ($)"))
        
        # Intentar resolver la imagen; si no existe, usar un Button con texto como fallback
        graf_icon_path = resolve_image('grafica_icon.png')
        if graf_icon_path:
            btn_grafica = Image(source=graf_icon_path, size_hint_x=None, width=60)
            btn_grafica.allow_stretch = True
            btn_grafica.keep_ratio = True
            # navegación al tocar la imagen
            btn_grafica.bind(on_touch_down=lambda inst, touch: setattr(self.manager, 'current', 'estadistica') if inst.collide_point(*touch.pos) else None)
        else:
            btn_grafica = Button(text="VER GRÁFICA", size_hint_x=None, width=100, background_color=(0, 0.8, 0.4, 1), bold=True)
            btn_grafica.bind(on_press=lambda x: setattr(self.manager, 'current', 'estadistica'))

        header_ahorro.add_widget(btn_grafica)
        self.layout.add_widget(header_ahorro)
        
        self.money_input = TextInput(text=app.datos.ahorrado_guardado, multiline=False, input_filter='float', size_hint_y=None, height=100)
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
        self.res_cuota = Label(text="Cuota minima mensual: $---")
        self.res_cuota_diaria = Label(text="Cuota diaria: $---", color=(1, 0.6, 0.2, 1))
        
        self.res_posible = Label(text="Libre tras arriendo: $---", color=(0.5, 1, 0.5, 1), halign="center")
        self.res_posible.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, None)))
        
        self.res_sospecha = Label(text="", color=(1, 0.2, 0.2, 1), bold=True, halign="center")
        self.res_sospecha.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, None)))
        
        self.res_estado = Label(text="Estado: Esperando datos...", italic=True, halign="center", size_hint_y=None)
        self.res_estado.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - 20, None)), texture_size=lambda s, t: setattr(s, 'height', t[1] + 40))
        
        for widget in [self.res_meta, self.res_tiempo, self.res_falta, self.res_cuota, self.res_cuota_diaria, self.res_posible, self.res_sospecha, self.res_estado]:
            self.layout.add_widget(widget)

        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        try:
            app.audio.play_bg('ps5.mp3')
        except:
            pass
        
        meta = sum(p['precio'] for p in app.datos.productos)
        self.res_meta.text = f"Meta Total: ${meta:.2f}"

        if getattr(app.datos, 'gasto_hoy', 0) > 0 and self.money_input.text:
            self.actualizar_reporte(None)

    def actualizar_reporte(self, instance):
        app = App.get_running_app()
        try:
            ahorrado = float(self.money_input.text or 0)
            app.datos.ahorrado_guardado = str(ahorrado)
            app.datos.save_data()
            
            reporte = motor_matematico.analizar_reporte(app.datos, ahorrado)

            if reporte["error"] == "PRESUPUESTO_VACIO":
                self.res_estado.text = "¡Presupuesto vacio!\nAñade algo."
                try: app.audio.play_fx('erro.mp3')
                except: pass
                return
            elif reporte["error"] == "FECHA_INVALIDA":
                self.res_estado.text = "¡Fecha límite INVÁLIDA!\nVe a presupuesto y corrígela."
                try: app.audio.play_fx('erro.mp3')
                except: pass
                return

            saldo_esperado = reporte["saldo_esperado"]
            
            if saldo_esperado > 0 and ahorrado < (saldo_esperado - 0.01):
                diferencia = saldo_esperado - ahorrado
                self.res_sospecha.text = f"¡Oe! Según fechas e ingresos deberías tener ${saldo_esperado:.2f}.\nTe faltan ${diferencia:.2f}... ¿Gastos pendejos sin confesar? D:"
            elif ahorrado > (saldo_esperado + 0.01):
                sobrante = ahorrado - saldo_esperado
                self.res_sospecha.text = f"¡ALTO CHORO! Se supone deberias tener ${saldo_esperado:.2f} y tienes ${sobrante:.2f} de más...\nsi no pusiste bien un dato corrigelo ¿o acaso atracaste? ¡habla serio cabron! D:"
            else:
                self.res_sospecha.text = ""

            self.res_tiempo.text = f"Faltan: {reporte['meses_aprox']} meses ({reporte['total_dias']} dias)"
            self.res_falta.text = f"Te faltan: ${reporte['falta']:.2f}"
            cuota_mensual = reporte.get('cuota', float('inf'))
            cuota_diaria = reporte.get('cuota_diaria', None)
            if cuota_mensual == float('inf'):
                self.res_cuota.text = "Cuota minima mensual: IMPOSIBLE"
            else:
                self.res_cuota.text = f"Cuota minima mensual: ${cuota_mensual:.2f}"
            if cuota_diaria is None or cuota_diaria == float('inf'):
                self.res_cuota_diaria.text = "Cuota diaria: IMPOSIBLE"
            else:
                self.res_cuota_diaria.text = f"Cuota diaria: ${cuota_diaria:.2f}"

            if reporte['disponible_mes'] > 0 and reporte['falta'] > 0:
                self.res_posible.text = f"Dinero libre al mes: ${reporte['disponible_mes']:.2f}\n(Podrias ganar en {reporte['meses_rapidos']:.1f} meses)"
            else:
                self.res_posible.text = f"Dinero libre al mes: ${reporte['disponible_mes']:.2f}\n(Estas frito con los gastos)"

            if ahorrado == 13:
                self.res_estado.text = "entre más me la mamas\nmás me crece"
                try: app.trigger_13_logic()
                except: pass
                return

            try:
                app.audio.stop_13()
                app.audio.play_bg('ps5.mp3')
            except:
                pass

            msg, sound = obtener_feedback_msg(app.datos, ahorrado, reporte)
            self.res_estado.text = msg
            if sound:
                try: app.audio.play_fx(sound)
                except: pass
                
        except ValueError:
            self.res_estado.text = "¡Pon un numero valido! xD"
            try: app.audio.play_fx('erro.mp3')
            except: pass
