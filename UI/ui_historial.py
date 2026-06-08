# /ui/ui_historial.py
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.clock import Clock
from collections import defaultdict
import logic.motor_matematico as motor_matematico

class GenericHistorialScreen(Screen):
    """
    Pantalla de historial genérica y configurable.

    Parámetros esperados (pasar en super().__init__ o en la subclase wrapper):
      - data_attr: nombre del atributo en app.datos que contiene la lista de items (ej: 'historial_pecados')
      - total_label_template: texto base para el label total (ej: 'GASTO TOTAL: ${:.2f}')
      - title_text: texto del título (ej: '--- REGISTRO DE PECADOS ---')
      - back_target: nombre de la pantalla a la que vuelve el botón 'volver'
      - color_header: tupla RGBA para color de header de grupo
      - value_prefix: prefijo para mostrar valores ('+' para ingresos, '' o '$' para gastos)
      - mode: uno de 'pecado', 'regalo', 'gasto' para manejar la eliminación y ajustes en app.datos
    """

    def __init__(self,
                 data_attr,
                 total_label_template,
                 title_text,
                 back_target,
                 color_header=(1, 1, 1, 1),
                 value_prefix='',
                 mode='pecado',
                 **kw):
        super().__init__(**kw)
        self.data_attr = data_attr
        self.total_label_template = total_label_template
        self.title_text = title_text
        self.back_target = back_target
        self.color_header = color_header
        self.value_prefix = value_prefix
        self.mode = mode  # 'pecado' | 'regalo' | 'gasto'

        # internal for loading animation
        self._loading_event = None
        self._loading_frame = 0
        self._loading_frames = ["cargando", "cargando.", "cargando..", "cargando..."]

        # will hold the grupos to build asynchronously
        self._pending_grupos = None

        self.layout = BoxLayout(orientation='vertical', padding=[20, 30, 20, 20], spacing=10)

        # Determinar color del título según el modo (pecado=rojo, regalo=verde, gasto=naranja)
        title_color_map = {
            'pecado': (1, 0, 0, 1),      # rojo
            'regalo': (0, 1, 0, 1),      # verde
            'gasto': (1, 0.5, 0, 1)      # naranja
        }
        title_color = title_color_map.get(self.mode, self.color_header)

        self.titulo_hist = Label(
            text=self.title_text,
            font_size='20sp',
            size_hint_y=None,
            height=50,
            bold=True,
            color=title_color,
            halign='center',
            valign='middle'
        )
        # Ajuste para que el label respete el ancho y calcule su altura por el texto
        self.titulo_hist.bind(
            width=lambda s, w: setattr(s, 'text_size', (w, None)),
            texture_size=lambda s, t: setattr(s, 'height', t[1] + 10)
        )
        self.layout.add_widget(self.titulo_hist)

        # Total principal: aplicar color según el modo (mismo esquema que el título)
        self.total_label = Label(
            text=self.total_label_template.format(0.0),
            font_size='20sp',
            size_hint_y=None,
            height=40,
            bold=True,
            color=title_color
        )
        self.layout.add_widget(self.total_label)

        self.mes_label = Label(
            text="POR MES:",
            size_hint_y=None,
            halign="center",
            valign="top"
        )
        self.mes_label.bind(
            width=lambda s, w: setattr(s, 'text_size', (w, None)),
            texture_size=lambda s, t: setattr(s, 'height', t[1] + 10)
        )
        self.layout.add_widget(self.mes_label)

        self.layout.add_widget(BoxLayout(size_hint_y=None, height=10))

        # Loading label: mostrará la animación "cargando" en bucle hasta que los widgets estén listos.
        self.loading_label = Label(
            text=self._loading_frames[0],
            font_size='24sp',
            size_hint_y=None,
            height=80,
            bold=True,
            halign='center',
            valign='middle'
        )
        self.loading_label.bind(
            width=lambda s, w: setattr(s, 'text_size', (w, None)),
            texture_size=lambda s, t: setattr(s, 'height', t[1] + 10)
        )
        # Añadimos el loading_label en el layout en la posición donde deberían ir los widgets.
        self.layout.add_widget(self.loading_label)

        # Scroll y lista (inicialmente ocultos hasta que termine la carga)
        self.scroll = ScrollView(size_hint=(1, 1))
        self.hist_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=20)
        self.hist_list.bind(minimum_height=self.hist_list.setter('height'))
        self.scroll.add_widget(self.hist_list)
        # ocultamos el scroll hasta que se complete la carga
        self.scroll.opacity = 0
        self.scroll.disabled = True
        self.layout.add_widget(self.scroll)

        btn_back = Button(
            text=f"VOLVER",
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.2, 0.2, 1),
            bold=True
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', self.back_target))
        self.layout.add_widget(btn_back)

        self.add_widget(self.layout)

    def _animate_loading(self, dt):
        # Actualiza el texto del loading_label en bucle
        self._loading_frame = (self._loading_frame + 1) % len(self._loading_frames)
        self.loading_label.text = self._loading_frames[self._loading_frame]

    def _start_loading_animation(self):
        # Inicia la animación si no está ya corriendo
        if self._loading_event is None:
            self._loading_frame = 0
            self.loading_label.text = self._loading_frames[0]
            self.loading_label.opacity = 1
            self._loading_event = Clock.schedule_interval(self._animate_loading, 0.5)

    def _stop_loading_animation(self):
        # Detiene la animación y oculta el label de carga, mostrando los widgets
        if self._loading_event is not None:
            self._loading_event.cancel()
            self._loading_event = None
        self.loading_label.opacity = 0
        self.scroll.opacity = 1
        self.scroll.disabled = False

    def _build_hist_widgets(self, dt):
        """
        Construye los widgets del historial a partir de self._pending_grupos.
        Esta función se ejecuta en el loop principal pero programada con schedule_once,
        de modo que la animación pueda correr mientras tanto.
        """
        grupos = self._pending_grupos or {}
        # Construcción de widgets
        for fecha_grupo, items in grupos.items():
            if fecha_grupo == datetime.date.today().strftime("%Y-%m-%d"):
                header_text = "HOY"
            elif fecha_grupo == (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"):
                header_text = "AYER"
            else:
                try:
                    d = datetime.datetime.strptime(fecha_grupo, "%Y-%m-%d")
                    header_text = d.strftime("%d/%m/%y")
                except:
                    header_text = fecha_grupo

            header = Label(
                text=header_text,
                size_hint_y=None,
                height=50,
                font_size='18sp',
                color=self.color_header,
                bold=True,
                halign='center'
            )
            header.bind(
                width=lambda s, w: setattr(s, 'text_size', (w, None)),
                texture_size=lambda s, t: setattr(s, 'height', t[1] + 10)
            )
            self.hist_list.add_widget(header)

            for item in items:
                row = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, spacing=10)

                nombre_txt = item.get('nombre', 'Item')
                lbl_nom = Label(
                    text=nombre_txt,
                    halign="left",
                    valign="middle",
                    size_hint_x=0.65
                )
                lbl_nom.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
                row.add_widget(lbl_nom)

                valor = item.get('precio', 0) if 'precio' in item else item.get('monto', 0)

                # color del valor: regalos verdes, gastos/normales rojos, gastos necesarios naranja para 'gasto'
                if self.mode == 'regalo':
                    valor_color = (0, 1, 0, 1)
                elif self.mode == 'gasto':
                    valor_color = (1, 0.5, 0, 1)
                else:
                    valor_color = (1, 0, 0, 1)

                row.add_widget(Label(
                    text=f"{self.value_prefix}${valor:.2f}",
                    size_hint_x=0.20,
                    color=valor_color,
                    bold=True,
                    font_size='16sp'
                ))

                btn_del = Button(
                    text="X",
                    size_hint_x=None,
                    width=45,
                    background_color=(1, 0, 0, 1),
                    bold=True
                )
                btn_del.bind(on_press=lambda instance, it=item: self.confirmar_eliminar(it))
                row.add_widget(btn_del)

                self.hist_list.add_widget(row)

        # Limpieza del pending y detener animación
        self._pending_grupos = None
        self._stop_loading_animation()

        # Actualizar estadísticas y labels
        app = App.get_running_app()
        historial = getattr(app.datos, self.data_attr, [])
        try:
            stats = motor_matematico.generar_estadisticas_pecados(historial)
        except Exception:
            stats = {'total': 0.0, 'mensuales': {}}

        total = stats.get('total', 0.0)
        title_color_map = {
            'pecado': (1, 0, 0, 1),
            'regalo': (0, 1, 0, 1),
            'gasto': (1, 0.5, 0, 1)
        }
        label_color = title_color_map.get(self.mode, self.color_header)

        self.total_label.text = self.total_label_template.format(total)
        self.total_label.color = label_color

        txt_meses = "POR MES:\n"
        for mes, monto in stats.get('mensuales', {}).items():
            txt_meses += f"{mes}: ${monto:.2f}  |  "
        self.mes_label.text = txt_meses

    def on_enter(self):
        app = App.get_running_app()

        # Mostrar animación de carga
        self._start_loading_animation()

        # Limpiar lista (si había contenido previo)
        self.hist_list.clear_widgets()

        historial = getattr(app.datos, self.data_attr, [])

        def get_date_key(item):
            fecha = item.get('fecha', '2000-01-01')
            try:
                return datetime.datetime.strptime(fecha, "%Y-%m-%d")
            except:
                return datetime.datetime(2000, 1, 1)

        historial_sorted = sorted(historial, key=get_date_key, reverse=True)

        grupos = defaultdict(list)
        for item in historial_sorted:
            fecha = item.get('fecha', 'S/F')
            grupos[fecha].append(item)

        # Guardamos los grupos y programamos la construcción en la siguiente iteración del loop
        # Esto permite que la animación (Clock) se ejecute mientras se construyen los widgets.
        self._pending_grupos = grupos
        Clock.schedule_once(self._build_hist_widgets, 0)

    def on_leave(self):
        # Asegurar que la animación se detenga si el usuario sale de la pantalla antes de que termine
        if self._loading_event is not None:
            self._loading_event.cancel()
            self._loading_event = None

    def confirmar_eliminar(self, item):
        def do_delete(instance):
            app = App.get_running_app()
            historial = getattr(app.datos, self.data_attr, [])
            if item in historial:
                historial.remove(item)
                precio = item.get('precio', 0.0) if 'precio' in item else item.get('monto', 0.0)

                # Ajustes por modo
                if self.mode == 'pecado':
                    app.datos.gasto_acumulado = max(0.0, getattr(app.datos, 'gasto_acumulado', 0.0) - precio)
                elif self.mode == 'regalo':
                    app.datos.ingresos_acumulados = max(0.0, getattr(app.datos, 'ingresos_acumulados', 0.0) - precio)
                    app.datos.ingresos_extra = app.datos.ingresos_acumulados + getattr(app.datos, 'ingresos_hoy', 0.0)
                elif self.mode == 'gasto':
                    app.datos.gasto_necesario_acumulado = max(0.0, getattr(app.datos, 'gasto_necesario_acumulado', 0.0) - precio)

                try:
                    app.datos.save_data()
                except Exception:
                    pass

                popup.dismiss()
                # reconstruir la pantalla
                self.on_enter()

        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        content.add_widget(Label(
            text=f"¿Estás seguro de borrar\n'{item.get('nombre', 'este item')}' del historial?",
            halign='center', valign='middle'
        ))

        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        si = Button(text="SÍ, BORRAR", background_color=(1, 0, 0, 1), bold=True)
        si.bind(on_press=do_delete)
        no = Button(text="CANCELAR", background_color=(0, 0.6, 1, 1), bold=True)
        no.bind(on_press=lambda x: popup.dismiss())

        btn_box.add_widget(si)
        btn_box.add_widget(no)
        content.add_widget(btn_box)

        popup = Popup(title="Confirmar eliminación", content=content, size_hint=(0.85, 0.4))
        popup.open()