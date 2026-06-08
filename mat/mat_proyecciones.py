# mat_proyecciones.py
from typing import Any
from mat.mat_utils import safe_float

def calcular_impacto_pecado(datos: Any, gasto_total_historico: float) -> float:
    # Se eliminó la variable basura de arriendo. Todo es gasto fijo.
    total_gastos_fijos_mensual = sum(safe_float(g.get('monto', 0.0)) for g in getattr(datos, 'gastos_fijos', []))
    salario = safe_float(getattr(datos, 'salario', 0.0))
    
    disponible_mes = salario - total_gastos_fijos_mensual
    disponible_diario = disponible_mes / 30.44 if disponible_mes > 0 else 0.0
    
    if disponible_diario > 0:
        return gasto_total_historico / disponible_diario
    return float('inf')