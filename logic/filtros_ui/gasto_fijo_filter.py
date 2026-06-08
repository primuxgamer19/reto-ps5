# logic/filtros_ui/gasto_fijo_filter.py
# Patrones y keywords para gastos necesarios / inversiones / imprevistos
# Actualizado: añade 'phrases' para combinaciones (ej. "paquete para vender", "compra para negocio"),
# keywords ampliadas y variantes para distinguir inversión/necesario de gasto pendejo.

weights = {
    'inversion': {
        # patrones base (regex)
        r'inver[sc]i[oó]n(?:es)?': 5, r'invert(?:ir|i|í|ido)': 5, r'para vender': 7
    },
    'imprevisto': {
        r'medicament(?:o|a)s?': 5, r'medicinas?': 5, r'doctores?': 5, r'hospital(?:es)?': 5
    }
}

# Frases compuestas (prioritarias) para detectar intención de inversión o gasto necesario
phrases = [
    # inversión / reventa
    'paquete para vender', 'paquete para revender', 'compré para vender', 'compré para revender',
    'compra para negocio', 'compra para vender', 'compra para revender', 'compra stock',
    'compra insumos para venta', 'compra insumos negocio', 'compra para tienda', 'compra para local',
    'compra para emprendimiento', 'compra para emprender', 'compra para revender online',
    # formación / herramientas (inversión)
    'curso para negocio', 'curso para emprender', 'compra herramienta para trabajo', 'compra herramienta negocio',
    'inversion en equipo', 'compra maquinaria', 'compra herramienta', 'compra activo',
    # imprevistos y reparaciones
    'reparacion urgente', 'reparacion de coche', 'reparacion casa', 'gasto por accidente',
    'gasto por emergencia', 'consulta medica', 'consulta medica urgente', 'medicamento urgente'
]

# Keywords amplias para fuzzy matching y búsqueda rápida
keywords = {
    'inversion': [
        'inversion','inversiones','invertir','inverti','invertido','capital','capitalizar','activo','activos',
        'insumo','insumos','material','materiales','herramienta','herramientas','stock','mercancia',
        'mercancia_vendida','para_vender','para_revender','revender','revenda','revendedor','revendedora',
        'tienda','local','kiosco','emprendimiento','negocio','clientes','ganancia','ganancias','venta',
        'compra_stock','compra_insumos','compra_mayorista','compra_mayor','compra_para_vender','compra_para_negocio',
        'maquinaria','equipo','mobiliario','mueble','licencia','licencias','software','hosting','dominio',
        # variantes y errores
        'inverssion','inversión','invertirrr','capitall','herramientass','insumoss','stockk','mercanciaa'
    ],
    'imprevisto': [
        'medicamento','medicamentos','medicina','medicinas','doctor','doctores','consulta_medica','consulta',
        'hospital','hospitales','urgencia','emergencia','clinica','clinicas','dentista','dentistas',
        'reparacion','reparaciones','reparar','arreglo','arreglos','mecanico','mecanicos','llanta','llantas',
        'grua','gruas','choque','accidente','multa','multas','transito','gas','luz','agua','internet',
        'servicio_basico','corte_luz','corte_agua','averia','rotura','fuga','plomeria','electricista',
        # variantes y errores
        'medicamentoo','medicinaa','doctorr','hospitalesess','reparacioness','mecanicoo','llantass'
    ]
}

# Nota: Este módulo expone datos (weights, phrases, keywords). La lógica de evaluación combinada
# (frases > regex > keywords > fuzzy fallback) se aplica en filtro_nombres.py para mantener
# rendimiento y coherencia entre UIs.