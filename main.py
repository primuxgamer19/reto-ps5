import datetime
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.popup import Popup

# --- MOTOR DE AUDIO OPTIMIZADO ---
class AudioManager:
    def __init__(self):
        self.bg_music = None
        self.music_13 = None
        self.is_playing_13 = False
        self.cache = {}

    def play_fx(self, file_name):
        if file_name not in self.cache:
            self.cache[file_name] = SoundLoader.load(file_name)
        
        sound = self.cache[file_name]
        if sound:
            sound.stop()
            sound.play()

    def play_bg(self, file_name):
        if not self.bg_music:
            self.bg_music = SoundLoader.load(file_name)
        if self.bg_music and self.bg_music.state == 'stop':
            self.bg_music.loop = True
            self.bg_music.volume = 0.3
            self.bg_music.play()

    def stop_bg(self):
        if self.bg_music: self.bg_music.stop()

    def stop_13(self):
        self.is_playing_13 = False
        if self.music_13: self.music_13.stop()

    def load_13_music(self, file_name):
        if not self.music_13:
            self.music_13 = SoundLoader.load(file_name)

# --- COMPONENTE DE UI PERSONALIZADO ---
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

# --- PANTALLAS ---
class PortadaScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=20)
        self.img = Image(source='portada_img.png') 
        layout.add_widget(self.img)
        layout.add_widget(Label(text="Cargando calculadora del Reto...", size_hint_y=None, height=50))
        self.add_widget(layout)

    def on_enter(self):
        app = App.get_running_app()
        app.audio.load_13_music('letania13.mp3')
        Clock.schedule_once(self.ir_a_calculadora, 3)

    def ir_a_calculadora(self, dt):
        App.get_running_app().audio.play_bg('ps5.mp3')
        self.manager.current = 'calculadora'
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

        nav_box = BoxLayout(size_hint_y=None, height=80, spacing=10)
        btn_meta = Button(text="PRESUPUESTO", background_color=(0.2, 0.6, 1, 1))
        btn_meta.bind(on_press=lambda x: setattr(self.manager, 'current', 'presupuesto'))
        
        btn_notif = Button(text="NOTIFICACIONES", background_color=(1, 0.5, 0, 1))
        btn_notif.bind(on_press=lambda x: setattr(self.manager, 'current', 'notificaciones'))
        
        nav_box.add_widget(btn_meta)
        nav_box.add_widget(btn_notif)
        self.layout.add_widget(nav_box)

        self.res_meta = Label(text="Meta Total: $---", font_size='16sp')
        self.res_tiempo = Label(text="Tiempo: ---", color=(0, 0.8, 1, 1))
        self.res_falta = Label(text="Te falta: $---", color=(1, 0.5, 0, 1))
        self.res_cuota = Label(text="Cuota limite mensual: $---")
        self.res_posible = Label(text="Libre tras arriendo: $---\n", color=(0.5, 1, 0.5, 1), halign="center") # LABEL CONCENTRADO EN 2 LINEAS
        self.res_estado = Label(text="Estado: Esperando datos...", italic=True, halign="center")
        
        for widget in [self.res_meta, self.res_tiempo, self.res_falta, self.res_cuota, self.res_posible, self.res_estado]:
            self.layout.add_widget(widget)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        app = App.get_running_app()
        meta = sum(p['precio'] for p in app.productos)
        self.res_meta.text = f"Meta Total: ${meta:.2f}"

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
            except:
                fecha_limite = datetime.date.today() + datetime.timedelta(days=30)
                
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

            msg, sound = self.obtener_feedback(ahorrado, meta, total_dias, porcentaje, cuota)
            self.res_estado.text = msg
            if sound: app.audio.play_fx(sound)
                
        except ValueError:
            self.res_estado.text = "¡Pon un numero valido! xD"
            app.audio.play_fx('erro.mp3')
    def obtener_feedback(self, ahorrado, meta, dias, porcentaje, cuota):
        app = App.get_running_app()
        disponible_mes = app.salario - app.arriendo
        
        # Calculamos si termina antes ahorrando todo su billete libre
        meses_limite = max(1, dias / 30.0)
        if disponible_mes > 0:
            meses_fast = (meta - ahorrado) / disponible_mes
            termina_antes = meses_fast < meses_limite
        else:
            meses_fast = 9999
            termina_antes = False

        # 1. EASTER EGGS INTACTOS Y EXCEPCIONES ABSOLUTAS
        if ahorrado > 10000: return "¡Ni tu te lo crees! XD\n¿Robaste un banco o que?", 'pum.mp3'
        if ahorrado == 666: return "¿$666? ¡El diablo Bro o_O!", 'pum.mp3'
        if ahorrado == 777: return "¿$777? ¡Hey muy buenas a todos, Guapisimos!\nB-)", 'acierto.mp3'
        if 0 < ahorrado < 0.0001: return "POBREZA MOLECULAR DETECTADA.\n¡No trolees y busca camello! xd", 'pum.mp3'
        if ahorrado == 67: return "ni se te ocurra decirlo... -_-", 'alerta.wav'

        # 2. MENTIROSO SIN SALARIO
        if app.salario <= 0 and porcentaje >= 50 and ahorrado < meta:
            return f"¡Ni tu te lo crees! XD\nSin camello y ya tienes ${ahorrado}?\n¿A quien atracaste bro?", 'pum.mp3'

        # 3. VICTORIA ABSOLUTA
        if ahorrado >= meta:
            return "¡LO LOGRASTE! B-)\nLa PS5 es tuya. ¡A viciar!", 'Alelulla.wav'

        # 4. TIEMPO AGOTADO (y no ha ganado)
        if dias <= 0:
            return f"¡RETO PERDIDO! F en el chat.\nTe pasaste {-dias} dias de la fecha\ny sigues pobre. ¡A RAPARSE!", 'pum.mp3'

        # 5. SIN SALARIO DECLARADO / SIN FONDOS
        if app.salario <= 0 and porcentaje < 50:
            return "¡BUSCA CAMELLO VAGO! -_-\nSi no, te quedas calvo y\ncomiendo pizza con piña.", 'pum.mp3'

        # 6. CALCULANDO NIVELES BAJOS (0 a 1.99)
        if ahorrado <= 1.99:
            if ahorrado < 0.01: msg = f"NIVEL: VACIO TOTAL x_x\nCon ${ahorrado} no pagas ni aire."
            elif ahorrado < 0.05: msg = f"NIVEL: MISERIA -_-\n${ahorrado} no compra ni chicle."
            elif ahorrado < 0.50: msg = f"NIVEL: HAMBRE T_T\n${ahorrado} no compra empanada."
            else: msg = f"NIVEL: LIMPIO (._.)\n${ahorrado:.2f} no alcanza pal encebollado."

            if dias < 60: msg += f"\n¡Queda poco tiempo y tu en cero!\nLa maquina de afeitar te espera."
            elif termina_antes and disponible_mes >= cuota: 
                msg += f"\n¡Derrochador! Te sobran ${disponible_mes:.2f} libre.\nSi ahorraras bien, en {meses_fast:.1f} meses coronas."
            elif disponible_mes > 0 and disponible_mes >= cuota: msg += "\n¡Oye ponte serio con el ahorro\ny no seas derrochador!"
            elif disponible_mes > 0 and disponible_mes < cuota: msg += "\n¡Ya se acaba el tiempo y tu sueldo\nno alcanza! Busca extras."
            else: msg += f"\nPero tranki, faltan {dias} dias.\n¡Mueve ese culo y ahorra!"
            
            return msg, 'pum.mp3'

        # 7. PROGRESO MEDIO-BAJO (PELIGRO MAXIMO)
        if porcentaje < 30:
            if dias < 60: return f"PELIGRO MAXIMO [{porcentaje:.1f}%]. [PIZZA CON PIÑA]\n¡La pizza ya salio del horno D:!", 'pum.mp3'
            elif termina_antes: return f"PELIGRO MAXIMO [{porcentaje:.1f}%].\nDeja de gastar a lo loco, con tu billete\nlibre podrias terminar en {meses_fast:.1f} meses.", 'pum.mp3'
            elif disponible_mes >= cuota: return f"PELIGRO MAXIMO [{porcentaje:.1f}%].\nTienes sueldo, asi que pellizcate.", 'pum.mp3'
            else: return f"PELIGRO MAXIMO [{porcentaje:.1f}%].\nLa cuota es alta, ajustate los pantalones.", 'pum.mp3'

        # 8. PROGRESO MEDIO (A MEDIA LLAVE)
        if porcentaje < 70:
            if dias < 60 or cuota > disponible_mes: return f"A MEDIA BRO [{porcentaje:.1f}%] o_o\nPero igual te tocara rapada por atrasado -_-", 'pum.mp3'
            elif termina_antes: return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\nCon tus ${disponible_mes:.2f} libres podrias\nterminar en {meses_fast:.1f} meses ¡Dale!", 'alerta.wav'
            elif disponible_mes >= cuota and dias > 120: return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\nUff de que lo logras lo logras :D", 'alerta.wav'
            else: return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\n¡Dale que falta camello! T_T", 'alerta.wav'

        # 9. PROGRESO ALTO (CASI AHI)
        if dias < 30 and disponible_mes < cuota:
            return f"¡CASI AHI! [{porcentaje:.1f}%] --->\nPero el tiempo respira en tu nuca D:", 'alerta.wav'
        
        return f"¡CASI AHI! [{porcentaje:.1f}%] --->\nYa huelo el plastico nuevo :D", 'acierto.mp3'
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
        
        self.finanzas_box.add_widget(Label(text="Tu Salario Mensual ($):", size_hint_y=None, height=20))
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

    def añadir_item_vacio(self, instance):
        self.lista_ui.remove_widget(self.fecha_box)
        self.crear_fila("Nuevo", 0.0)
        self.lista_ui.add_widget(self.fecha_box)

    def eliminar_fila(self, row_obj):
        if row_obj in self.rows:
            self.rows.remove(row_obj)
            self.lista_ui.remove_widget(row_obj)

    def guardar_y_volver(self, instance):
        app = App.get_running_app()
        app.productos = [r.get_data() for r in self.rows]
        app.fecha_limite = self.date_input.text
        
        try:
            app.salario = float(self.salario_input.text or 0)
            app.arriendo = float(self.arriendo_input.text or 0)
        except:
            app.salario = 0
            app.arriendo = 0

        meta = sum(p['precio'] for p in app.productos)
        ahorrado = float(app.ahorrado_guardado or 0)
        falta = meta - ahorrado
        
        try:
            fecha_limite = datetime.datetime.strptime(app.fecha_limite, "%Y-%m-%d").date()
            hoy = datetime.date.today()
            meses = max(1, (fecha_limite - hoy).days // 30)
        except: meses = 1
        
        cuota = falta / meses
        disponible = app.salario - app.arriendo

        if app.salario <= 0 or disponible < cuota:
            app.audio.play_fx('pum.mp3')
        else:
            app.audio.play_fx('acierto.mp3')

        app.save_data()
        self.manager.current = 'calculadora'

class NotificacionesScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        layout.add_widget(Label(text="--- AJUSTES DE NOTIFICACIÓN ---", font_size='18sp', size_hint_y=None, height=50))
        layout.add_widget(Label(text="¿A qué hora quieres que te joda la app? (0-23)", size_hint_y=None, height=30))
        
        self.hour_input = TextInput(text="15", multiline=False, input_filter='int', font_size='30sp', size_hint_y=None, height=80)
        layout.add_widget(self.hour_input)
        
        btn_save = Button(text="GUARDAR AJUSTES", background_color=(0, 0.8, 0, 1), size_hint_y=None, height=80)
        btn_save.bind(on_press=self.guardar_ajustes)
        layout.add_widget(btn_save)
        
        btn_back = Button(text="VOLVER", background_color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=80)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'calculadora'))
        layout.add_widget(btn_back)
        
        layout.add_widget(Label(text="Nota: La app te avisará cada 24 horas\nsi sigues con el mismo monto.", italic=True))
        self.add_widget(layout) # ESTO ESTABA MAL INDENTADO Y LO ARREGLAMOS B-

            def on_enter(self):
        app = App.get_running_app()
        self.hour_input.text = str(app.notif_hour)

    def guardar_ajustes(self, instance):
        app = App.get_running_app()
        try:
            h = int(self.hour_input.text)
            if 0 <= h <= 23:
                app.notif_hour = h
                app.save_data()
                self.manager.current = 'calculadora'
            else:
                app.audio.play_fx('erro.mp3')
        except:
            app.audio.play_fx('erro.mp3')

