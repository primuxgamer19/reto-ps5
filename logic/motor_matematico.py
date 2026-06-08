# motor_matematico.py
# PUENTE MODULAR - No contiene cálculos, solo redirige a los módulos correspondientes.
from typing import Any, Dict, List

import mat.mat_dashboard as mat_dashboard
import mat.mat_proyecciones as mat_proyecciones
import mat.mat_stats as mat_stats
import mat.mat_historia as mat_historia
import mat.mat_geometria as mat_geometria
from mat.mat_utils import safe_float

def analizar_reporte(datos: Any, ahorrado_actual: Any) -> Dict[str, Any]:
    """Llamado por ui_calculadora.py y ui_presupuesto.py"""
    return mat_dashboard.analizar_reporte(datos, safe_float(ahorrado_actual))

def calcular_impacto_pecado(datos: Any, gasto_total_historico: float) -> float:
    """Llamado por ui_pecado.py"""
    return mat_proyecciones.calcular_impacto_pecado(datos, gasto_total_historico)

def generar_estadisticas_pecados(historial: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Llamado por ui_pecado.py, ui_regalo.py y ui_gastos_fijos.py para generar historiales"""
    return mat_stats.generar_estadisticas_pecados(historial)

def obtener_linea_tiempo(datos: Any) -> List[Dict[str, Any]]:
    """Llamado por ui_estadistica.py para obtener el progreso diario"""
    return mat_historia.generar_linea_tiempo(datos)

def mapear_coordenadas(linea_tiempo: list, width: float, height: float) -> list:
    """Llamado por ui_estadistica.py para escalar los puntos a la pantalla"""
    return mat_geometria.calcular_coordenadas_grafica(linea_tiempo, width, height)