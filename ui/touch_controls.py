# touch_controls.py
import math
from kivy.metrics import dp
from ui.ui_config import DEFAULT_PADDING

class TouchController:
    """
    Controlador independiente de gestos táctiles.
    - Diseñado para integrarse con cualquier widget que exponga:
      width, height, x, y, top, right, view_x_min, view_x_max, view_y_min, view_y_max,
      world_x_min, world_x_max, world_y_min, world_y_max, actualizar_render(), aplicar_restricciones_fisicas()
    - Provee manejo de:
      * Un dedo: paneo (arrastrar en X e Y)
      * Dos dedos: pinch-to-zoom centrado en el punto medio; también paneo si ambos dedos se mueven juntos
    - No depende de main.py ni de la app; es un módulo reutilizable.
    """

    def __init__(self, owner_widget):
        """
        owner_widget: referencia al widget que contiene la cámara y las propiedades de vista.
        Debe implementar actualizar_render() y aplicar_restricciones_fisicas().
        """
        self.owner = owner_widget
        self._touches = []
        self._touch_positions = {}   # map touch.uid -> (x, y)
        self._last_dist = None

    # ---------- Utilidades públicas ----------
    def reset_state(self):
        """Limpia todo el estado interno del controlador de toques."""
        self._touches.clear()
        self._touch_positions.clear()
        self._last_dist = None

    # ---------- Integración con eventos de Kivy ----------
    def touch_down(self, touch):
        """Llamar desde on_touch_down del widget"""
        if not self.owner.collide_point(*touch.pos):
            return False

        if touch not in self._touches:
            self._touches.append(touch)
            try:
                uid = touch.uid
            except AttributeError:
                uid = id(touch)
            self._touch_positions[uid] = (touch.x, touch.y)

        # Si hay dos toques, inicializar distancia de referencia
        if len(self._touches) == 2:
            t1, t2 = self._touches[0], self._touches[1]
            self._last_dist = math.hypot(t1.x - t2.x, t1.y - t2.y)

        return True

    def touch_move(self, touch):
        """Llamar desde on_touch_move del widget"""
        if touch not in self._touches:
            return False

        n = len(self._touches)

        # --- Un dedo: paneo en X e Y ---
        if n == 1:
            rango_x = self.owner.view_x_max - self.owner.view_x_min
            rango_y = self.owner.view_y_max - self.owner.view_y_min

            # Convertir píxeles a unidades del mundo
            dx_world = (touch.dx / float(self.owner.width)) * rango_x
            dy_world = (touch.dy / float(self.owner.height)) * rango_y

            # Aplicar desplazamiento (arrastrar mueve la vista en la misma dirección del dedo)
            self.owner.view_x_min -= dx_world
            self.owner.view_x_max -= dx_world
            self.owner.view_y_min -= dy_world
            self.owner.view_y_max -= dy_world

            # Actualizar referencia de posición
            try:
                uid = touch.uid
            except AttributeError:
                uid = id(touch)
            self._touch_positions[uid] = (touch.x, touch.y)

            # Aplicar restricciones y redibujar
            self.owner.aplicar_restricciones_fisicas()
            self.owner.actualizar_render()
            return True

        # --- Dos dedos: pinch-to-zoom centrado + paneo medio ---
        elif n == 2:
            t1, t2 = self._touches[0], self._touches[1]

            try:
                uid1 = t1.uid
            except AttributeError:
                uid1 = id(t1)
            try:
                uid2 = t2.uid
            except AttributeError:
                uid2 = id(t2)

            prev1 = self._touch_positions.get(uid1, (t1.x - t1.dx, t1.y - t1.dy))
            prev2 = self._touch_positions.get(uid2, (t2.x - t2.dx, t2.y - t2.dy))

            prev_dist = math.hypot(prev1[0] - prev2[0], prev1[1] - prev2[1])
            curr_dist = math.hypot(t1.x - t2.x, t1.y - t2.y)

            if prev_dist == 0:
                prev_dist = 0.0001
            if curr_dist == 0:
                curr_dist = 0.0001

            escala = prev_dist / curr_dist

            rango_x = self.owner.view_x_max - self.owner.view_x_min
            rango_y = self.owner.view_y_max - self.owner.view_y_min

            # Punto medio en pantalla
            mid_x = (t1.x + t2.x) / 2.0
            mid_y = (t1.y + t2.y) / 2.0

            # Mapear pantalla -> mundo (inverso de mapear_valor)
            padding_ejes = DEFAULT_PADDING
            w_util = max(self.owner.width - padding_ejes, 1)
            h_util = max(self.owner.height - padding_ejes, 1)

            rel_x = (mid_x - (self.owner.x + padding_ejes)) / float(w_util)
            rel_y = (mid_y - (self.owner.y + padding_ejes)) / float(h_util)
            rel_x = min(max(rel_x, 0.0), 1.0)
            rel_y = min(max(rel_y, 0.0), 1.0)

            world_mid_x = self.owner.view_x_min + rel_x * rango_x
            world_mid_y = self.owner.view_y_min + rel_y * rango_y

            nuevo_rango_x = rango_x * escala
            nuevo_rango_y = rango_y * escala

            # Límites razonables para evitar zoom extremo
            min_rango_x = 1.0
            max_rango_x = max((self.owner.world_x_max - self.owner.world_x_min) * 10.0, min_rango_x)
            nuevo_rango_x = min(max(nuevo_rango_x, min_rango_x), max_rango_x)

            min_rango_y = 0.01
            max_rango_y = max((self.owner.world_y_max - self.owner.world_y_min) * 10.0, min_rango_y)
            nuevo_rango_y = min(max(nuevo_rango_y, min_rango_y), max_rango_y)

            # Recalcular vista centrada en world_mid
            self.owner.view_x_min = world_mid_x - nuevo_rango_x * rel_x
            self.owner.view_x_max = self.owner.view_x_min + nuevo_rango_x
            self.owner.view_y_min = world_mid_y - nuevo_rango_y * rel_y
            self.owner.view_y_max = self.owner.view_y_min + nuevo_rango_y

            # Paneo medio si ambos dedos se mueven juntos
            move_x_prev = (prev1[0] + prev2[0]) / 2.0
            move_y_prev = (prev1[1] + prev2[1]) / 2.0
            move_x_curr = (t1.x + t2.x) / 2.0
            move_y_curr = (t1.y + t2.y) / 2.0
            delta_px_x = move_x_curr - move_x_prev
            delta_px_y = move_y_curr - move_y_prev

            dx_world = (delta_px_x / float(self.owner.width)) * nuevo_rango_x
            dy_world = (delta_px_y / float(self.owner.height)) * nuevo_rango_y

            self.owner.view_x_min -= dx_world
            self.owner.view_x_max -= dx_world
            self.owner.view_y_min -= dy_world
            self.owner.view_y_max -= dy_world

            # Guardar posiciones actuales
            self._touch_positions[uid1] = (t1.x, t1.y)
            self._touch_positions[uid2] = (t2.x, t2.y)
            self._last_dist = curr_dist

            self.owner.aplicar_restricciones_fisicas()
            self.owner.actualizar_render()
            return True

        return False

    def touch_up(self, touch):
        """Llamar desde on_touch_up del widget"""
        if touch not in self._touches:
            return False

        try:
            uid = touch.uid
        except AttributeError:
            uid = id(touch)
        if uid in self._touch_positions:
            del self._touch_positions[uid]

        self._touches.remove(touch)

        if not self._touches:
            self._last_dist = None
            self._touch_positions.clear()
        else:
            # Si queda 1 toque, actualizar su referencia
            if len(self._touches) == 1:
                remaining = self._touches[0]
                try:
                    uidr = remaining.uid
                except AttributeError:
                    uidr = id(remaining)
                self._touch_positions[uidr] = (remaining.x, remaining.y)

        return True