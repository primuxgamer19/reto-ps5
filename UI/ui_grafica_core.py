# ui_grafica_core.py
# ui_grafica_core.py
import math
import datetime

from kivy.uix.widget import Widget
from kivy.metrics import dp
import mat.mat_geometria as mat_geometria
import mat.mat_historia as mat_historia
# Controlador de gestos táctiles (módulo separado)
from .touch_controls import TouchController

# Popups y widgets reutilizables
from .ui_widgets import InfoPopup

# Config UI centralizada
from .ui_config import DEFAULT_PADDING, DEFAULT_VIEW_SPAN_DAYS, DEFAULT_VIEW_Y_PADDING

class GraficaInteractiva(Widget):
    """
    Motor de renderizado: estado y control.
    Esta versión mantiene exactamente las mismas firmas y atributos que antes.
    El dibujo se delega a ui_grafica_render.draw_full para mantener el archivo pequeño.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.linea_tiempo = []
        self.productos = []
        self.fecha_limite = ""
        
        # Estado de la cámara (Lo que se ve actualmente)
        self.view_x_min = 0
        self.view_x_max = 1
        self.view_y_min = 0
        self.view_y_max = 1
        
        # Límites del mundo (Lo que existe en total)
        self.world_x_min = 0
        self.world_x_max = 1
        self.world_y_min = 0
        self.world_y_max = 1

        # Controlador de gestos táctiles (módulo separado)
        self.touch_controller = TouchController(self)

        # Estado auxiliar para clicks y nodos
        self.coordenadas_click = []
        
        # Timestamps auxiliares
        self._ultimo_ts = None
        self._fecha_limite_ts = None
        self._primera_ts = None

        # Flags de vista
        self.view_focused = False
        self.reset_view_requested = False
        
        # Valores por defecto configurables
        self.default_view_span_days = DEFAULT_VIEW_SPAN_DAYS
        self.default_view_y_padding = DEFAULT_VIEW_Y_PADDING

        # Cada vez que la pantalla cambia de tamaño o de posición, redibujamos
        self.bind(pos=self.actualizar_render, size=self.actualizar_render)

    def set_datos(self, linea_tiempo, productos, fecha_limite):
        self.linea_tiempo = linea_tiempo
        self.productos = productos
        self.fecha_limite = fecha_limite
        
        # Extraer límites del mundo a partir del JSON
        wx_min, wx_max, wy_min, wy_max = mat_geometria.calcular_limites(
            self.linea_tiempo, self.productos, self.fecha_limite
        )
        
        # Inicialmente usar lo que devuelve la geometría
        self.world_x_min = wx_min

        # --- Calcular timestamp de la fecha límite si existe ---
        self._fecha_limite_ts = None
        try:
            if self.fecha_limite:
                try:
                    dt_lim = datetime.datetime.strptime(self.fecha_limite, "%Y-%m-%d")
                    self._fecha_limite_ts = dt_lim.timestamp()
                except Exception:
                    self._fecha_limite_ts = None
        except Exception:
            self._fecha_limite_ts = None

        # --- Calcular el timestamp del último registro real y del primero en linea_tiempo ---
        ultimo_ts = None
        primera_ts = None
        try:
            for dia in self.linea_tiempo:
                try:
                    dt = datetime.datetime.strptime(dia.get('fecha', ''), "%Y-%m-%d")
                    ts = dt.timestamp()
                    if ultimo_ts is None or ts > ultimo_ts:
                        ultimo_ts = ts
                    if primera_ts is None or ts < primera_ts:
                        primera_ts = ts
                except Exception:
                    continue
        except Exception:
            ultimo_ts = None
            primera_ts = None

        # Guardar los timestamps calculados para uso en renderizado
        self._ultimo_ts = ultimo_ts
        self._primera_ts = primera_ts

        # --- Establecer world_x_min: no mostrar fechas anteriores al primer registro real ---
        if self._primera_ts is not None:
            self.world_x_min = self._primera_ts
        else:
            self.world_x_min = wx_min

        # --- Establecer world_x_max: mantener la fecha límite como tope si es válida ---
        if self._fecha_limite_ts is not None:
            self.world_x_max = self._fecha_limite_ts
        else:
            if ultimo_ts is not None:
                self.world_x_max = ultimo_ts + 86400
            else:
                self.world_x_max = wx_max + 86400

        self.world_y_min = wy_min
        self.world_y_max = wy_max * 1.1
        
        # Asegurar world_y_max > world_y_min
        if self.world_y_max <= self.world_y_min:
            self.world_y_max = self.world_y_min + 1.0
        
        # Reiniciar la cámara para ver todo el panorama
        self.view_x_min = self.world_x_min
        self.view_x_max = self.world_x_max
        self.view_y_min = self.world_y_min
        self.view_y_max = self.world_y_max

        # Resetear flag de enfoque para que la primera renderización pueda auto-enfocar
        self.view_focused = False
        self.reset_view_requested = False
        
        self.actualizar_render()

    # ---------- Eventos táctiles: delegar al TouchController ----------
    def on_touch_down(self, touch):
        if self.touch_controller.touch_down(touch):
            if len(self.touch_controller._touches) == 1 and not touch.is_double_tap:
                self.verificar_click_punto(touch)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.touch_controller.touch_move(touch):
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.touch_controller.touch_up(touch):
            return True
        return super().on_touch_up(touch)

    def aplicar_restricciones_fisicas(self):
        """
        Mantiene límites y restricciones de zoom/pan.
        Se preservaron las mismas variables y firmas que en la versión anterior.
        """
        rango_x = self.view_x_max - self.view_x_min
        rango_y = self.view_y_max - self.view_y_min
        mundo_x_rango = max(self.world_x_max - self.world_x_min, 1.0)
        mundo_y_rango = max(self.world_y_max - self.world_y_min, 1.0)
        
        # Limitar Zoom Out en X: No alejar más del doble del tamaño del mundo
        if rango_x > mundo_x_rango * 2:
            centro_x = self.view_x_min + (rango_x / 2)
            self.view_x_min = centro_x - mundo_x_rango
            self.view_x_max = centro_x + mundo_x_rango
            
        # Limitar Zoom Out en Y: No alejar más del doble del tamaño del mundo vertical
        if rango_y > mundo_y_rango * 2:
            centro_y = self.view_y_min + (rango_y / 2)
            self.view_y_min = centro_y - mundo_y_rango
            self.view_y_max = centro_y + mundo_y_rango

        # Limitar Zoom In en X: No acercar más de 12 horas en el eje de fechas (X)
        if rango_x < 43200:
            centro = self.view_x_min + (rango_x / 2)
            self.view_x_min = centro - 21600
            self.view_x_max = centro + 21600

        # Ajuste solicitado: permitir acercamiento vertical fino (centavos)
        min_rango_y = 0.01
        min_rango_y = max(min_rango_y, (self.world_y_max - self.world_y_min) / 100000.0)

        if rango_y < min_rango_y:
            centro_y = self.view_y_min + (rango_y / 2)
            self.view_y_min = centro_y - (min_rango_y / 2)
            self.view_y_max = centro_y + (min_rango_y / 2)

        # Evitar salirse del mundo en X (ajuste estricto)
        if self.view_x_min < self.world_x_min:
            shift = self.world_x_min - self.view_x_min
            self.view_x_min += shift
            self.view_x_max += shift
        if self.view_x_max > self.world_x_max:
            shift = self.view_x_max - self.world_x_max
            self.view_x_min -= shift
            self.view_x_max -= shift

        # Evitar salirse del mundo en Y (con márgenes)
        if self.view_y_min < self.world_y_min:
            shift = self.world_y_min - self.view_y_min
            self.view_y_min += shift
            self.view_y_max += shift
        if self.view_y_max > self.world_y_max:
            shift = self.view_y_max - self.world_y_max
            self.view_y_min -= shift
            self.view_y_max -= shift

        # Asegurar que no se muestren valores negativos absurdos si el mundo empieza en 0
        if self.world_y_min >= 0:
            if self.view_y_min < 0:
                shift = -self.view_y_min
                self.view_y_min += shift
                self.view_y_max += shift
                if self.view_y_max > self.world_y_max:
                    self.view_y_max = self.world_y_max
                    self.view_y_min = max(self.world_y_min, self.view_y_max - max(mundo_y_rango * 2, min_rango_y))

        # Refuerzo final: clamps estrictos para X y Y
        if self.view_x_min < self.world_x_min:
            self.view_x_min = self.world_x_min
        if self.view_x_max > self.world_x_max:
            self.view_x_max = self.world_x_max

        if self.view_x_max - self.view_x_min > mundo_x_rango * 2:
            desired = mundo_x_rango * 2
            centro = (self.view_x_min + self.view_x_max) / 2.0
            self.view_x_min = max(self.world_x_min, centro - desired / 2.0)
            self.view_x_max = min(self.world_x_max, centro + desired / 2.0)
            if self.view_x_min < self.world_x_min:
                self.view_x_min = self.world_x_min
                self.view_x_max = self.world_x_min + desired
            if self.view_x_max > self.world_x_max:
                self.view_x_max = self.world_x_max
                self.view_x_min = self.world_x_max - desired

        if self.view_y_min < self.world_y_min:
            self.view_y_min = self.world_y_min
        if self.view_y_max > self.world_y_max:
            self.view_y_max = self.world_y_max

        if (self.view_y_max - self.view_y_min) < min_rango_y:
            centro_y = (self.view_y_min + self.view_y_max) / 2.0
            self.view_y_min = centro_y - (min_rango_y / 2.0)
            self.view_y_max = centro_y + (min_rango_y / 2.0)
            if self.view_y_min < self.world_y_min:
                self.view_y_min = self.world_y_min
                self.view_y_max = self.world_y_min + min_rango_y
            if self.view_y_max > self.world_y_max:
                self.view_y_max = self.world_y_max
                self.view_y_min = self.world_y_max - min_rango_y

    def reset_view_to_default(self, span_days=None, y_padding_percent=None):
        """
        Ajusta view_x_min/view_x_max y view_y_min/view_y_max del widget a valores por defecto.
        - span_days: número de días a mostrar en X (si None usa self.default_view_span_days).
        - y_padding_percent: padding relativo para eje Y (si None usa self.default_view_y_padding).
        - Marca self.view_focused = True para que el auto-focus no sobrescriba la vista.
        - Si no hay datos válidos, no modifica la vista.
        """
        if not getattr(self, 'linea_tiempo', None):
            return

        span_days = span_days if span_days is not None else self.default_view_span_days
        y_padding_percent = y_padding_percent if y_padding_percent is not None else self.default_view_y_padding

        max_ts_real = None
        saldos = []

        for d in self.linea_tiempo:
            fecha_raw = d.get('fecha')
            if not fecha_raw:
                continue
            try:
                dt = datetime.datetime.strptime(fecha_raw, "%Y-%m-%d")
                ts = dt.timestamp()
            except Exception:
                continue

            detalles = d.get('detalles', [])
            es_meta = any(isinstance(t, str) and 'META / FECHA LÍMITE' in t for t in detalles)
            if not es_meta:
                if max_ts_real is None or ts > max_ts_real:
                    max_ts_real = ts
                try:
                    saldos.append(float(d.get('saldo', 0.0)))
                except Exception:
                    saldos.append(0.0)

        # Si no hay datos reales, intentar usar cualquier timestamp (incluye meta)
        if max_ts_real is None:
            for d in self.linea_tiempo:
                fecha_raw = d.get('fecha')
                if not fecha_raw:
                    continue
                try:
                    dt = datetime.datetime.strptime(fecha_raw, "%Y-%m-%d")
                    ts = dt.timestamp()
                except Exception:
                    continue
                if max_ts_real is None or ts > max_ts_real:
                    max_ts_real = ts

        if max_ts_real is None:
            return

        span_seconds = float(span_days) * 86400.0
        try:
            self.view_x_max = max_ts_real
            self.view_x_min = max_ts_real - span_seconds
        except Exception:
            pass

        # Ajuste Y si hay saldos reales
        if saldos:
            min_saldo = min(saldos)
            max_saldo = max(saldos)
            rango_saldo = max_saldo - min_saldo
            if rango_saldo <= 0:
                padding = max(1.0, abs(max_saldo) * y_padding_percent)
            else:
                padding = rango_saldo * y_padding_percent
            new_view_y_min = min_saldo - padding
            new_view_y_max = max_saldo + padding
            if new_view_y_max <= new_view_y_min:
                new_view_y_max = new_view_y_min + max(1.0, abs(new_view_y_min) * y_padding_percent)
            try:
                self.view_y_min = new_view_y_min
                self.view_y_max = new_view_y_max
            except Exception:
                pass

        # Marcar que la vista fue restablecida para evitar que el auto-focus la sobrescriba
        try:
            self.view_focused = True
        except Exception:
            pass

        # Limpiar flag de reset si estaba puesto
        try:
            if getattr(self, 'reset_view_requested', False):
                self.reset_view_requested = False
        except Exception:
            pass

    def actualizar_render(self, *args):
        """
        Calcula parámetros y delega el dibujo a ui_grafica_render.draw_full.
        Mantiene la misma semántica que la versión anterior.
        """
        # Importar aquí para evitar ciclos en tiempo de importación
        from .ui_grafica_render import draw_full

        padding_ejes = DEFAULT_PADDING
        w_util = max(self.width - padding_ejes, 1)
        h_util = max(self.height - padding_ejes, 1)

        # Aplicar restricciones antes de dibujar
        try:
            self.aplicar_restricciones_fisicas()
        except Exception:
            # En caso de fallo, no bloquear el renderizado; seguir con valores actuales
            pass

        # Delegar todo el trabajo de dibujo al módulo render
        draw_full(self, padding_ejes, w_util, h_util)

    def verificar_click_punto(self, touch):
        """Detecta si tocaste un nodo financiero"""
        for pt in self.coordenadas_click:
            distancia = math.hypot(pt['x'] - touch.x, pt['y'] - touch.y)
            if distancia < dp(25):
                self.mostrar_detalle(pt['data'])
                return

    def _on_popup_dismiss_restore_touches(self, *args):
        """Restaurar/limpiar estado del touch controller al cerrar popup."""
        try:
            self.touch_controller.reset_state()
        except Exception:
            self.touch_controller._touches = []
            self.touch_controller._touch_positions = {}
            self.touch_controller._last_dist = None

    def mostrar_detalle(self, data):
        detalles_texto = "\n".join(data.get('detalles', [])) if data.get('detalles') else "Sin movimientos."
        mensaje = f"Fecha: {data.get('fecha', '')}\nSaldo acumulado: ${float(data.get('saldo', 0.0)):.2f}\n\nDetalles:\n{detalles_texto}"
        
        try:
            self.touch_controller.reset_state()
        except Exception:
            self.touch_controller._touches = []
            self.touch_controller._touch_positions = {}
            self.touch_controller._last_dist = None

        popup = InfoPopup(mensaje, title="Historial del Día")
        popup.bind(on_dismiss=self._on_popup_dismiss_restore_touches)
        popup.open()