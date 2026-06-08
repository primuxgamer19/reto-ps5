# mat_geometria.py
# Calcula las coordenadas, límites del mundo real y el nivel de detalle (LOD) para el plano cartesiano

import math
import datetime

def calcular_limites(linea_tiempo, productos, fecha_limite_str):
    """
    Define los límites máximos y mínimos del plano (El Mundo Real).
    Eje X: Desde el primer registro hasta la fecha límite.
    Eje Y: Desde $0 hasta la meta total (o el saldo máximo alcanzado).
    """
    # Calcular el total de la meta
    meta_total = sum(float(p.get('precio', 0.0)) for p in (productos or []))
    
    if not linea_tiempo:
        hoy_ts = datetime.datetime.now().timestamp()
        return hoy_ts, hoy_ts + (86400 * 30), 0.0, meta_total if meta_total > 0 else 100.0

    fechas_ts = []
    saldos = []
    
    for dia in linea_tiempo:
        try:
            dt = datetime.datetime.strptime(dia['fecha'], "%Y-%m-%d")
            fechas_ts.append(dt.timestamp())
        except Exception:
            continue
        saldos.append(float(dia.get('saldo', 0.0)))

    if not fechas_ts:
        hoy_ts = datetime.datetime.now().timestamp()
        return hoy_ts, hoy_ts + (86400 * 30), 0.0, meta_total if meta_total > 0 else 100.0

    # X Mínimo: La fecha más antigua registrada
    x_min = min(fechas_ts)
    
    # X Máximo: La fecha límite
    try:
        dt_limite = datetime.datetime.strptime(fecha_limite_str, "%Y-%m-%d")
        x_max = dt_limite.timestamp()
    except Exception:
        x_max = max(fechas_ts)
        
    if x_max <= x_min:
        x_max = x_min + (86400 * 7) # Margen de supervivencia de 7 días si las fechas están mal

    # Y Mínimo: Siempre empezamos desde el fondo (pero permitir negativos si existen en datos)
    # Si hay saldos negativos, respetarlos; si no, mantener 0.0 como mínimo.
    min_saldo = min(saldos) if saldos else 0.0
    y_min = min(0.0, min_saldo)

    # Y Máximo: Lo que sea mayor, el costo de todos los productos o el dinero que realmente tienes
    max_ahorrado = max(saldos) if saldos else 0.0
    y_max = max(meta_total, max_ahorrado)
    
    if y_max <= y_min:
        y_max = y_min + 100.0

    return x_min, x_max, y_min, y_max

def calcular_paso_optimo(rango_visible, max_lineas=8):
    """
    Matemática de Nivel de Detalle (LOD). 
    Calcula dinámicamente si los números del eje deben ir de 0.01, 1, 5, 10, o 100
    basado en qué tan cerca o lejos está la vista actual.
    """
    if rango_visible <= 0:
        return 1.0
        
    tamano_ideal = rango_visible / max_lineas
    
    # Encontrar la magnitud base en potencia de 10
    magnitud = 10.0 ** math.floor(math.log10(tamano_ideal))
    residual = tamano_ideal / magnitud
    
    # Ajustar a pasos estéticos (1, 2, 5)
    if residual > 5:
        paso = 10 * magnitud
    elif residual > 2:
        paso = 5 * magnitud
    else:
        paso = 2 * magnitud
        
    return paso

def mapear_valor(valor, in_min, in_max, out_min, out_max):
    """Interpola un valor de un rango al rango de píxeles de la pantalla"""
    if in_max == in_min:
        # Devolver el centro del rango de salida para evitar apilar todo en un borde
        return out_min + (out_max - out_min) / 2.0
    return out_min + ((valor - in_min) / (in_max - in_min)) * (out_max - out_min)