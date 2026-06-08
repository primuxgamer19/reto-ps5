# mat_stats.py
import datetime
from collections import defaultdict
from typing import Any, Dict, List
from mat.mat_utils import safe_float

def generar_estadisticas_pecados(historial: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = 0.0
    mensuales = defaultdict(float)

    for item in (historial or []):
        # Compatibilidad total: busca precio, monto o valor sin crashear
        precio = 0.0
        if 'precio' in item:
            precio = safe_float(item.get('precio', 0.0))
        elif 'monto' in item:
            precio = safe_float(item.get('monto', 0.0))
        else:
            precio = safe_float(item.get('valor', 0.0))

        total += precio

        fecha_str = item.get('fecha', "") or item.get('fecha_inicio', "")
        try:
            fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
            clave_mes = fecha.strftime("%Y-%m")
        except Exception:
            clave_mes = "SIN_FECHA"
            
        mensuales[clave_mes] += precio

    return {
        "total": total,
        "mensuales": dict(mensuales)
    }