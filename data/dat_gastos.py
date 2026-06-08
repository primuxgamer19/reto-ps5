# dat_gastos.py
# Módulo encargado de gestionar los gastos fijos, pecados y necesarios.

class GastosMixin:
    def init_gastos(self):
        self.gastos_fijos = []
        
        # Pecados
        self.gasto_hoy = 0.0
        self.fecha_gasto = ""
        self.gasto_acumulado = 0.0
        self.pecados_hoy = []
        self.historial_pecados = []

        # Necesarios
        self.gastos_necesarios_hoy = []
        self.fecha_gasto_necesario = ""
        self.gasto_necesario_acumulado = 0.0
        self.historial_gastos_necesarios = []

    def cargar_gastos(self, data: dict):
        self.gastos_fijos = data.get('gastos_fijos', [])
        
        self.gasto_hoy = data.get('gasto_hoy', 0.0)
        self.fecha_gasto = data.get('fecha_gasto', "")
        self.gasto_acumulado = data.get('gasto_acumulado', 0.0)
        self.pecados_hoy = data.get('pecados_hoy', [])
        self.historial_pecados = data.get('historial_pecados', [])

        self.gastos_necesarios_hoy = data.get('gastos_necesarios_hoy', [])
        self.fecha_gasto_necesario = data.get('fecha_gasto_necesario', "")
        self.gasto_necesario_acumulado = data.get('gasto_necesario_acumulado', 0.0)
        self.historial_gastos_necesarios = data.get('historial_gastos_necesarios', [])

    def guardar_gastos(self) -> dict:
        try:
            self.gasto_hoy = float(self.gasto_hoy or 0.0)
            self.gasto_acumulado = float(self.gasto_acumulado or 0.0)
            self.gasto_necesario_acumulado = float(self.gasto_necesario_acumulado or 0.0)
        except Exception:
            pass

        # Limpiar gastos fijos para el JSON
        fijos_limpios = []
        for g in (self.gastos_fijos or []):
            gg = dict(g)
            monto_val = gg.get('monto', gg.get('precio', 0.0))
            try:
                gg['monto'] = float(monto_val)
            except Exception:
                gg['monto'] = 0.0
            if 'precio' in gg:
                del gg['precio']
            if 'fecha_inicio' in gg and gg['fecha_inicio'] is None:
                gg.pop('fecha_inicio', None)
            fijos_limpios.append(gg)

        return {
            'gastos_fijos': fijos_limpios,
            'gasto_hoy': self.gasto_hoy,
            'fecha_gasto': self.fecha_gasto,
            'gasto_acumulado': self.gasto_acumulado,
            'pecados_hoy': self.pecados_hoy,
            'historial_pecados': self.historial_pecados,
            'gastos_necesarios_hoy': self.gastos_necesarios_hoy,
            'fecha_gasto_necesario': self.fecha_gasto_necesario,
            'gasto_necesario_acumulado': self.gasto_necesario_acumulado,
            'historial_gastos_necesarios': self.historial_gastos_necesarios
        }

    def procesar_eventos_gastos(self, hoy_str: str):
        # Pecados
        if self.fecha_gasto != "" and self.fecha_gasto != hoy_str:
            for p in self.pecados_hoy:
                if 'fecha' not in p:
                    p['fecha'] = self.fecha_gasto
                self.historial_pecados.append(p)
            try:
                self.gasto_acumulado = float(self.gasto_acumulado or 0.0) + float(self.gasto_hoy or 0.0)
            except Exception:
                pass
            self.pecados_hoy = []
            self.gasto_hoy = 0.0
            self.fecha_gasto = hoy_str

        # Necesarios
        if self.fecha_gasto_necesario != "" and self.fecha_gasto_necesario != hoy_str:
            for g in self.gastos_necesarios_hoy:
                if 'fecha' not in g:
                    g['fecha'] = self.fecha_gasto_necesario
                self.historial_gastos_necesarios.append(g)
            gasto_ayer = sum(float(g.get('precio', 0.0)) for g in self.gastos_necesarios_hoy)
            try:
                self.gasto_necesario_acumulado = float(self.gasto_necesario_acumulado or 0.0) + float(gasto_ayer or 0.0)
            except Exception:
                pass
            self.gastos_necesarios_hoy = []
            self.fecha_gasto_necesario = hoy_str 