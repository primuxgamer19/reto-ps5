# dat_ingresos.py
# Módulo encargado de gestionar el salario y los regalos/ingresos extras.

class IngresosMixin:
    def init_ingresos(self):
        self.salario = 0.0
        self.fecha_salario = ""
        self.regalos_hoy = []
        self.historial_regalos = []
        self.fecha_regalo = ""
        self.ingresos_acumulados = 0.0
        self.ingresos_hoy = 0.0
        self.ingresos_extra = 0.0
        self.last_regalos_notif_date = ""
        self.last_regalos_notif_sum = 0.0
        self.last_regalos_notif_count = 0

    def cargar_ingresos(self, data: dict):
        self.salario = data.get('salario', 0.0)
        self.fecha_salario = data.get('fecha_salario', "")
        self.regalos_hoy = data.get('regalos_hoy', [])
        self.historial_regalos = data.get('historial_regalos', [])
        self.fecha_regalo = data.get('fecha_regalo', "")
        self.ingresos_acumulados = data.get('ingresos_acumulados', 0.0)
        self.ingresos_hoy = data.get('ingresos_hoy', 0.0)
        
        # Cálculo seguro de ingresos extra
        try:
            self.ingresos_extra = float(data.get('ingresos_extra') or (float(self.ingresos_acumulados) + float(self.ingresos_hoy)))
        except Exception:
            self.ingresos_extra = 0.0

        self.last_regalos_notif_date = data.get('last_regalos_notif_date', "")
        self.last_regalos_notif_sum = data.get('last_regalos_notif_sum', 0.0)
        self.last_regalos_notif_count = data.get('last_regalos_notif_count', 0)

    def guardar_ingresos(self) -> dict:
        try:
            self.salario = float(self.salario or 0.0)
            self.ingresos_acumulados = float(self.ingresos_acumulados or 0.0)
            self.ingresos_hoy = float(self.ingresos_hoy or 0.0)
            self.ingresos_extra = self.ingresos_acumulados + self.ingresos_hoy
        except Exception:
            pass

        return {
            'salario': self.salario,
            'fecha_salario': self.fecha_salario,
            'regalos_hoy': self.regalos_hoy,
            'historial_regalos': self.historial_regalos,
            'fecha_regalo': self.fecha_regalo,
            'ingresos_acumulados': self.ingresos_acumulados,
            'ingresos_hoy': self.ingresos_hoy,
            'ingresos_extra': self.ingresos_extra,
            'last_regalos_notif_date': self.last_regalos_notif_date,
            'last_regalos_notif_sum': getattr(self, 'last_regalos_notif_sum', 0.0),
            'last_regalos_notif_count': getattr(self, 'last_regalos_notif_count', 0)
        }

    def procesar_eventos_ingresos(self, hoy_str: str):
        if self.fecha_regalo != "" and self.fecha_regalo != hoy_str:
            for r in self.regalos_hoy:
                if 'fecha' not in r:
                    r['fecha'] = self.fecha_regalo
                self.historial_regalos.append(r)
            try:
                self.ingresos_acumulados = float(self.ingresos_acumulados or 0.0) + float(self.ingresos_hoy or 0.0)
            except Exception:
                pass
            self.regalos_hoy = []
            self.ingresos_hoy = 0.0
            self.fecha_regalo = hoy_str