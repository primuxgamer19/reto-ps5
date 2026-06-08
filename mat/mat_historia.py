# mat_historia.py
# Reconstruye el flujo de caja diario basado en el historial y los eventos de hoy

import datetime
from collections import defaultdict
from typing import Any, List, Dict
from mat.mat_utils import safe_float

def generar_linea_tiempo(datos: Any) -> List[Dict[str, Any]]:
    eventos = defaultdict(lambda: {'ingresos': 0.0, 'gastos': 0.0, 'detalles': []})
    hoy_str = datetime.date.today().strftime("%Y-%m-%d")
    
    # 1. Recopilar Regalos (Ingresos: Historial + Hoy)
    lista_ingresos = getattr(datos, 'historial_regalos', []) + getattr(datos, 'regalos_hoy', [])
    for r in lista_ingresos:
        fecha = r.get('fecha', hoy_str) # Si no tiene fecha, es de hoy
        val = safe_float(r.get('precio', 0.0))
        eventos[fecha]['ingresos'] += val
        eventos[fecha]['detalles'].append(f"+ Regalo/Venta: {r.get('nombre', 'Extra')} (${val:.2f})")
        
    # 2. Recopilar Pecados (Gastos: Historial + Hoy)
    lista_pecados = getattr(datos, 'historial_pecados', []) + getattr(datos, 'pecados_hoy', [])
    for p in lista_pecados:
        fecha = p.get('fecha', hoy_str)
        val = safe_float(p.get('precio', 0.0))
        eventos[fecha]['gastos'] += val
        eventos[fecha]['detalles'].append(f"- Pecado: {p.get('nombre', 'Pendejada')} (${val:.2f})")
        
    # 3. Recopilar Gastos Necesarios (Gastos: Historial + Hoy)
    lista_necesarios = getattr(datos, 'historial_gastos_necesarios', []) + getattr(datos, 'gastos_necesarios_hoy', [])
    for n in lista_necesarios:
        fecha = n.get('fecha', hoy_str)
        val = safe_float(n.get('precio', 0.0))
        eventos[fecha]['gastos'] += val
        eventos[fecha]['detalles'].append(f"- Necesario: {n.get('nombre', 'Gasto')} (${val:.2f})")

    fechas_ordenadas = sorted(eventos.keys())
    
    if not fechas_ordenadas:
        return [{'fecha': hoy_str, 'saldo': safe_float(getattr(datos, 'ahorrado_guardado', 0.0)), 'detalles': ['Sin historial ni movimientos hoy']}]

    linea_tiempo = []
    saldo_acumulado = 0.0
    
    # Reconstruir día a día
    for f in fechas_ordenadas:
        ev = eventos[f]
        saldo_acumulado += (ev['ingresos'] - ev['gastos'])
        linea_tiempo.append({
            'fecha': f,
            'saldo': saldo_acumulado,
            'ingresos_dia': ev['ingresos'],
            'gastos_dia': ev['gastos'],
            'detalles': ev['detalles']
        })

    # Proyectar el punto de la Fecha Límite
    fecha_limite = getattr(datos, 'fecha_limite', "")
    if fecha_limite and fecha_limite > fechas_ordenadas[-1]:
        linea_tiempo.append({
            'fecha': fecha_limite,
            'saldo': saldo_acumulado,
            'ingresos_dia': 0.0,
            'gastos_dia': 0.0,
            'detalles': ['META / FECHA LÍMITE']
        })

    return linea_tiempo
    