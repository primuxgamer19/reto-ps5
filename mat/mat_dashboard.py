# mat_dashboard.py
import datetime
import math
from typing import Any, Dict
from mat.mat_utils import safe_float, calcular_meses_trabajo, calcular_acumulado_gastos_fijos

def analizar_reporte(datos: Any, ahorrado_actual: float) -> Dict[str, Any]:
    meta = sum(safe_float(p.get('precio', 0.0)) for p in getattr(datos, 'productos', []))
    if meta <= 0:
        return {"error": "PRESUPUESTO_VACIO"}

    try:
        fecha_limite_obj = datetime.datetime.strptime(getattr(datos, 'fecha_limite', ''), "%Y-%m-%d").date()
    except Exception:
        return {"error": "FECHA_INVALIDA"}

    hoy = datetime.date.today()
    total_dias = (fecha_limite_obj - hoy).days
    meses_aprox = math.ceil(total_dias / 30.44) if total_dias > 0 else 0

    falta = max(0.0, meta - safe_float(ahorrado_actual))
    cuota = (falta / meses_aprox) if meses_aprox > 0 else float('inf')
    cuota_diaria = (falta / total_dias) if total_dias > 0 else float('inf')
    porcentaje = min(100.0, (safe_float(ahorrado_actual) / meta) * 100.0) if meta > 0 else 0.0

    # 1. Finanzas del Mes (Libre de polvo y paja, sin arriendo fantasma)
    salario = safe_float(getattr(datos, 'salario', 0.0))
    total_gastos_fijos_mensual = sum(safe_float(g.get('monto', 0.0)) for g in getattr(datos, 'gastos_fijos', []))
    disponible_mes = salario - total_gastos_fijos_mensual

    # 2. Cálculo del Saldo Esperado (Dinero que DEBERÍAS tener ahorrado)
    meses_trabajo = calcular_meses_trabajo(getattr(datos, 'fecha_salario', ""))
    
    # INGRESOS TOTALES (Salario BRUTO acumulado + Regalos) 
    # Usamos salario bruto porque luego le restamos los gastos fijos acumulados. Evita cobrar doble.
    ingreso_laboral_bruto = meses_trabajo * salario
    ingresos_extra = safe_float(getattr(datos, 'ingresos_extra', 0.0))
    
    # GASTOS TOTALES
    gasto_pecados = safe_float(getattr(datos, 'gasto_acumulado', 0.0)) + safe_float(getattr(datos, 'gasto_hoy', 0.0))
    gasto_necesario = safe_float(getattr(datos, 'gasto_necesario_acumulado', 0.0)) + sum(safe_float(g.get('precio', 0.0)) for g in getattr(datos, 'gastos_necesarios_hoy', []))
    acumulado_gastos_fijos = calcular_acumulado_gastos_fijos(getattr(datos, 'gastos_fijos', []))

    # BALANCE FINAL
    saldo_esperado = (ingreso_laboral_bruto + ingresos_extra) - (gasto_pecados + gasto_necesario + acumulado_gastos_fijos)

    meses_rapidos = math.ceil(falta / disponible_mes) if (disponible_mes > 0 and falta > 0) else (0 if falta == 0 else float('inf'))

    return {
        "error": None,
        "meta": meta,
        "total_dias": total_dias,
        "meses_aprox": meses_aprox,
        "falta": falta,
        "cuota": cuota,
        "cuota_diaria": cuota_diaria,
        "porcentaje": porcentaje,
        "disponible_mes": disponible_mes,
        "saldo_esperado": saldo_esperado,
        "meses_rapidos": meses_rapidos,
        "meses_trabajo": meses_trabajo,
        "total_gastos_fijos_mensual": total_gastos_fijos_mensual,
        "gasto_necesario_acumulado": safe_float(getattr(datos, 'gasto_necesario_acumulado', 0.0)),
        "gasto_necesario_hoy": sum(safe_float(g.get('precio', 0.0)) for g in getattr(datos, 'gastos_necesarios_hoy', [])),
        "acumulado_gastos_fijos": acumulado_gastos_fijos
    }
