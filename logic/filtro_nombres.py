# logic/filtro_nombres.py
"""
Puente que mantiene la API original y delega listas/pesos a módulos por UI.
Mejoras añadidas:
 - Validación de regex
 - Fusión segura de patrones (suma con tope)
 - Soporte de 'keywords' por UI (listas largas)
 - Fuzzy matching (difflib) para errores ortográficos
 - Conserva la lógica central de resolución de conflictos y sugerencias
"""
import re
import difflib
import logging
from typing import List, Dict, Any
from .filtros_ui import regalo_filter, pecado_filter, gasto_fijo_filter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MAX_WEIGHT_PER_PATTERN = 20
FUZZY_THRESHOLD = 0.82  # umbral para considerar coincidencia difusa
FUZZY_TOKEN_MIN_LEN = 3

class FiltroNombres:
    def __init__(self):
        # Stop words reducidas (mantener 'para' y 'mi' para detectar auto-consumo)
        self.stop_words = [
            'un', 'una', 'el', 'la', 'los', 'las', 'de', 'del', 'con',
            'por', 'en', 'es', 'son', 'su', 'sus', 'y', 'o', 'al'
        ]

        # Frases de auto-consumo
        self.frases_fraude = [
            r'\bpara mi\b', r'\bpa mi\b', r'\bpa mí\b', r'\bpara mí\b',
            r'\bme lo merezco\b', r'\bantojo\b', r'\bgustito\b', r'\bgusto\b',
            r'\bsolo por hoy\b', r'\bpara la casa\b', r'\bpara probar\b',
            r'\bporque quiero\b', r'\bme gusta\b', r'\bcapricho\b',
            r'\bme di un gusto\b', r'\bjusto lo que necesitaba\b', r'\bpor fin\b'
        ]

        # Negaciones
        self.negations = [r'\bno\b', r'\bnunca\b', r'\bjam[aá]s\b', r'\btampoco\b', r'\bni\b']

        # Estructura de pesos (categorías)
        self.weights = {
            'inversion': {},
            'regalo_caridad': {},
            'imprevisto': {},
            'pecado_fraude': {}
        }

        # Cargar módulos y fusionar (patrones + keywords)
        self._load_and_validate_modules()

    # -------------------------
    # Carga, validación y fusión
    # -------------------------
    def _load_and_validate_modules(self):
        modules = [regalo_filter, pecado_filter, gasto_fijo_filter]
        raw_patterns = {}  # categoria -> {pattern: weight_sum}

        for mod in modules:
            mod_weights = getattr(mod, 'weights', {})
            mod_keywords = getattr(mod, 'keywords', {})

            # Procesar pesos explícitos (regex -> weight)
            for categoria, patrones in mod_weights.items():
                raw_patterns.setdefault(categoria, {})
                for patron, peso in patrones.items():
                    key = patron if isinstance(patron, str) else str(patron)
                    if not self._is_valid_regex(key):
                        logger.warning("Patrón inválido ignorado: %s (módulo: %s)", key, getattr(mod, '__name__', 'unknown'))
                        continue
                    prev = raw_patterns[categoria].get(key, 0)
                    new = min(prev + int(peso), MAX_WEIGHT_PER_PATTERN)
                    raw_patterns[categoria][key] = new

            # Procesar keywords (listas largas). Convertir cada keyword a patrón escapado y asignar peso base.
            for categoria, kw_list in mod_keywords.items():
                raw_patterns.setdefault(categoria, {})
                for kw in kw_list:
                    key = re.escape(kw.strip().lower())
                    # peso base para keywords (puede ajustarse)
                    base_weight = 4
                    prev = raw_patterns[categoria].get(key, 0)
                    new = min(prev + base_weight, MAX_WEIGHT_PER_PATTERN)
                    raw_patterns[categoria][key] = new

        # Asignar a self.weights
        for categoria, pats in raw_patterns.items():
            self.weights[categoria] = pats

        logger.info("Pesos y keywords cargados. Categorías: %s", ", ".join(self.weights.keys()))

    def _is_valid_regex(self, pattern: str) -> bool:
        try:
            re.compile(pattern)
            return True
        except re.error:
            try:
                re.compile(re.escape(pattern))
                return True
            except re.error:
                return False

    # -------------------------
    # Utilidades de limpieza
    # -------------------------
    def _limpiar_texto_basico(self, texto: str) -> str:
        texto = texto.lower().strip()
        # Normalizar acentos básicos
        replacements = {
            'á':'a','é':'e','í':'i','ó':'o','ú':'u','ñ':'n','ü':'u'
        }
        for a,b in replacements.items():
            texto = texto.replace(a,b)
        texto_limpio = re.sub(r'[^\w\s]', ' ', texto)
        # colapsar espacios
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        return " " + texto_limpio + " "

    def _limpiar_y_tokenizar(self, texto: str) -> List[str]:
        palabras = texto.split()
        return [p for p in palabras if p not in self.stop_words]

    # -------------------------
    # Fuzzy helpers
    # -------------------------
    def _fuzzy_match_tokens(self, tokens: List[str], keyword_list: List[str]) -> List[tuple]:
        """
        Devuelve lista de (token, matched_keyword, score) para coincidencias difusas.
        """
        matches = []
        # usar get_close_matches por token contra la lista de keywords
        for t in tokens:
            if len(t) < FUZZY_TOKEN_MIN_LEN:
                continue
            # get_close_matches devuelve strings; calcular ratio con difflib.SequenceMatcher
            close = difflib.get_close_matches(t, keyword_list, n=3, cutoff=FUZZY_THRESHOLD)
            for c in close:
                score = difflib.SequenceMatcher(None, t, c).ratio()
                matches.append((t, c, score))
        return matches

    # -------------------------
    # Lógica de análisis (mantiene comportamiento original)
    # -------------------------
    def analizar(self, nombre: str) -> Dict[str, Any]:
        if not nombre or not isinstance(nombre, str):
            return self._resultado_vacio(nombre)

        texto_crudo = self._limpiar_texto_basico(nombre)
        palabras_utiles = self._limpiar_y_tokenizar(texto_crudo)
        texto_procesado = " " + " ".join(palabras_utiles) + " "

        scores = {'inversion': 0, 'regalo_caridad': 0, 'imprevisto': 0, 'pecado_fraude': 0}

        # 1. EJECUCIÓN DE PESOS (patrones exactos / escapados)
        for categoria, patrones in self.weights.items():
            for patron, peso in patrones.items():
                try:
                    # patron ya está escapado o es regex válido
                    if re.search(rf"\b{patron}\b", texto_procesado):
                        scores[categoria] += peso
                except re.error:
                    # fallback: buscar literal
                    if re.search(re.escape(patron), texto_procesado):
                        scores[categoria] += peso

        # 1b. Fuzzy matching: construir lista de keywords por categoría (sin escapes)
        categoria_keywords = {}
        for cat, pats in self.weights.items():
            # convertir patrones escapados a palabras simples si posible
            kw_list = []
            for p in pats.keys():
                try:
                    # intentar unescape simple
                    unescaped = re.sub(r'\\', '', p)
                    # tomar tokens de la pattern
                    tokens = re.findall(r'[a-z0-9áéíóúñü]+', unescaped)
                    for tk in tokens:
                        if len(tk) >= FUZZY_TOKEN_MIN_LEN:
                            kw_list.append(tk)
                except Exception:
                    continue
            categoria_keywords[cat] = list(set(kw_list))

        # aplicar fuzzy matching por tokens
        for cat, kw_list in categoria_keywords.items():
            if not kw_list:
                continue
            fuzzy_matches = self._fuzzy_match_tokens(palabras_utiles, kw_list)
            for token, matched_kw, score in fuzzy_matches:
                # peso proporcional al score (ej: base 4 * score)
                add = int(round(4 * score))
                scores[cat] += add

        # 2. DETECCIÓN DE AUTO-CONSUMO INTELIGENTE
        es_auto_consumo = False
        for frase in self.frases_fraude:
            if re.search(frase, texto_crudo):
                es_auto_consumo = True
                break

        # NO penalizar "para mi" si es regalo a familia
        family_pattern = r'\b(mama|mama|papa|madre|padre|herman|hij|novi|espos|pareja|familia)\b'
        if es_auto_consumo and re.search(family_pattern, texto_crudo):
            es_auto_consumo = False

        if es_auto_consumo:
            scores['inversion'] = 0
            scores['pecado_fraude'] += 20

        # 3. RESOLUCIÓN DE CONFLICTOS (Inversión vs Pecado)
        if scores['inversion'] > 0 and scores['pecado_fraude'] > 0:
            tiene_intencion_venta = re.search(
                r'\b(vender|venta|ventas|vend[ií]|vend(?:ido|ida|idas?|iendo)|clientes?|revender|tienda|local|negocio|emprend|ganancia|gane|gane|chambe|para vender|para revender)\b',
                texto_procesado
            )
            if not tiene_intencion_venta:
                scores['inversion'] = 0
                scores['pecado_fraude'] += 15
            else:
                scores['pecado_fraude'] = 0

        # 4. PENALIZACIÓN SOCIAL (solo si NO es regalo)
        if scores['regalo_caridad'] == 0 and re.search(r'\b(amig|amigo|amiga|panas|brothers|bros|compas)\b', texto_procesado):
            scores['pecado_fraude'] += 10

        # 5. DETECCIÓN DE NEGACIÓN
        tiene_negacion = any(re.search(n, texto_procesado) for n in self.negations)

        # 6. CLASIFICACIÓN FINAL
        categorias_activas = {k: v for k, v in scores.items() if v > 0}

        if not categorias_activas:
            tipo = 'normal'
            sugerencia = None
        else:
            tipo_ganador = max(categorias_activas, key=categorias_activas.get)

            if tiene_negacion and tipo_ganador == 'pecado_fraude':
                tipo = 'normal'
                sugerencia = "Dices que no es pecado... te daré el beneficio de la duda esta vez."
            else:
                tipo = tipo_ganador

                if es_auto_consumo and scores['pecado_fraude'] > 10:
                    sugerencia = "¡INTENTO DE FRAUDE! Poner 'para mi' o excusas baratas te delata."
                elif tipo == 'pecado_fraude' and scores.get('inversion', 0) == 0 and 'inver' in texto_crudo:
                    sugerencia = "¡MENTIROSO! Eso no es inversión si no lo vas a vender. ¡Al confesionario!"
                elif tipo == 'inversion':
                    sugerencia = "¡Inversión legítima detectada! Así se construye el imperio."
                elif tipo == 'imprevisto':
                    sugerencia = "Gasto de salud o emergencia. Prioridad aceptada."
                elif tipo == 'regalo_caridad':
                    sugerencia = "Plata que llega de fuera. ¡Aprovéchala!"
                else:
                    sugerencia = "Gasto innecesario detectado. ¡Ten un poco de decencia!"

        return {
            'tipo': tipo,
            'es_inversion': tipo == 'inversion',
            'es_regalo_caridad': tipo == 'regalo_caridad',
            'es_imprevisto': tipo == 'imprevisto',
            'es_pecado_fraude': tipo == 'pecado_fraude' or (tipo == 'normal' and scores.get('pecado_fraude', 0) > 0),
            'sugerencia': sugerencia,
            'nombre_original': nombre,
            'scores': scores
        }

    def _resultado_vacio(self, nombre: Any) -> Dict[str, Any]:
        return {
            'tipo': 'desconocido',
            'es_inversion': False, 'es_regalo_caridad': False,
            'es_imprevisto': False, 'es_pecado_fraude': False,
            'sugerencia': None, 'nombre_original': nombre, 'scores': {}
        }

    def analizar_lista(self, lista_items: List[Dict]) -> List[Dict[str, Any]]:
        return [self.analizar(item.get('nombre', '')) for item in lista_items]