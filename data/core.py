# core.py
# Lógica central de MotorDatos: defaults, eventos diarios y helpers

import datetime
from typing import List, Dict, Any

class MotorDatosCore:
    def __init__(self):
        # Campos principales inicializados por el wrapper
        self.productos: List[Dict[str, Any]] = []
        self.ahorrado_guardado = ""
        self.fecha_limite = ""
        self.last_notif_date = ""
        self.is_first_run = True

        self.salario = 0.0
        self.arriendo = 0.0

        self.gasto_hoy = 0.0
        self.fecha_gasto = ""
        self.fecha_salario = ""
        self.gasto_acumulado = 0.0
        self.pecados_hoy: List[Dict[str, Any]] = []
        self.historial_pecados: List[Dict[str, Any]] = []

        self.regalos_hoy: List[Dict[str, Any]] = []
        self.historial_regalos: List[Dict[str, Any]] = []
        self.fecha_regalo = ""
        self.ingresos_acumulados = 0.0
        self.ingresos_hoy = 0.0
        self.ingresos_extra = 0.0

        self.gastos_fijos: List[Dict[str, Any]] = []
        self.gastos_necesarios_hoy: List[Dict[str, Any]] = []
        self.fecha_gasto_necesario = ""
        self.gasto_necesario_acumulado = 0.0
        self.historial_gastos_necesarios: List[Dict[str, Any]] = []

        self.last_regalos_notif_date = ""
        self.last_regalos_notif_sum = 0.0
        self.last_regalos_notif_count = 0

    def set_defaults(self):
        self.productos = [
            {'nombre': 'PS5 Slim', 'precio': 550.0},
            {'nombre': 'Regulador', 'precio': 60.0},
            {'nombre': 'Monitor 1080p', 'precio': 280.0},
            {'nombre': 'GTA 6', 'precio': 150.0}
        ]
        self.ahorrado_guardado = ""
        self.fecha_limite = "2026-11-19"
        self.last_notif_date = ""
        self.is_first_run = True

        self.salario = 0.0
        self.arriendo = 0.0

        self.gasto_hoy = 0.0
        self.fecha_gasto = ""
        self.fecha_salario = ""
        self.gasto_acumulado = 0.0
        self.pecados_hoy = []
        self.historial_pecados = []

        self.regalos_hoy = []
        self.historial_regalos = []
        self.fecha_regalo = ""
        self.ingresos_acumulados = 0.0
        self.ingresos_hoy = 0.0
        self.ingresos_extra = 0.0

        self.gastos_fijos = []
        self.gastos_necesarios_hoy = []
        self.fecha_gasto_necesario = ""
        self.gasto_necesario_acumulado = 0.0
        self.historial_gastos_necesarios = []

        self.last_regalos_notif_date = ""
        self.last_regalos_notif_sum = 0.0
        self.last_regalos_notif_count = 0

    def procesar_eventos_diarios(self) -> bool:
        """
        Mueve registros diarios a historial si cambió el día.
        Devuelve True si se debe mostrar popup de notificación diaria.
        """
        hoy = datetime.date.today()
        hoy_str = hoy.strftime("%Y-%m-%d")
        mostrar_popup = False

        # Pecados
        if self.fecha_gasto != "" and self.fecha_gasto != hoy_str:
            for p in self.pecados_hoy:
                if 'fecha' not in p:
                    p['fecha'] = self.fecha_gasto
                self.historial_pecados.append(p)
            try:
                self.gasto_acumulado = float(self.gasto_acumulado or 0.0) + float(self.gasto_hoy or 0.0)
            except Exception:
                self.gasto_acumulado = (self.gasto_acumulado or 0.0) + (self.gasto_hoy or 0.0)
            self.pecados_hoy = []
            self.gasto_hoy = 0.0
            self.fecha_gasto = hoy_str

        # Regalos
        if self.fecha_regalo != "" and self.fecha_regalo != hoy_str:
            for r in self.regalos_hoy:
                if 'fecha' not in r:
                    r['fecha'] = self.fecha_regalo
                self.historial_regalos.append(r)
            try:
                self.ingresos_acumulados = float(self.ingresos_acumulados or 0.0) + float(self.ingresos_hoy or 0.0)
            except Exception:
                self.ingresos_acumulados = (self.ingresos_acumulados or 0.0) + (self.ingresos_hoy or 0.0)
            self.regalos_hoy = []
            self.ingresos_hoy = 0.0
            self.fecha_regalo = hoy_str

        # Gastos necesarios
        if self.fecha_gasto_necesario != "" and self.fecha_gasto_necesario != hoy_str:
            for g in self.gastos_necesarios_hoy:
                if 'fecha' not in g:
                    g['fecha'] = self.fecha_gasto_necesario
                self.historial_gastos_necesarios.append(g)
            gasto_ayer = sum(g.get('precio', 0) for g in self.gastos_necesarios_hoy)
            try:
                self.gasto_necesario_acumulado = float(self.gasto_necesario_acumulado or 0.0) + float(gasto_ayer or 0.0)
            except Exception:
                self.gasto_necesario_acumulado = (self.gasto_necesario_acumulado or 0.0) + (gasto_ayer or 0.0)
            self.gastos_necesarios_hoy = []
            self.fecha_gasto_necesario = hoy_str

        # Notificación diaria
        if self.is_first_run:
            self.is_first_run = False
            self.last_notif_date = hoy_str
        elif self.last_notif_date != hoy_str:
            mostrar_popup = True
            self.last_notif_date = hoy_str

        return mostrar_popup

    def obtener_ahorrado_float(self) -> float:
        try:
            return float(self.ahorrado_guardado or 0.0)
        except Exception:
            return 0.0

    def listar_discrepancias_esquema(self) -> list:
        problemas = []
        for i, g in enumerate(self.gastos_fijos or []):
            if 'monto' not in g:
                problemas.append(f"gastos_fijos[{i}] no tiene 'monto'")
            else:
                try:
                    float(g.get('monto', 0.0))
                except Exception:
                    problemas.append(f"gastos_fijos[{i}].monto no es numérico")
        for i, h in enumerate(self.historial_gastos_necesarios or []):
            if 'precio' not in h:
                problemas.append(f"historial_gastos_necesarios[{i}] no tiene 'precio'")
            else:
                try:
                    float(h.get('precio', 0.0))
                except Exception:
                    problemas.append(f"historial_gastos_necesarios[{i}].precio no es numérico")
        for i, p in enumerate(self.productos or []):
            if 'precio' not in p:
                problemas.append(f"productos[{i}] no tiene 'precio'")
            else:
                try:
                    float(p.get('precio', 0.0))
                except Exception:
                    problemas.append(f"productos[{i}].precio no es numérico")
        return problemas