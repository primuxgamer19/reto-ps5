# normalizers.py
# Funciones para normalizar esquemas y tipos del JSON de datos

from typing import List, Dict, Any

def _to_float_safe(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def normalize_gastos_fijos(raw_gastos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normaliza la lista de gastos fijos:
    - Acepta 'precio' como sinónimo de 'monto'
    - Acepta 'fecha' como sinónimo de 'fecha_inicio'
    - Asegura que 'monto' sea float
    """
    normalized = []
    for g in (raw_gastos or []):
        ng = dict(g)
        if 'monto' not in ng and 'precio' in ng:
            ng['monto'] = _to_float_safe(ng.get('precio', 0.0))
        else:
            ng['monto'] = _to_float_safe(ng.get('monto', 0.0))
        if 'fecha_inicio' not in ng and 'fecha' in ng:
            ng['fecha_inicio'] = ng.get('fecha')
        normalized.append(ng)
    return normalized

def normalize_historial_precio_list(raw_list: List[Dict[str, Any]], prefer_monto=False) -> List[Dict[str, Any]]:
    """
    Normaliza listas de historiales que usan 'precio' o 'monto'.
    Si prefer_monto=True, convierte 'precio' a 'monto' en su lugar.
    """
    normalized = []
    for item in (raw_list or []):
        ni = dict(item)
        if 'precio' in ni:
            ni['precio'] = _to_float_safe(ni.get('precio', 0.0))
        elif 'monto' in ni and not prefer_monto:
            ni['precio'] = _to_float_safe(ni.get('monto', 0.0))
        if prefer_monto:
            if 'monto' not in ni and 'precio' in ni:
                ni['monto'] = _to_float_safe(ni.get('precio', 0.0))
            else:
                ni['monto'] = _to_float_safe(ni.get('monto', 0.0))
        normalized.append(ni)
    return normalized

def normalize_productos(raw_productos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Asegura que cada producto tenga 'precio' numérico.
    """
    normalized = []
    for p in (raw_productos or []):
        np_ = dict(p)
        if 'precio' in np_:
            np_['precio'] = _to_float_safe(np_.get('precio', 0.0))
        elif 'monto' in np_:
            np_['precio'] = _to_float_safe(np_.get('monto', 0.0))
        normalized.append(np_)
    return normalized

def normalize_general_numbers(mapping: dict, keys: List[str]) -> None:
    """
    Convierte en sitio los valores de keys en mapping a float si vienen como string.
    """
    for k in keys:
        v = mapping.get(k, None)
        if isinstance(v, str):
            try:
                mapping[k] = float(v)
            except Exception:
                mapping[k] = 0.0