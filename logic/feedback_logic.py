# feedback_logic.py
import datetime
from kivy.app import App
from .filtro_nombres import FiltroNombres

def _calcular_penitencia(porcentaje):
    """Calcula el castigo final basado en qué tan cerca estuviste de la meta."""
    if porcentaje >= 85:
        return 1, "Prepara la máquina pa' quedarte calvo como Krilin D: (Casi coronas, pero fallaste por soso)"
    elif porcentaje >= 50:
        return 2, "Te toca el coco liso y tragarte un pedazo de pizza con piña por huevón T_T"
    else:
        return 3, "Te quedas calvo, te tragas una pizza con piña familiar y a gritar '¡qué rico!' gimiendo por pendejo 💀 (Nivel: Humillación Total)"

def _sum_items(lista, key='precio'):
    """Suma segura de una lista de dicts, admite claves distintas (ej: 'monto')."""
    total = 0.0
    for it in lista or []:
        try:
            total += float(it.get(key, it.get('precio', 0) or 0))
        except Exception:
            continue
    return total

def obtener_feedback_msg(datos, ahorrado, reporte_matematico):
    """
    Analiza la situación financiera y devuelve un mensaje honesto
    junto con el archivo de sonido correspondiente al puro estilo de Kevin.
    """
    # --- Extracción segura de reporte matemático ---
    meta = reporte_matematico.get('meta', 0)
    dias = reporte_matematico.get('total_dias', 0)
    porcentaje = reporte_matematico.get('porcentaje', 0)
    cuota = reporte_matematico.get('cuota', 0)
    cuota_diaria = reporte_matematico.get('cuota_diaria', None)
    disponible_mes = reporte_matematico.get('disponible_mes', 0)
    meses_fast = reporte_matematico.get('meses_rapidos', 9999) if reporte_matematico.get('meses_rapidos', 0) > 0 else 9999
    meses_trabajo = reporte_matematico.get('meses_trabajo', 0)
    saldo_esperado = reporte_matematico.get('saldo_esperado', 0)

    # --- Datos desde motor_datos (con getattr para evitar crashes) ---
    gasto_hoy = float(getattr(datos, 'gasto_hoy', 0.0) or 0.0)
    ingresos_extra = float(getattr(datos, 'ingresos_extra', 0.0) or 0.0)
    ingresos_acumulados = float(getattr(datos, 'ingresos_acumulados', 0.0) or 0.0)
    ingresos_hoy = float(getattr(datos, 'ingresos_hoy', 0.0) or 0.0)
    salario = float(getattr(datos, 'salario', 0.0) or 0.0)
    arriendo = float(getattr(datos, 'arriendo', 0.0) or 0.0)

    meses_limite = max(1, dias / 30.0) if dias is not None else 1
    termina_antes = (meses_fast < meses_limite) if disponible_mes > 0 else False

    # --- Inicializar filtro y análisis semántico ---
    filtro = FiltroNombres()
    pecados_analysis = filtro.analizar_lista(getattr(datos, 'pecados_hoy', []))
    regalos_analysis = filtro.analizar_lista(getattr(datos, 'regalos_hoy', []))
    gastos_necesarios_analysis = filtro.analizar_lista(getattr(datos, 'gastos_necesarios_hoy', []))
    gastos_fijos_list = getattr(datos, 'gastos_fijos', [])

    # --- Totales relevantes ---
    total_gastos_fijos = _sum_items(gastos_fijos_list, key='monto')
    total_regalos_hoy = _sum_items(getattr(datos, 'regalos_hoy', []), key='precio')
    total_regalos_acumulado = ingresos_acumulados
    total_gastos_necesarios_hoy = _sum_items(getattr(datos, 'gastos_necesarios_hoy', []), key='precio')
    total_pecados_hoy = _sum_items(getattr(datos, 'pecados_hoy', []), key='precio')

    # --- Detección de casos graves por clasificación semántica ---
    if any(anal.get('es_inversion') for anal in pecados_analysis):
        return ("¡HABLA SERIO HUEVÓN!\n\n"
                "Eso que metiste en 'Pecados' tiene toda la pinta de ser una inversión.\n"
                "No te pases de soso bro, ahí no va esa nota. Borra esa huevada de 'pecados', muévete a 'presupuesto' y ponlo en 'regalos'.\n"
                "¡Ponte once! B-)"), 'alerta.wav'

    # --- BLOQUE ORIGINAL: EASTER EGGS Y TROLEOS FIJOS ---
    if ahorrado > 10000: return ("¡Ni tú te lo crees! XD\n"
                                 "¿Atracaste un banco o qué chuchas?"), 'pum.mp3'
    if ahorrado == 666: return "¿$666? ¡Mala vibra bro, el diablo mismo o_O!", 'pum.mp3'
    if ahorrado == 777: return ("¿$777? ¡Hey muy buenas a todos, guapísimos!\n"
                                "B-)"), 'acierto.mp3'
    if 0 < ahorrado < 0.0001: return ("POBREZA MOLECULAR DETECTADA.\n"
                                      "¡No trolees y ponte a buscar chamba, vago! xd"), 'pum.mp3'
    if ahorrado == 67: return "Ni se te ocurra decirlo... -_-", 'alerta.wav'

    # --- BLOQUE 2: FRAUDE CONTABLE Y ERRORES LÓGICOS ---
    if arriendo > salario and salario > 0:
        return (f"¿Pagas más de arriendo que lo que ganas de sueldo?\n"
                f"¿A quién le debes plata? Ya ponte serio e informática -_-"), 'pum.mp3'

    if ahorrado > saldo_esperado + 5:
        return (f"¡Mentira detectada! -_-\n"
                f"Según tus cuentas deberías tener máximo ${saldo_esperado:.2f}.\n"
                f"¿De dónde salieron estos ${ahorrado:.2f}? ¿Hiciste un tumbe o te los robaste?"), 'pum.mp3'

    f_gastos_fijos = filtro.analizar_lista(gastos_fijos_list)
    if any(a.get('es_pecado_fraude') for a in f_gastos_fijos):
        return ("¡GASTO PENDEJO DETECTADO!\n"
                "No me quieras ver la cara de cojudo a mí, habla serio -_-"), 'pum.mp3'

    if any(a.get('es_pecado_fraude') for a in gastos_necesarios_analysis):
        return ("A ver bro, pusiste como 'necesario' cosas que se ven bien pendejas.\n"
                "Póngase serio con el reto o ya vaya comprando la máquina de afeitar -_-"), 'pum.mp3'

    # --- HIGHER HIERARCHY: METAS Y CASTIGOS FINALES OVERRIDE ---
    if ahorrado >= meta:
        has_sales_today = any(anal.get('es_inversion') for anal in regalos_analysis)
        if salario <= 0 and ingresos_extra >= meta and not has_sales_today:
            return ("¡AL FIN LO LOGRASTE B-Outside!\n"
                    "Pero con pura plata regalada de caridad...\n"
                    "Pinche mendigo del diablo, te salvaste de la pizza con piña -_-"), 'Alelulla.wav'
        return ("¡LO LOGRASTE, MI BROTHER! B-)\n"
                "¡La PS5 es tuya por fin! Prepárate para el GTA 6 a 60 FPS fijos. ¡A viciar duro!"), 'Alelulla.wav'

    if dias <= 0:
        nivel, descripcion = _calcular_penitencia(porcentaje)
        return (f"¡RETO PERDIDO, F EN EL CHAT!\n"
                f"Te pasaste {-dias} días de la fecha límite y sigues chiro.\n\n"
                f"PENITENCIA NIVEL {nivel}\n"
                f"{descripcion}"), 'pum.mp3'

    # --- Detección de inversión en regalos ---
    from datetime import date
    hoy_str = date.today().strftime("%Y-%m-%d")

    hay_inversion_en_regalos = any(anal.get('es_inversion') for anal in regalos_analysis)

    if hay_inversion_en_regalos:
        regalos_hoy_list = getattr(datos, 'regalos_hoy', [])
        suma_regalos_hoy = sum(r.get('precio', 0.0) for r in regalos_hoy_list)
        count_regalos_hoy = len(regalos_hoy_list)

        last_date = getattr(datos, 'last_regalos_notif_date', "")
        last_sum = float(getattr(datos, 'last_regalos_notif_sum', 0.0) or 0.0)
        last_count = int(getattr(datos, 'last_regalos_notif_count', 0) or 0)

        fecha_regalo = getattr(datos, 'fecha_regalo', '')
        ingresos_hoy = float(getattr(datos, 'ingresos_hoy', 0.0) or 0.0)
        es_nuevo_hoy = (fecha_regalo == hoy_str) or (ingresos_hoy > 0)

        snapshot_changed = (abs(suma_regalos_hoy - last_sum) > 0.005) or (count_regalos_hoy != last_count)

        if es_nuevo_hoy and snapshot_changed:
            try:
                datos.last_regalos_notif_date = hoy_str
                datos.last_regalos_notif_sum = suma_regalos_hoy
                datos.last_regalos_notif_count = count_regalos_hoy
                datos.save_data()
            except Exception:
                pass

            return ("¡ESA ES MI BROTHER, LAS INVERSIONES DANDO FRUTO B-)!\n\n"
                    "Ese es puro sudor convertido en billetes reales.\n"
                    "¡Sigue camellando así que de ley coronamos la play! :D"), 'acierto.mp3'

    if any(anal.get('es_imprevisto') for anal in pecados_analysis):
        return ("Chuzo mi pana, se registró un gasto imprevisto / necesario.\n"
                "Detecté una enfermedad o una nota fea D:\n"
                "Espero que te recuperes rápido tú o quien sea, ¡fuerza bro! :)"), 'alerta.wav'

    # --- BLOQUE: EL CONFESIONARIO (SISTEMA DE ESCALADA) ---
    if gasto_hoy > 0 and ahorrado < meta:
        if gasto_hoy <= 5.0:
            return (f"¿HABLA SERIO? ¿Te gastaste ${gasto_hoy:.2f} en hueva?\n"
                    f"¡NO SEAS ANIMAL OE, QUE CADA CENTAVITO CUENTA PAL RETO!\n"
                    f"Si sigues de manirroto te va a tocar jugar el GTA 6 en la play de tu vecino, ponte once."), 'pum.mp3'
        elif gasto_hoy <= 15.0:
            return (f"¡UY GATO, PONTE ONCE! ${gasto_hoy:.2f} tirados a la basura.\n"
                    f"Esa plata hoy eran ahorros serios, mañana va a ser puro arrepentimiento feo.\n"
                    f"¡Deja de gastar el billete en pendejadas, habla serio!"), 'pum.mp3'
        else:
            return (f"¡PECADO MORTAL DETECTADO D:!\n"
                    f"Te pasaste de verga, botaste ${gasto_hoy:.2f} hoy día.\n"
                    f"¡Tienes cero prioridades cholo, vas directo a quedarte coco liso!"), 'pum.mp3'

    # --- NUEVO BLOQUE: ALERTA / FELICITACIÓN SEGÚN VENTAS HOY vs CUOTA DIARIA ---
    try:
        ventas_hoy = 0.0
        regalos_hoy_list = getattr(datos, 'regalos_hoy', []) or []
        for idx, r in enumerate(regalos_hoy_list):
            anal = regalos_analysis[idx] if idx < len(regalos_analysis) else {}
            if anal.get('es_inversion'):
                try:
                    ventas_hoy += float(r.get('precio', 0.0) or 0.0)
                except Exception:
                    continue
    except Exception:
        ventas_hoy = float(getattr(datos, 'ingresos_hoy', 0.0) or 0.0)

    if cuota_diaria is not None and cuota_diaria != float('inf'):
        if ventas_hoy >= cuota_diaria and ventas_hoy > 0:
            return (f"¡QUÉ BUENA MI PANA, VENDISTE AZURRADO B-)!\n\n"
                    f"Hiciste ${ventas_hoy:.2f} hoy, con eso ya cubres la cuota diaria (${cuota_diaria:.2f}).\n"
                    f"Sigue así que de ley coronamos pronto esa PS5."), 'acierto.mp3'
        if ventas_hoy > 0 and ventas_hoy < cuota_diaria:
            if ventas_hoy < max(1.0, cuota_diaria * 0.10):
                return (f"¡PERO QUÉ MIERDA VENDISTE VE? ${ventas_hoy:.2f} hoy... esa farsa no alcanza ni pa' la cola negra con chifles.\n"
                        f"Te toca apretar el culo más o buscar otra chamba rápido, ya pues muévete."), 'pum.mp3'
            return (f"¡ALERTA EN LAS VENTAS, BRO! Hoy solo hiciste ${ventas_hoy:.2f},\n"
                    f"pero tu cuota diaria es de ${cuota_diaria:.2f}.\n"
                    f"Necesitas vender más o te toca meter de tu bolsillo para ahorrar la diferencia."), 'pum.mp3'

    # --- BLOQUE: GASTOS FIJOS, GASTOS NECESARIOS E INGRESOS POR REGALOS ---
    if salario and salario > 0:
        if total_gastos_fijos > salario * 0.5:
            return (f"¡EY OJO AHÍ! Tus gastos fijos mensuales ya suman ${total_gastos_fijos:.2f},\n"
                    f"eso ya es más de la mitad de tu sueldo (${salario:.2f}).\n"
                    f"Revisa bien tus deudas o servicios porque si no, no vas a poder ahorrar ni un centavo."), 'alerta.wav'

        if (total_gastos_fijos + total_pecados_hoy) > salario * 0.7:
            return (f"¡PELIGRO CHOLO! Entre gastos fijos (${total_gastos_fijos:.2f}) y gastos pendejos (${total_pecados_hoy:.2f})\n"
                    f"ya te estás tirando más del 70% de lo que ganas. ¡Ajusta esas prioridades ya o te quedas calvo!"), 'pum.mp3'

        if total_regalos_hoy > salario * 0.2:
            return (f"¡SUAVE AHÍ BROTHER! Hoy te gastaste/recibiste ${total_regalos_hoy:.2f} en puros regalos.\n"
                    f"Eso ya supera el 20% de tu sueldo (${salario:.2f}). No dejes que te desbarate el presupuesto."), 'pum.mp3'
    else:
        if ingresos_extra > 0:
            if ingresos_acumulados == 0 and ingresos_hoy > 0:
                return ("¡MANTENIDO DETECTADO JAJAJA XD!\n\n"
                        "Toda tu plata viene de puros regalos.\n"
                        "¡Agradece a tus panas y familia porque sin ellos te quedas sin play de por vida!"), 'pum.mp3'
            if any(a.get('es_inversion') for a in regalos_analysis) and ingresos_extra >= meta * 0.5:
                return ("¡Buen camello, mi brother! Gran parte de tu ingreso extra viene de tus ventas.\n"
                        "Vas por buen camino armando tu propio flujo de billetes."), 'acierto.mp3'

    # --- BLOQUE 5: NIVELES DE PROGRESO Y ANÁLISIS ESTRATÉGICO ---
    if ahorrado <= 1.99:
        if ahorrado < 0.01: msg = f"NIVEL: VACÍO TOTAL x_x\nCon ${ahorrado} no completas ni pa' una biela, cholo T_T."
        elif ahorrado < 0.05: msg = f"NIVEL: MISERIA -_-\nCon {ahorrado} centavitos no te compras ni un chifle, habla serio."
        elif ahorrado < 0.50: msg = f"NIVEL: HAMBRE T_T\nCon {ahorrado} ctvs no compras ni una empanada de viento pa' llenarte."
        else: msg = f"NIVEL: LIMPIO (._.)\nCon ${ahorrado:.2f} no nos alcanza ni pal encebollado con cola negra, qué dolor."

        if any(anal.get('es_inversion') for anal in regalos_analysis):
            msg += "\n¡Estás invirtiendo y ya se ven los badulaques! Sigue camellando duro."
        elif salario <= 0 and any(anal.get('es_inversion') for anal in pecados_analysis):
            msg += "\n¡Por fin te dignaste a invertir en algo productivo! Ya estás dejando de ser mendigo."
        elif dias < 60:
            msg += f"\n¡Chuzo, queda poquísimo tiempo y tú estás en cero!\n¡La máquina de afeitar te está llamando, coco liso T_T!"
        elif salario <= 0:
            msg += "\n¡BUSCA CAMELLO, VAGO DE MIERDA! -_-\nSi no te mueves, te vas a quedar calvo y comiendo esa asquerosidad de pizza con piña."
        elif meses_trabajo <= 1.5 and salario > 0:
            msg += "\nEsperando ese primer pago, mi pana.\n¡Ahorra apenas cobres o te dejamos sin un pelo!"
        elif termina_antes and disponible_mes >= cuota:
            msg += f"\n¡Habla serio, derrochador! Con ${disponible_mes:.2f} libres,\nen apenas {meses_fast:.1f} meses ya coronarías la play -_-"
        else:
            msg += f"\nPero tranki brother, todavía nos quedan {dias} días.\n¡Mueve ese culo y ahorra!"
        
        return msg, 'pum.mp3'

    if porcentaje < 30:
        if dias < 60:
            return f"¡PELIGRO MÁXIMO! [{porcentaje:.1f}%]. [PIZZA CON PIÑA]\n¡La pizza ya está saliendo del horno, qué asco D:! ¡Ponte once!", 'pum.mp3'
        elif salario <= 0:
            if any(anal.get('es_inversion') for anal in regalos_analysis):
                return f"PELIGRO [{porcentaje:.1f}%].\nTienes billete de las ventas.\n¡Sigue metiéndole harto la mano!", 'acierto.mp3'
            return f"¡PELIGRO MÁXIMO! [{porcentaje:.1f}%].\n¡BUSCA CAMELLO, VAGO DE MIERDA! -_-\nO te quedas calvo y tragando pizza con piña.", 'pum.mp3'
        elif meses_trabajo <= 1.5 and salario > 0:
            if ahorrado >= disponible_mes * 0.70:
                return f"INICIO [{porcentaje:.1f}%].\n¡Esa es, primer sueldo bien guardado y ahorrado, bro! :D", 'acierto.mp3'
            else:
                return f"INICIO [{porcentaje:.1f}%].\nAsumo que aún no cobras o te estás tragando la plata en pendejadas...\n¡YA PONTE PILAS -_-!", 'pum.mp3'
        elif termina_antes:
            return f"PELIGRO MÁXIMO [{porcentaje:.1f}%].\nDeja de gastar como loco, con lo que te queda libre\npodrías terminar en {meses_fast:.1f} meses. No seas soso.", 'pum.mp3'
        elif disponible_mes >= cuota:
            return f"PELIGRO MÁXIMO [{porcentaje:.1f}%].\nTienes sueldo fijo, así que muévete huevón, no te duermas.", 'pum.mp3'
        else:
            return f"PELIGRO MÁXIMO [{porcentaje:.1f}%].\nLa cuota está altísima... ¡VE PREPARANDO EL COCO LISO!.", 'pum.mp3'

    if porcentaje < 70:
        if dias < 60 or (cuota > disponible_mes and salario > 0):
            return f"A MEDIA LLAVE, BRO [{porcentaje:.1f}%] o_o\nPero si te dejas estar, te va a tocar la rapada por atrasado igual -_-", 'pum.mp3'
        elif salario <= 0:
            if any(anal.get('es_inversion') for anal in regalos_analysis):
                return f"A MEDIA LLAVE, BRO [{porcentaje:.1f}%] o_o\n¡Esas inversiones están funcionando! Nada de andar de mendigo pidón.", 'acierto.mp3'
            return f"A MEDIA LLAVE, BRO [{porcentaje:.1f}%] o_o\nNo tienes sueldo fijo, ¡O BUSCAS CAMELLO RÁPIDO O DESPÍDETE DE TU CABELLO!", 'pum.mp3'
        elif termina_antes:
            return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\nCon tus ${disponible_mes:.2f} libres podrías\nterminar en {meses_fast:.1f} meses. ¡Métele nitro!", 'alerta.wav'
        elif disponible_mes >= cuota and dias > 120:
            return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\nUff, si seguimos así, ¡de que coronamos, coronamos! :D", 'alerta.wav'
        else:
            return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\n¡Dale duro que todavía falta bastante camello! T_T", 'alerta.wav'

    if dias < 30 and disponible_mes < cuota:
        return f"¡YA CASI CORONAMOS! [{porcentaje:.1f}%] --->\nPero el tiempo nos está respirando en la nuca, ¡ponte once! D:", 'alerta.wav'
    
    return f"¡YA CASI CORONAMOS! [{porcentaje:.1f}%] --->\nYa huelo el plástico nuevo de la PS5 y la caja del GTA 6, qué delicia :D", 'acierto.mp3'
    