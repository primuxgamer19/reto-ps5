# debug/init_debug.py
"""
Inicializa funcionalidades de debugging globales:
- hook global de excepciones
- redirección de stdout/stderr al logger de debug
- exporta init_debug(app_ref) para inicializar desde debug/main_debug.py

Este módulo debe residir únicamente en debug/ y no importarse desde la lógica
principal para evitar incluirlo en builds de release.
"""
import sys
import os
import traceback
import datetime
import logging
from typing import Optional

try:
    # Importar la utilidad de logging específica de debug (esta está en debug/)
    from .notificaciones_debug import notif_debug
except Exception:
    notif_debug = None


class StreamToDebugLogger:
    """Redirige writes a un logger de debug."""
    def __init__(self, level=logging.INFO):
        self.level = level

    def write(self, buf):
        if not buf:
            return
        # dividir en líneas y loguear cada una
        for line in buf.rstrip().splitlines():
            try:
                if notif_debug and getattr(notif_debug, 'logger', None):
                    notif_debug.logger.log(self.level, line)
                elif notif_debug:
                    # fallback raw
                    notif_debug._write_raw(f"[STDOUT] {line}")
                else:
                    # última vía: imprimir en stderr para que el entorno la capture
                    sys.__stderr__.write(line + "\n")
            except Exception:
                try:
                    sys.__stderr__.write(line + "\n")
                except Exception:
                    pass

    def flush(self):
        pass


_app_ref = None


def _handle_uncaught_exception(exc_type, exc_value, exc_tb):
    """Hook global para excepciones no capturadas."""
    # Dejar que KeyboardInterrupt pase normalmente
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    msg = f"Uncaught exception: {exc_value}\n{tb_text}"

    # Loguear via notif_debug si está disponible
    try:
        if notif_debug:
            notif_debug.log_error('Uncaught exception', {'exc': str(exc_value), 'traceback': tb_text})
            # Adicional: dump del estado de la app si tenemos referencia
            if _app_ref is not None:
                try:
                    from .ui_debug_overlay import dump_state_to_file
                    dump_path = dump_state_to_file(_app_ref)
                    notif_debug.log_info('Estado volcado por excepción', {'dump_path': dump_path})
                except Exception as e:
                    notif_debug.log_warning('No se pudo volcar estado en excepción', {'error': str(e)})
        else:
            # Escribir en un archivo de fallback dentro de debug/resources/data
            fallback_dir = os.path.join('debug', 'resources', 'data')
            os.makedirs(fallback_dir, exist_ok=True)
            fallback_file = os.path.join(fallback_dir, f'uncaught_{ts}.log')
            with open(fallback_file, 'w', encoding='utf-8') as f:
                f.write(msg)
    except Exception:
        # última vía: imprimir en stderr
        try:
            sys.__stderr__.write(msg + '\n')
        except Exception:
            pass


def init_debug(app_ref: Optional[object] = None):
    """Inicializa el entorno de debug.

    - Registra sys.excepthook
    - Redirige stdout/stderr
    - Guarda la referencia a la app para dump de estado
    """
    global _app_ref
    _app_ref = app_ref

    # Hook global de excepciones
    sys.excepthook = _handle_uncaught_exception

    # Redirigir stdout/stderr si no están ya redirigidos
    try:
        sys.stdout = StreamToDebugLogger(level=logging.INFO)
        sys.stderr = StreamToDebugLogger(level=logging.ERROR)
    except Exception:
        pass

    # Informar en logs
    try:
        if notif_debug:
            notif_debug.log_info('Init debug inicializado', {'has_app_ref': bool(app_ref)})
    except Exception:
        pass


# Permitir uso directo: al importar e invocar init_debug() desde main_debug.py
if __name__ == '__main__':
    print('init_debug: ejecutar desde debug/main_debug.py con init_debug(app)')
