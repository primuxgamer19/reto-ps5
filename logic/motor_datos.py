import os
import json
import datetime
from kivy.utils import platform

from data.dat_presupuesto import PresupuestoMixin
from data.dat_ingresos import IngresosMixin
from data.dat_gastos import GastosMixin
from data.dat_notificaciones import NotificacionesMixin

from data.normalizers import (
    normalize_gastos_fijos,
    normalize_historial_precio_list,
    normalize_productos,
    normalize_general_numbers
)
from data.io_utils import atomic_write_json, obtener_ruta_exportacion, exportar_json, importar_json

class MotorDatos(PresupuestoMixin, IngresosMixin, GastosMixin, NotificacionesMixin):
    def __init__(self):
        self.init_presupuesto()
        self.init_ingresos()
        self.init_gastos()
        self.init_notificaciones()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # project_root: carpeta raíz del proyecto (un nivel arriba de logic/)
        project_root = os.path.dirname(base_dir)
        self.base_dir = base_dir
        # Guardar el archivo de datos en la raíz del proyecto (como estaba originalmente)
        self.data_file = os.path.join(project_root, "ahorro_data.json")
        self.platform_name = platform if isinstance(platform, str) else None
        
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}
        else:
            data = {}

        self.cargar_presupuesto(data)
        self.cargar_ingresos(data)
        self.cargar_gastos(data)
        self.cargar_notificaciones(data)

        self.gastos_fijos = normalize_gastos_fijos(self.gastos_fijos)
        self.historial_gastos_necesarios = normalize_historial_precio_list(self.historial_gastos_necesarios)
        self.historial_pecados = normalize_historial_precio_list(self.historial_pecados)
        self.historial_regalos = normalize_historial_precio_list(self.historial_regalos)
        self.pecados_hoy = normalize_historial_precio_list(self.pecados_hoy)
        self.regalos_hoy = normalize_historial_precio_list(self.regalos_hoy)
        self.productos = normalize_productos(self.productos)
        self.gastos_necesarios_hoy = normalize_historial_precio_list(self.gastos_necesarios_hoy)

        normalize_general_numbers(self.__dict__, [
            'salario', 'gasto_hoy', 'gasto_acumulado',
            'ingresos_acumulados', 'ingresos_hoy', 'gasto_necesario_acumulado',
            'last_regalos_notif_sum'
        ])

        for fecha_attr in ['fecha_gasto', 'fecha_salario', 'fecha_regalo', 'fecha_gasto_necesario',
                           'fecha_limite', 'last_notif_date', 'last_regalos_notif_date']:
            if getattr(self, fecha_attr, None) is None:
                setattr(self, fecha_attr, "")

        if not hasattr(self, "is_first_run"):
            self.is_first_run = True

    def save_data(self):
        data = {}
        data.update(self.guardar_presupuesto())
        data.update(self.guardar_ingresos())
        data.update(self.guardar_gastos())
        data.update(self.guardar_notificaciones())

        try:
            if getattr(self, "last_notif_date", ""):
                data["last_notif_date"] = self.last_notif_date
        except:
            pass

        atomic_write_json(self.data_file, data, indent=4, ensure_ascii=False)

    def procesar_eventos_diarios(self) -> bool:
        hoy = datetime.date.today()
        hoy_str = hoy.strftime("%Y-%m-%d")
        
        self.procesar_eventos_ingresos(hoy_str)
        self.procesar_eventos_gastos(hoy_str)

        mostrar_popup = False
        cfg = self.get_config()
        if not hasattr(self, "is_first_run"):
            self.is_first_run = True

        if self.is_first_run:
            self.is_first_run = False
            self.set_last_sent_date(hoy_str)
        else:
            if cfg.get("enabled", False) and cfg.get("last_sent", "") != hoy_str:
                mostrar_popup = True
                self.set_last_sent_date(hoy_str)

        self.save_data()
        return mostrar_popup

    def obtener_ruta_exportacion(self) -> str:
        return obtener_ruta_exportacion(self.base_dir, self.platform_name)

    def exportar_json(self, nombre_archivo: str) -> tuple:
        self.save_data()
        return exportar_json(self.data_file, nombre_archivo, self.base_dir, self.platform_name)

    def importar_json(self, ruta_origen: str) -> tuple:
        ok, msg = importar_json(ruta_origen, self.data_file)
        if ok:
            self.load_data()
        return ok, msg