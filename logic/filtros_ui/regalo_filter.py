# logic/filtros_ui/regalo_filter.py
# Patrones y keywords para la UI de Regalos (ingresos / ventas detectadas)
# Contiene: weights (regex->peso) y keywords (listas largas para fuzzy matching)

weights = {
    'regalo_caridad': {
        # patrones generales (mantener algunos pesos originales)
        r'regalos?': 5, r'regalad(?:o|a)s?': 5, r'obsequios?': 5, r'donaci[oó]n': 5,
        r'caridad': 5, r'gratis': 5, r'bendici[oó]n': 5
    },
    # mantener inversión en este módulo para detectar ventas dentro de regalos
    'inversion': {
        r'venta': 6, r'ventas?': 6, r'vend(?:ido|ida|idos|idas|iendo|er|í)': 6, r'vend[ií]': 6,
        r'vend(?:er|iendo|ido)': 6, r'para vender': 7, r'para revender': 7
    }
}

# Lista extensa (100+) de palabras/variantes que indican VENTA / INGRESO por venta
keywords = {
    'regalo_caridad': [
        # palabras que indican regalo/ingreso externo (familia, bonos, donaciones, premios)
        'regalo','regalos','obsequio','obsequios','donacion','donaciones','donativo','donativos',
        'bendicion','bendiciones','bono','bonos','sueldo extra','sueldo_extra','propina','propinas',
        'premio','premios','ganancia','ganancias','hallazgo','hallazgos','encontrado','encontrada',
        'prestado','prestaron','prestamo','prestamos','regalado','regalada','sorpresa','sorpresas',
        'ayuda','ayudas','subsidio','subsidios','herencia','herencias','venta','ventas','vendido',
        'vendida','vendidos','vendidas','vendi','vendí','vender','vendiend','vendiendo','revender',
        'revendido','revendida','revendiendo','venta_online','venta_online','marketplace','mercado',
        'tienda','local','kiosco','negocio','emprendimiento','emprender','emprendimiento_local',
        'clientes','cliente','ingreso','ingresos','ingreso_extra','ingresos_extra','ingreso_pasivo',
        'comision','comisiones','venta_directa','venta_rapida','venta_de_garaje','venta_de_garaje',
        'venta_de_galletas','venta_de_pan','venta_de_ropa','venta_de_artesanias','venta_de_servicios',
        'gané','gane','ganado','ganada','ganancias_por_venta','venta_mayorista','venta_minorista',
        'reventa','revenda','revendedor','revendedora','stock','mercancia','mercancía','mercancia_vendida',
        'producto_vendido','producto','productos','tienda_online','ecommerce','shop','venta_online',
        'paypal','transferencia','transferencias','pago','pagos','cobro','cobros','factura','facturas',
        'recibo','recibos','pedido','pedidos','orden','ordenes','ordenes_de_compra','venta_local',
        'venta_casa','venta_calle','venta_evento','feria','ferias','expo','exposicion','exposiciones',
        'kermes','kermeses','venta_de_comida','venta_de_bebidas','venta_de_artesania','venta_de_servicio',
        'venta_de_ropa_usada','venta_de_segunda','venta_de_segunda_mano','venta_de_libros','venta_de_juguetes',
        'venta_de_electronica','venta_de_celulares','venta_de_muebles','venta_de_joyas','venta_de_accesorios',
        'venta_de_calzado','venta_de_zapatos','venta_de_tenis','venta_de_zapatillas','venta_de_complementos',
        'venta_de_cosmeticos','venta_de_maquillaje','venta_de_cursos','venta_de_clases','venta_de_talleres',
        'venta_de_servicios_profesionales','venta_de_servicios_tecnicos','venta_de_software','venta_de_apps',
        'venta_de_cursos_online','venta_de_ebooks','venta_de_materiales','venta_de_insumos','venta_de_herramientas',
        'venta_de_plantas','venta_de_semillas','venta_de_alimentos','venta_de_pan','venta_de_galletas',
        'vend','vnd','vndd','vndido','vndida','vndos','vndas','vndí','vndíe','vndiendo','vndido'
    ],
    'inversion': [
        # duplicar algunas variantes para reforzar detección de venta como inversión
        'inversion','inversiones','invertir','inverti','invertido','capital','activo','activos',
        'insumo','insumos','material','materiales','herramienta','herramientas','stock','mercancia',
        'mercancia_vendida','para_vender','para_revender','revender','revenda','revendedor','revendedora',
        'tienda','local','kiosco','emprendimiento','negocio','clientes','ganancia','ganancias','venta'
    ]
}