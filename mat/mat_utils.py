# mat_utils.py
import datetime
from typing import Any, List, Dict

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0.0)
    except Exception:
        return default

def calcular_meses_trabajo(fecha_salario_str: str) -> float:
    if not fecha_salario_str:
        return 0.0
    try:
        f_sal = datetime.datetime.strptime(fecha_salario_str, "%Y-%m-%d").date()
        hoy = datetime.date.today()
        if f_sal > hoy:
            return 0.0
        dias_trabajados = (hoy - f_sal).days
        # Promedio exacto de días por mes para cálculos financieros
        return dias_trabajados / 30.44
    except Exception:
        return 0.0

def calcular_acumulado_gastos_fijos(gastos_fijos: List[Dict[str, Any]]) -> float:
    hoy = datetime.date.today()
    total = 0.0
    for g in (gastos_fijos or []):
        monto = safe_float(g.get('monto', 0.0))
        fecha_inicio_str = g.get('fecha_inicio', '')
        
        if not fecha_inicio_str:
            # Si no tiene fecha, asume que es un gasto de solo este mes actual
            total += monto
            continue
        
        try:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            if fecha_inicio > hoy:
                continue
            dias_activo = (hoy - fecha_inicio).days
            meses_proporcionales = dias_activo / 30.44
            total += (meses_proporcionales * monto)
        except Exception:
            total += monto
            
    return total