# io_utils.py
# Utilidades de E/S: guardado atómico, exportar/importar y ruta de exportación

import json
import os
import shutil
from typing import Tuple

def atomic_write_json(path: str, data: dict, indent: int = 4, ensure_ascii: bool = False) -> bool:
    """
    Escribe JSON de forma atómica: escribe a archivo temporal y reemplaza.
    Devuelve True si tuvo éxito.
    """
    temp_path = path + ".tmp"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        os.replace(temp_path, path)
        return True
    except Exception:
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
            return True
        except Exception:
            return False

def obtener_ruta_exportacion(base_dir: str, platform_name: str = None) -> str:
    """
    Devuelve la carpeta donde exportar/importar JSON.
    Si platform_name == 'android' usa ruta de descargas típica.
    """
    if platform_name == 'android':
        export_dir = "/storage/emulated/0/Download/JSON exportados"
    else:
        export_dir = os.path.join(base_dir, "JSON exportados")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir

def exportar_json(data_file: str, nombre_archivo: str, base_dir: str, platform_name: str = None) -> Tuple[bool, str]:
    carpeta_destino = obtener_ruta_exportacion(base_dir, platform_name)
    if not nombre_archivo.endswith('.json'):
        nombre_archivo += '.json'
    ruta_final = os.path.join(carpeta_destino, nombre_archivo)
    try:
        shutil.copy2(data_file, ruta_final)
        return True, f"Datos exportados en:\n{ruta_final}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def compartir_json_nativo(data_file: str) -> Tuple[bool, str]:
    """
    NUEVO: Abre el menú nativo de Android para compartir el JSON a WhatsApp, Drive, etc.
    """
    try:
        from plyer import share
        share.share(path=data_file)
        return True, "Abriendo menú de compartir... Envíalo a Drive, Telegram o WhatsApp B-)"
    except Exception as e:
        return False, f"No se pudo abrir el menú de compartir: {str(e)}"

def importar_json(ruta_origen: str, destino: str) -> Tuple[bool, str]:
    """
    Valida estructura mínima y copia el JSON a destino.
    """
    try:
        with open(ruta_origen, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'productos' not in data:
                return False, "JSON inválido."
        shutil.copy2(ruta_origen, destino)
        return True, "Importado con éxito."
    except Exception as e:
        return False, f"Error: {str(e)}"
        