# widgets/export_dialog.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import datetime

class ExportDialog(Popup):
    def __init__(self, on_export_callback, **kwargs):
        super().__init__(title="Exportar Respaldo (JSON)", size_hint=(0.85, 0.5), **kwargs)
        self.on_export_callback = on_export_callback
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(text="Elige un nombre para tu archivo:", size_hint_y=None, height=30))
        
        fecha_actual = datetime.date.today().strftime('%Y%m%d')
        self.txt_name = TextInput(text=f"MiRespaldo_{fecha_actual}", multiline=False, size_hint_y=None, height=50)
        content.add_widget(self.txt_name)
        
        content.add_widget(Widget()) 
        
        btn_box = BoxLayout(size_hint_y=None, height=55, spacing=15)
        btn_ok = Button(text="GUARDAR", background_color=(0, 0.7, 0, 1), bold=True)
        btn_ok.bind(on_press=self._procesar_export)
        btn_cancel = Button(text="CANCELAR", background_color=(0.8, 0, 0, 1), bold=True)
        btn_cancel.bind(on_press=self.dismiss)
        
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cancel)
        content.add_widget(btn_box)
        self.content = content

    def _procesar_export(self, instance):
        nombre = self.txt_name.text.strip()
        if not nombre:
            nombre = "Respaldo_SinNombre"
        self.on_export_callback(nombre)
        self.dismiss()