# ui_grafica_render.py
# ui_grafica_render.py
import math
import datetime

from kivy.graphics import Line, Color, Ellipse, Rectangle, StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
import mat.mat_geometria as mat_geometria
def draw_full(widget, padding_ejes, w_util, h_util):
    """
    Dibuja todo en el canvas del widget recibido.
    Recibe el widget (GraficaInteractiva) y parámetros calculados por el core.
    No modifica el estado del widget salvo añadir elementos gráficos.
    """
    canvas = widget.canvas
    canvas.clear()
    widget.coordenadas_click = []

    # Validación rápida
    if widget.view_x_max <= widget.view_x_min or widget.view_y_max <= widget.view_y_min:
        return

    with canvas:
        # Fondo
        Color(0.08, 0.08, 0.08, 1)
        Rectangle(pos=widget.pos, size=widget.size)

        # === EJE Y ===
        rango_y = widget.view_y_max - widget.view_y_min
        paso_y = mat_geometria.calcular_paso_optimo(rango_y, max_lineas=6)

        # --- Evitar demasiados ticks en Y: limitar por resolución de píxeles ---
        # Máximo número de ticks razonables según altura útil y separación mínima en píxeles
        min_pixel_sep = dp(20)  # separación mínima entre etiquetas en píxeles
        max_ticks = max(2, int(h_util / min_pixel_sep))
        # Asegurar que paso_y no sea más pequeño que el que produciría max_ticks
        paso_y_min_por_pixels = rango_y / float(max_ticks)
        if paso_y < paso_y_min_por_pixels:
            paso_y = paso_y_min_por_pixels

        # Alinear el primer tick de Y al múltiplo superior de paso_y dentro de la vista
        # Usamos ceil para que el primer tick esté dentro de la vista y sea múltiplo de paso_y
        try:
            y_actual = math.ceil(widget.view_y_min / paso_y) * paso_y
        except Exception:
            y_actual = math.floor(widget.view_y_min / paso_y) * paso_y

        # Determinar número de decimales a mostrar según el tamaño del paso
        if paso_y >= 1:
            formato_decimales = 0
        else:
            # calcular cuántos decimales son necesarios (ej: paso_y=0.01 -> 2 decimales)
            formato_decimales = max(0, -int(math.floor(math.log10(paso_y))) )
            # limitar decimales razonables
            formato_decimales = min(formato_decimales, 6)

        while y_actual <= widget.view_y_max + 1e-12:
            y_px = widget.y + padding_ejes + mat_geometria.mapear_valor(
                y_actual, widget.view_y_min, widget.view_y_max, 0, h_util
            )
            if widget.y + padding_ejes <= y_px <= widget.top:
                Color(0.2, 0.2, 0.2, 1)
                Line(points=[widget.x + padding_ejes, y_px, widget.right, y_px], width=1)

                if formato_decimales == 0:
                    texto = f"${int(round(y_actual))}"
                else:
                    texto = f"${y_actual:.{formato_decimales}f}"

                lbl = CoreLabel(text=texto, font_size=dp(11), color=(0.7, 0.7, 0.7, 1))
                lbl.refresh()
                tex = lbl.texture
                Color(1, 1, 1, 1)
                Rectangle(texture=tex, pos=(widget.x + dp(5), y_px - (tex.size[1]/2)), size=tex.size)
            y_actual += paso_y

        # === EJE X ===
        rango_x = widget.view_x_max - widget.view_x_min
        paso_x = mat_geometria.calcular_paso_optimo(rango_x, max_lineas=4)
        paso_x = max(86400, math.floor(paso_x / 86400) * 86400)

        # --- Ancla estable para la rejilla X: usar el inicio del mundo (world_x_min) alineado a medianoche ---
        # Esto evita que la cuadrícula "salte" cuando view_x_min cambia ligeramente.
        try:
            # Anchor: midnight of world_x_min (stable reference independent of view_x_min)
            anchor_midnight = datetime.datetime.fromtimestamp(widget.world_x_min).replace(
                hour=0, minute=0, second=0, microsecond=0
            ).timestamp()
            # Si anchor_midnight is after world_x_min, step back one day
            if anchor_midnight > widget.world_x_min:
                anchor_midnight -= 86400
            # Compute the first tick >= view_x_min using the anchor as origin
            offset = widget.view_x_min - anchor_midnight
            # number of whole steps from anchor to the first tick at or before view_x_min
            n = math.floor(offset / paso_x)
            x_actual = anchor_midnight + n * paso_x
            # Ensure x_actual is <= view_x_min; if it's greater, step back one
            if x_actual > widget.view_x_min:
                x_actual -= paso_x
        except Exception:
            # Fallback al comportamiento anterior si algo falla
            x_actual = math.floor(widget.view_x_min / paso_x) * paso_x

        while x_actual <= widget.view_x_max:
            if x_actual < widget.world_x_min:
                x_actual += paso_x
                continue
            if x_actual > widget.world_x_max:
                break

            x_px = widget.x + padding_ejes + mat_geometria.mapear_valor(
                x_actual, widget.view_x_min, widget.view_x_max, 0, w_util
            )

            if widget.x + padding_ejes <= x_px <= widget.right:
                Color(0.2, 0.2, 0.2, 1)
                Line(points=[x_px, widget.y + padding_ejes, x_px, widget.top], width=1)

                dt = datetime.datetime.fromtimestamp(x_actual)
                if rango_x > 86400 * 365:
                    texto = dt.strftime("%Y")
                else:
                    texto = dt.strftime("%b %d")

                lbl = CoreLabel(text=texto, font_size=dp(11), color=(0.7, 0.7, 0.7, 1))
                lbl.refresh()
                tex = lbl.texture
                Color(1, 1, 1, 1)
                Rectangle(texture=tex, pos=(x_px - (tex.size[0]/2), widget.y + dp(10)), size=tex.size)
            x_actual += paso_x

        # === MARCO L ===
        Color(0.6, 0.6, 0.6, 1)
        Line(points=[widget.x + padding_ejes, widget.y + padding_ejes, widget.right, widget.y + padding_ejes], width=dp(1.5))
        Line(points=[widget.x + padding_ejes, widget.y + padding_ejes, widget.x + padding_ejes, widget.top], width=dp(1.5))

        # === LÍNEA HISTORIAL ===
        punto_anterior = None

        def punto_en_bounds(xp, yp):
            return (widget.x - dp(50) <= xp <= widget.right + dp(50)) and (widget.y - dp(50) <= yp <= widget.top + dp(50))

        # Visible plotting rectangle (estricto, sin márgenes)
        visible_left = widget.x + padding_ejes
        visible_right = widget.right
        visible_bottom = widget.y + padding_ejes
        visible_top = widget.top

        # --- Cambio mínimo y seguro: usar STENCIL para recortar la línea al interior del plano ---
        overlap = dp(0)  # ajuste exacto al borde
        StencilPush()
        Color(0, 0, 0, 0)
        Rectangle(pos=(visible_left - overlap, visible_bottom - overlap),
                  size=((visible_right - visible_left) + overlap * 2, (visible_top - visible_bottom) + overlap * 2))
        StencilUse()

        for dia in widget.linea_tiempo:
            try:
                dt = datetime.datetime.strptime(dia['fecha'], "%Y-%m-%d")
                ts = dt.timestamp()
            except Exception:
                continue

            # Filtrado: no procesar puntos fuera de los límites X definidos por el core
            if ts < widget.world_x_min:
                continue
            if widget._fecha_limite_ts is not None:
                if ts >= widget._fecha_limite_ts:
                    continue
            else:
                if widget._ultimo_ts is not None and ts > widget._ultimo_ts:
                    continue

            x_px = widget.x + padding_ejes + mat_geometria.mapear_valor(
                ts, widget.view_x_min, widget.view_x_max, 0, w_util
            )
            y_px = widget.y + padding_ejes + mat_geometria.mapear_valor(
                float(dia.get('saldo', 0.0)), widget.view_y_min, widget.view_y_max, 0, h_util
            )

            # Guardar coordenadas para detección de clicks (interacción intacta)
            widget.coordenadas_click.append({'x': x_px, 'y': y_px, 'data': dia})

            if punto_anterior:
                if dia.get('saldo', 0.0) >= punto_anterior['data'].get('saldo', 0.0):
                    Color(0.1, 0.9, 0.3, 1)
                else:
                    Color(1.0, 0.2, 0.2, 1)
                Line(points=[punto_anterior['x'], punto_anterior['y'], x_px, y_px], width=dp(2))

            # Nota: NO dibujamos los nodos aquí. Los nodos se dibujan después del stencil
            # según la lógica de zoom para evitar amontonamiento.

            punto_anterior = {'x': x_px, 'y': y_px, 'data': dia}

        # Desactivar stencil
        StencilUnUse()
        StencilPop()

        # (Los ejes, ticks, etiquetas y marco ya se dibujaron antes y siguen visibles)
        # Si quieres que los nodos solo se dibujen estrictamente dentro del rectángulo,
        # reemplaza punto_en_bounds por la comprobación visible_left/visible_right/visible_bottom/visible_top.

        # --- DIBUJO CONDICIONAL DE NODOS SEGÚN ZOOM ---
        # Calculamos la distancia mínima en píxeles entre puntos consecutivos en X.
        # Si los puntos están demasiado juntos (zoom muy alejado), ocultamos los nodos.
        min_dx = None
        prev_x = None
        # Aseguramos que las coordenadas estén ordenadas por X para medir distancias correctas
        coords_sorted = sorted(widget.coordenadas_click, key=lambda p: p['x'])
        for pt in coords_sorted:
            x_px = pt['x']
            if prev_x is not None:
                dx = abs(x_px - prev_x)
                if min_dx is None or dx < min_dx:
                    min_dx = dx
            prev_x = x_px

        # Umbral en píxeles: si la distancia mínima entre puntos es menor que esto,
        # consideramos que la vista está demasiado alejada y ocultamos los nodos.
        umbral_nodos = dp(12)

        # Decisión: mostrar nodos solo si min_dx es None (pocos puntos) o >= umbral
        mostrar_nodos = (min_dx is None) or (min_dx >= umbral_nodos)

        # Dibujar nodos solo si mostrar_nodos es True
        if mostrar_nodos:
            for pt in widget.coordenadas_click:
                x_px = pt['x']
                y_px = pt['y']
                if (visible_left <= x_px <= visible_right) and (visible_bottom <= y_px <= visible_top):
                    Color(1, 1, 1, 1)
                    Ellipse(pos=(x_px - dp(4), y_px - dp(4)), size=(dp(8), dp(8)))