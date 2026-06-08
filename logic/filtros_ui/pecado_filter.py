# logic/filtros_ui/pecado_filter.py
# Patrones para la UI de Pecados (gastos innecesarios / vicios)

weights = {
    'pecado_fraude': {
        r'cerve[sz]as?': 5, r'serbe[sz]as?': 5, r'bielas?': 5, r'chelas?': 5,
        r'pilsener': 5, r'club': 5, r'birra': 5, r'ron': 5, r'tragos?': 5,
        r'whisky': 5, r'vino': 5, r'caña': 5, r'alcohol': 5, r'guaro': 5, r'licor': 5,
        r'comidas?': 4, r'almuerzos?': 4, r'cenas?': 4, r'desayunos?': 4,
        r'restaurantes?': 5, r'hamburguesas?': 5, r'pizzas?': 5, r'mcdonalds?': 5,
        r'kfc': 5, r'burgers?': 5, r'tacos?': 5, r'chifa': 5, r'hornado': 5,
        r'fritada': 5, r'gaseosa': 4, r'cola': 4,
        r'amig(?:o|a|uit|u|az)o?s?': 5, r'panas?': 5, r'brothers?': 5, r'bros?': 5,
        r'compas?': 5, r'rumba': 5, r'perreo': 5, r'parranda': 5, r'juerga': 5,
        r'vacilada': 5, r'fiestas?': 5, r'jodas?': 5, r'farras?': 5,
        r'salidas?': 5, r'saliditas?': 5, r'cines?': 4, r'pel[ií]culas?': 4,
        r'netflix': 4, r'vapes?': 5, r'tabacos?': 5, r'cigarros?': 5, r'fumar': 5,
        r'porro': 6, r'mari': 6, r'discotecas?': 5, r'bares?': 5,
        r'juegos?': 4, r'videojuegos?': 5, r'ps[45]': 6, r'xbox': 6, r'nintendo': 5,
        r'consola': 6, r'steam': 5, r'psn': 5, r'skins?': 5, r'pavos?': 5,
        r'robux': 5, r'diamantes?': 5, r'twitch': 4,
        r'iphone': 6, r'samsung': 5, r'laptop': 5, r'computadora': 5,
        r'tenis': 5, r'zapatillas?': 5, r'outfit': 5, r'ropa de marca': 5,
        r'viaj(?:e|es)': 6, r'vacacion(?:es)?': 6, r'hotel': 5, r'resort': 5,
        r'carro': 6, r'auto': 6, r'moto': 6,
        r'apuestas?': 5, r'casinos?': 5,
        r'compr[óe]': 3, r'me compr': 4, r'gasto': 3
    }
}