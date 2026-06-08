# io_utils.py
# Utilidades de E/S: guardado atómico, exportar/importar y ruta de exportación

import json
import os
import shutil
import time
import re
from typing import Tuple


def atomic_write_json(path: str, data: dict, indent: int = 4, ensure_ascii: bool = False) -> bool:
    """
    Escribe JSON de forma atómica: escribe a archivo temporal y reemplaza.
    - Asegura existencia del directorio
    - Hace flush + fsync antes de reemplazar
    - Limpia el .tmp en caso de fallo
    Devuelve True si tuvo éxito.
    """
    dirpath = os.path.dirname(path) or '.'
    os.makedirs(dirpath, exist_ok=True)
    temp_path = path + ".tmp"
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path)
        return True
    except Exception:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass
        # Intentar escribir de forma no-atomica como fallback
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


def _make_safe_filename(name: str) -> str:
    """Sanea un nombre de archivo evitando caracteres inválidos."""
    name = (name or '').strip()
    # Eliminar caracteres problemáticos en Windows/Android
    name = re.sub(r'[\\/:"*?<>|]+', '_', name)
    if not name.lower().endswith('.json'):
        name += '.json'
    # Limitar longitud razonable
    return name[:200]


def exportar_json(data_file: str, nombre_archivo: str, base_dir: str, platform_name: str = None) -> Tuple[bool, str]:
    """
    Copia el archivo de datos a la carpeta de exportación o devuelve mensaje de error claro.
    - Sanitiza el nombre de archivo
    - Si el destino existe, añade sufijo con timestamp en vez de sobrescribir
    """
    if not os.path.exists(data_file):
        return False, f"Error: archivo de datos no encontrado: {data_file}"

    carpeta_destino = obtener_ruta_exportacion(base_dir, platform_name)
    safe_name = _make_safe_filename(nombre_archivo)
    ruta_final = os.path.join(carpeta_destino, safe_name)

    # Si existe, añadir sufijo timestamp
    if os.path.exists(ruta_final):
        ts = time.strftime('%Y%m%d_%H%M%S')
        base, ext = os.path.splitext(safe_name)
        ruta_final = os.path.join(carpeta_destino, f"{base}_{ts}{ext}")

    try:
        shutil.copy2(data_file, ruta_final)
        return True, f"Datos exportados en:\n{ruta_final}"
    except Exception as e:
        return False, f"Error exportando archivo: {str(e)}"


def compartir_json_nativo(data_file: str) -> Tuple[bool, str]:
    """
    Abre el menú nativo de Android para compartir el JSON a WhatsApp, Drive, etc.
    Devuelve (True, mensaje) si la operación se inició correctamente.
    """
    try:
        from plyer import share
    except Exception as e:
        return False, f"Plyer.share no disponible: {e}"

    if not os.path.exists(data_file):
        return False, f"Archivo a compartir no encontrado: {data_file}"

    try:
        share.share(path=data_file)
        return True, "Abriendo menú de compartir... Envíalo a Drive, Telegram o WhatsApp :)"
    except Exception as e:
        # Devolver mensaje más informativo para el usuario
        return False, f"No se pudo abrir el menú de compartir: {str(e)}"


def importar_json(ruta_origen: str, destino: str) -> Tuple[bool, str]:
    """
    Valida estructura mínima y copia el JSON a destino.
    - Maneja errores concretos (archivo no encontrado, JSON malformado)
    - Comprueba claves requeridas para MotorDatos
    """
    required_keys = ['presupuesto', 'ingresos', 'gastos', 'notificaciones']

    try:
        with open(ruta_origen, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, "Archivo de origen no encontrado."
    except json.JSONDecodeError as e:
        return False, f"JSON malformado: {e}"
    except Exception as e:
        return False, f"Error abriendo el archivo: {e}"

    # Comprobar claves mínimas
    missing = [k for k in required_keys if k not in data]
    if missing:
        return False, f"JSON inválido: faltan claves {missing}."

    # Asegurar que la carpeta destino exista
    try:
        dest_dir = os.path.dirname(destino) or '.'
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(ruta_origen, destino)
        return True, "Importado con éxito."
    except Exception as e:
        return False, f"Error copiando archivo: {e}"
