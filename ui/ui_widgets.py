# ui/ui_widgets.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
import datetime

# Import relativo: widgets está dentro del paquete ui
from .widgets.date_edit_popup import DateEditPopup
from .widgets.info_popup import InfoPopup
from .widgets.export_dialog import ExportDialog
from .widgets.import_dialog import ImportDialog

# === Filas existentes (se mantienen aquí) ===

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
    def __init__(self, nombre, precio, on_delete, on_archive, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=60, spacing=5, **kwargs)
        
        btn_old = Button(text="¡", size_hint_x=None, width=40, background_color=(1, 0.7, 0, 1))
        btn_old.bind(on_press=on_archive)
        
        self.txt_nombre = TextInput(text=nombre, multiline=False, hint_text="¿Qué compraste?")
        self.txt_precio = TextInput(text=str(precio), multiline=False, input_filter='float', hint_text="$$$")
        
        btn_del = Button(text="X", size_hint_x=None, width=40, background_color=(1, 0, 0, 1))
        btn_del.bind(on_press=on_delete)
        
        self.add_widget(btn_old)
        self.add_widget(self.txt_nombre)
        self.add_widget(self.txt_precio)
        self.add_widget(btn_del)

    def get_data(self):
        try: p = float(self.txt_precio.text)
        except: p = 0.0
        return {'nombre': self.txt_nombre.text, 'precio': p}

# === NUEVO WIDGET PARA REGALOS ===
class RegaloRow(BoxLayout):
    def __init__(self, nombre, precio, on_delete, on_archive, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=60, spacing=5, **kwargs)
        
        btn_old = Button(text="¡", size_hint_x=None, width=40, background_color=(0, 0.8, 0.2, 1))
        btn_old.bind(on_press=on_archive)
        
        self.txt_nombre = TextInput(text=nombre, multiline=False, hint_text="¿De quién o de dónde?")
        self.txt_precio = TextInput(text=str(precio), multiline=False, input_filter='float', hint_text="$$$")
        
        btn_del = Button(text="X", size_hint_x=None, width=40, background_color=(1, 0, 0, 1))
        btn_del.bind(on_press=on_delete)
        
        self.add_widget(btn_old)
        self.add_widget(self.txt_nombre)
        self.add_widget(self.txt_precio)
        self.add_widget(btn_del)

    def get_data(self):
        try: p = float(self.txt_precio.text)
        except: p = 0.0
        return {'nombre': self.txt_nombre.text, 'precio': p}

class GastoFijoRow(BoxLayout):
    """Fila para gastos fijos mensuales (Editable y a prueba de fallos)"""
    def __init__(self, nombre, monto, fecha_inicio, on_delete, on_edit_date, on_change, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=70, spacing=5, **kwargs)
        self.fecha_inicio = fecha_inicio

        self.txt_nombre = TextInput(
            text=nombre, multiline=False, size_hint_x=0.45, hint_text="Nombre del gasto"
        )
        
        self.txt_monto = TextInput(
            text=str(monto), multiline=False, input_filter='float', size_hint_x=0.2, hint_text="$$$"
        )
        
        self.txt_nombre.bind(text=on_change)
        self.txt_monto.bind(text=on_change)
        
        self.txt_fecha = Label(text=fecha_inicio, size_hint_x=0.2, font_size='13sp', color=(0.6, 0.6, 0.6, 1))
        
        btn_edit = Button(text="!", size_hint_x=None, width=40, background_color=(0.2, 0.6, 1, 1))
        btn_edit.bind(on_press=on_edit_date)
        
        btn_del = Button(text="X", size_hint_x=None, width=40, background_color=(1, 0, 0, 1))
        btn_del.bind(on_press=on_delete)
        
        self.add_widget(self.txt_nombre)
        self.add_widget(self.txt_monto)
        self.add_widget(self.txt_fecha)
        self.add_widget(btn_edit)
        self.add_widget(btn_del)

    def get_data(self):
        try:
            m = float(self.txt_monto.text)
        except ValueError:
            m = 0.0
            
        return {'nombre': self.txt_nombre.text, 'monto': m, 'fecha_inicio': self.fecha_inicio}

# === Re-exportar popups para compatibilidad con código existente ===
__all__ = [
    'PresupuestoRow', 'PecadoRow', 'RegaloRow', 'GastoFijoRow',
    'DateEditPopup', 'InfoPopup', 'ExportDialog', 'ImportDialog'
]