# dat_presupuesto.py
# Módulo encargado de gestionar las metas, productos y configuración general.

class PresupuestoMixin:
    def init_presupuesto(self):
        self.productos = [
            {'nombre': 'PS5 Slim', 'precio': 550.0},
            {'nombre': 'Regulador', 'precio': 60.0},
            {'nombre': 'Monitor 1080p', 'precio': 280.0},
            {'nombre': 'GTA 6', 'precio': 150.0}
        ]
        self.ahorrado_guardado = ""
        self.fecha_limite = "2026-11-19"
        self.is_first_run = True
        self.last_notif_date = ""

    def cargar_presupuesto(self, data: dict):
        self.productos = data.get('productos', self.productos)
        self.ahorrado_guardado = data.get('ahorrado', "")
        self.fecha_limite = data.get('fecha_limite', "2026-11-19")
        self.is_first_run = data.get('is_first_run', True)
        self.last_notif_date = data.get('last_notif_date', "")

    def guardar_presupuesto(self) -> dict:
        return {
            'productos': self.productos,
            'ahorrado': self.ahorrado_guardado,
            'fecha_limite': self.fecha_limite,
            'is_first_run': self.is_first_run,
            'last_notif_date': self.last_notif_date
        }