class RetoPS5App(App):
    def build(self):
        Window.softinput_mode = "pan"
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.audio = AudioManager()
        self.data_file = "ahorro_data.json"
        self.load_data()
        
        Clock.schedule_interval(self.check_notifications, 60)
        
        sm = ScreenManager()
        sm.add_widget(PortadaScreen(name='portada'))
        sm.add_widget(CalculadoraScreen(name='calculadora'))
        sm.add_widget(PresupuestoScreen(name='presupuesto'))
        sm.add_widget(NotificacionesScreen(name='notificaciones'))
        return sm

    def check_notifications(self, dt):
        ahora = datetime.datetime.now()
        if ahora.hour == self.notif_hour:
            hoy_str = ahora.strftime("%Y-%m-%d")
            if self.last_notif_date != hoy_str:
                self.show_notif_popup()
                self.last_notif_date = hoy_str
                self.save_data()

    def show_notif_popup(self):
        monto = self.ahorrado_guardado if self.ahorrado_guardado else "0"
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=f"Cuéntame cuánto tienes hoy...\n¿O acaso sigues con ${monto}? 🤨", halign="center"))
        btn = Button(text="¡Ya voy, ya voy!", size_hint_y=None, height=50)

        popup = Popup(title='¡RECORDATORIO DEL RETO!', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
        self.audio.play_fx('alerta.wav')

    def trigger_13_logic(self):
        if self.audio.is_playing_13: return
        self.audio.is_playing_13 = True
        
        self.audio.stop_bg()
        self.audio.play_fx('pum.mp3')
        Clock.schedule_once(self.play_letania, 0.8)

    def play_letania(self, dt):
        if not self.audio.music_13:
            self.audio.load_13_music('letania13.mp3')
        if self.audio.music_13:
            self.audio.music_13.bind(on_stop=lambda instance: setattr(self.audio, 'is_playing_13', False))
            self.audio.music_13.play()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.productos = data.get('productos', [])
                    self.ahorrado_guardado = data.get('ahorrado', "")
                    self.fecha_limite = data.get('fecha_limite', "2026-11-19")
                    self.notif_hour = data.get('notif_hour', 15)
                    self.last_notif_date = data.get('last_notif_date', "")
                    self.salario = data.get('salario', 0.0)
                    self.arriendo = data.get('arriendo', 0.0)
            except: self.set_defaults()
        else: self.set_defaults()

    def set_defaults(self):
        self.productos = [
            {'nombre': 'PS5 Slim', 'precio': 550.0},
            {'nombre': 'Regulador', 'precio': 60.0},
            {'nombre': 'Monitor 1080p', 'precio': 280.0},
            {'nombre': 'GTA 6', 'precio': 150.0}
        ]
        self.ahorrado_guardado = ""
        self.fecha_limite = "2026-11-19"
        self.notif_hour = 15
        self.last_notif_date = ""
        self.salario = 0.0
        self.arriendo = 0.0

    def save_data(self):
        data = {
            'productos': self.productos, 
            'ahorrado': self.ahorrado_guardado, 
            'fecha_limite': self.fecha_limite,
            'notif_hour': self.notif_hour,
            'last_notif_date': self.last_notif_date,
            'salario': self.salario,
            'arriendo': self.arriendo
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def on_stop(self):
        self.save_data()

if __name__ == '__main__':
    RetoPS5App().run()
        
