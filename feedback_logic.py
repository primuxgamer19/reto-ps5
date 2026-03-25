# feedback_logic.py

import datetime

def obtener_feedback_msg(app, ahorrado, meta, dias, porcentaje, cuota):
    disponible_mes = app.salario - app.arriendo
    gasto_hoy = getattr(app, 'gasto_hoy', 0.0)
    
    meses_limite = max(1, dias / 30.0)
    if disponible_mes > 0:
        meses_fast = (meta - ahorrado) / disponible_mes
        termina_antes = meses_fast < meses_limite
    else:
        meses_fast = 9999
        termina_antes = False

    # Saber cuánto llevas camellando
    meses_trabajo = 999
    if getattr(app, 'fecha_salario', ""):
        try:
            f_sal = datetime.datetime.strptime(app.fecha_salario, "%Y-%m-%d").date()
            meses_trabajo = (datetime.date.today() - f_sal).days / 30.0
        except ValueError:
            pass

    # --- BLOQUE 1: EASTER EGGS Y TROLEOS FIJOS ---
    if ahorrado > 10000: return "¡Ni tu te lo crees! XD\n¿Robaste un banco o que?", 'pum.mp3'
    if ahorrado == 666: return "¿$666? ¡El diablo Bro o_O!", 'pum.mp3'
    if ahorrado == 777: return "¿$777? ¡Hey muy buenas a todos, Guapisimos!\nB-)", 'acierto.mp3'
    if 0 < ahorrado < 0.0001: return "POBREZA MOLECULAR DETECTADA.\n¡No trolees y busca camello! xd", 'pum.mp3'
    if ahorrado == 67: return "ni se te ocurra decirlo... -_-", 'alerta.wav'

    # --- BLOQUE 2: HUECOS LÓGICOS CREADOS POR TI ---
    if app.arriendo > app.salario:
        return f"¿Pagas más de arriendo que de salario?\n¿A quién le debes plata? Ya ponte serio -_-", 'pum.mp3'
    
    if app.salario <= 0 and ahorrado >= meta:
        return f"¡Ni tu te lo crees! XD\nSin camello y ya tienes la plata...\n¿A quien atracaste bro? -_-", 'pum.mp3'

    if app.salario <= 0 and porcentaje >= 50 and ahorrado < meta:
        return f"¡Ni tu te lo crees! XD\nSin camello y ya tienes ${ahorrado}?\n¿A quien atracaste bro?", 'pum.mp3'

    # --- BLOQUE 3: METAS Y CASTIGOS FINALES ---
    if ahorrado >= meta:
        return "¡LO LOGRASTE! B-)\nLa PS5 es tuya. ¡A viciar!", 'Alelulla.wav'

    if dias <= 0:
        return f"¡RETO PERDIDO! F en el chat.\nTe pasaste {-dias} dias de la fecha\ny sigues pobre. ¡A RAPARSE!", 'pum.mp3'

    # --- BLOQUE 4: PECADO MORTAL ACTIVO ---
    if gasto_hoy > 0 and ahorrado < meta:
        return f"PECADO MORTAL DETECTADO D:\nTiraste a la basura ${gasto_hoy:.2f} hoy.\n¡Cero prioridades, te pasas de verga!", 'pum.mp3'

    # --- BLOQUE 5: CONSTRUCCIÓN MODULAR DE NIVELES ---
    if ahorrado <= 1.99:
        if ahorrado < 0.01: msg = f"NIVEL: VACIO TOTAL x_x\nCon ${ahorrado} no pagas ni caca T_T."
        elif ahorrado < 0.05: msg = f"NIVEL: MISERIA -_-\nCon {ahorrado} ctvs no compras ni chicle."
        elif ahorrado < 0.50: msg = f"NIVEL: HAMBRE T_T\nCon {ahorrado} ctvs no compras ni una empanada de aire."
        else: msg = f"NIVEL: LIMPIO (._.)\nCon ${ahorrado:.2f} no alcanza ni pal encebollado."

        if dias < 60: 
            msg += f"\n¡Queda poco tiempo y tu en cero!\nLa maquina de afeitar te espera T_T"
        elif app.salario <= 0:
            msg += "\n¡BUSCA CAMELLO VAGO! -_-\nSi no, te quedas calvo y comiendo pizza con piña."
        elif meses_trabajo <= 1.5 and app.salario > 0:
            # Aquí te evito la puteada porque tienes menos de 2 dolares
            msg += "\nEsperando ese primer pago bro.\n¡Ahorra cuando cobres o te quedas calvo!"
        elif termina_antes and disponible_mes >= cuota: 
            msg += f"\n¡Habla serio derrochador! Con ${disponible_mes:.2f} libres,\nen {meses_fast:.1f} meses coronarías -_-"
        elif disponible_mes > 0 and disponible_mes >= cuota: 
            msg += "\n¡Oye ponte serio con el ahorro\ny no seas atragantado!"
        elif disponible_mes > 0 and disponible_mes < cuota: 
            msg += "\n¡Ya se acaba el tiempo y tu sueldo\nno alcanza! Busca extras o te quedas calvo D:"
        else: 
            msg += f"\nPero tranki, faltan {dias} dias.\n¡Mueve ese culo y ahorra!"
        
        return msg, 'pum.mp3'

    if porcentaje < 30:
        if dias < 60: return f"PELIGRO MAXIMO [{porcentaje:.1f}%]. [PIZZA CON PIÑA]\n¡La pizza ya salio del horno D:!", 'pum.mp3'
        elif app.salario <= 0: return f"PELIGRO MAXIMO [{porcentaje:.1f}%].\n¡BUSCA CAMELLO VAGO! -_-\nSi no, te quedas calvo y comiendo pizza con piña.", 'pum.mp3'
        
        # AQUÍ ESTÁ LA LÓGICA DEL 70% QUE ME PEDISTE
        elif meses_trabajo <= 1.5 and app.salario > 0: 
            if ahorrado >= disponible_mes * 0.70:
                return f"INICIO [{porcentaje:.1f}%].\n¡Primer sueldo bien ahorrado bro! :D", 'acierto.mp3'
            else:
                return f"INICIO [{porcentaje:.1f}%].\nAsumo que aun no cobras o te tragas la plata...\n¡YA PONTE SERIO -_-!", 'pum.mp3'
                
        elif termina_antes: return f"PELIGRO MAXIMO [{porcentaje:.1f}%].\nDeja de gastar a lo loco, con tu billete\nlibre podrias terminar en {meses_fast:.1f} meses.", 'pum.mp3'
        elif disponible_mes >= cuota: return f"PELIGRO MAXIMO [{porcentaje:.1f}%].\nTienes sueldo, asi que apurate huevon.", 'pum.mp3'
        else: return f"PELIGRO MAXIMO [{porcentaje:.1f}%].\nLa cuota es alta ¡PREPARA EL COCO!.", 'pum.mp3'

    if porcentaje < 70:
        if dias < 60 or (cuota > disponible_mes and app.salario > 0): return f"A MEDIA BRO [{porcentaje:.1f}%] o_o\nPero igual te tocara rapada por atrasado -_-", 'pum.mp3'
        elif app.salario <= 0: return f"A MEDIA BRO [{porcentaje:.1f}%] o_o\nNo tienes sueldo, ¡BUSCA CAMELLO o despídete de tu pelo!", 'pum.mp3'
        elif termina_antes: return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\nCon tus ${disponible_mes:.2f} libres podrias\nterminar en {meses_fast:.1f} meses ¡Dale!", 'alerta.wav'
        elif disponible_mes >= cuota and dias > 120: return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\nUff de que lo logras lo logras :D", 'alerta.wav'
        else: return f"A MEDIA LLAVE [{porcentaje:.1f}%]. (o_o)\n¡Dale que falta camello! T_T", 'alerta.wav'

    if dias < 30 and disponible_mes < cuota:
        return f"¡CASI AHI! [{porcentaje:.1f}%] --->\nPero el tiempo respira en tu nuca D:", 'alerta.wav'
    
    return f"¡CASI AHI! [{porcentaje:.1f}%] --->\nYa huelo el plastico nuevo :D", 'acierto.mp3'
