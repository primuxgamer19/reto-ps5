# widgets/info_popup.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget

class InfoPopup(Popup):
    def __init__(self, mensaje, title="Información", **kwargs):
        """
        InfoPopup mantiene la firma original para compatibilidad.
        El popup conserva su tamaño original (no se hace más grande).
        Si el texto es largo, el contenido se muestra dentro de un ScrollView
        para que el usuario pueda scrollear sin que el popup cambie de tamaño.
        """
        super().__init__(title=title, size_hint=(0.85, 0.4), **kwargs)
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # Scrollable area que ocupa el espacio disponible dentro del popup
        scroll = ScrollView(size_hint=(1, 1))
        inner = BoxLayout(orientation='vertical', size_hint_y=None, padding=(0,0), spacing=10)
        inner.bind(minimum_height=inner.setter('height'))
        
        # Label que ajusta su altura a la textura y permite scrollear
        lbl = Label(text=mensaje, halign='left', valign='top', size_hint_y=None)
        lbl.bind(texture_size=lambda s, t: setattr(s, 'height', t[1]))
        lbl.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        inner.add_widget(lbl)
        
        scroll.add_widget(inner)
        content.add_widget(scroll)
        
        btn = Button(text="ENTENDIDO", size_hint_y=None, height=50, background_color=(0, 0.5, 0.8, 1))
        btn.bind(on_press=self.dismiss)
        content.add_widget(btn)
        self.content = content