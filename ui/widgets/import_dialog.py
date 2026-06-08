# widgets/import_dialog.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
import os

class ImportDialog(Popup):
    def __init__(self, directory, on_import_callback, **kwargs):
        super().__init__(title="Seleccionar Respaldo (Importar)", size_hint=(0.9, 0.75), **kwargs)
        self.on_import_callback = on_import_callback
        self.directory = directory
        
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        lbl_dir = Label(text=f"Buscando en:\n{directory}", size_hint_y=None, height=50, color=(0.7, 0.7, 0.7, 1), halign='center')
        lbl_dir.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        content.add_widget(lbl_dir)
        
        scroll = ScrollView()
        self.list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        
        archivos = []
        if os.path.exists(directory):
            archivos = [f for f in os.listdir(directory) if f.endswith('.json')]
        
        if not archivos:
            self.list_box.add_widget(Label(text="No se encontraron archivos JSON en esta carpeta.", size_hint_y=None, height=60))
        else:
            for arch in archivos:
                btn = Button(text=arch, size_hint_y=None, height=60, background_normal='', background_color=(0.2, 0.6, 0.8, 1))
                btn.bind(on_press=lambda instance, nombre_arch=arch: self._procesar_import(nombre_arch))
                self.list_box.add_widget(btn)
                
        scroll.add_widget(self.list_box)
        content.add_widget(scroll)
        
        btn_cancel = Button(text="CANCELAR", size_hint_y=None, height=55, background_color=(0.8, 0, 0, 1), bold=True)
        btn_cancel.bind(on_press=self.dismiss)
        content.add_widget(btn_cancel)
        
        self.content = content

    def _procesar_import(self, filename):
        ruta_completa = os.path.join(self.directory, filename)
        self.on_import_callback(ruta_completa)
        self.dismiss()