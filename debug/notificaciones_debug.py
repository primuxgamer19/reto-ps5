# Debug: NotificacionesDebugger
# Este módulo contiene utilidades de debug que se cargan sólo desde la carpeta debug/

import datetime
import json
import os
from pathlib import Path
import traceback
import logging
from logging.handlers import RotatingFileHandler


class NotificacionesDebugger:
    """
    Herramienta para debuggear y loguear el sistema de notificaciones.
    Logs y archivos asociados quedan dentro de debug/resources/data/ para
    no ensuciar la raíz del proyecto.
    """

    def __init__(self, base_debug_dir: str = 'debug/resources/data'):
        self.base_debug_dir = base_debug_dir
        self.log_file = Path(self.base_debug_dir) / 'notificaciones_debug.log'
        self.ensure_log_file()
        self._configure_rotating_logger()

    def ensure_log_file(self):
        """Crea el archivo de log si no existe (y la carpeta padre)."""
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            if not self.log_file.exists():
                self.log_file.write_text('', encoding='utf-8')
        except Exception as e:
            print(f"Error creando archivo de debug: {e}")

    def _configure_rotating_logger(self):
        try:
            self.logger = logging.getLogger('debug_notif')
            if not self.logger.handlers:
                handler = RotatingFileHandler(str(self.log_file), maxBytes=5_000_000, backupCount=3, encoding='utf-8')
                fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
                handler.setFormatter(fmt)
                self.logger.setLevel(logging.DEBUG)
                self.logger.addHandler(handler)
        except Exception as e:
            print(f"No se pudo configurar RotatingFileHandler: {e}")
            self.logger = None

    def _write_raw(self, entry: str):
        try:
            # Escribir con encoding explicito
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(entry + '\n')
        except Exception as e:
            print(f"Error escribiendo en log debug: {e}")

    def log(self, level: str, message: str, extra_data: dict = None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        if extra_data:
            try:
                log_entry += f" | {json.dumps(extra_data, ensure_ascii=False)}"
            except Exception:
                log_entry += f" | extra_data_unserializable"

        # Intentar logger rotativo, si no usar escritura directa
        try:
            if self.logger:
                if level == 'DEBUG':
                    self.logger.debug(message + (f" | {extra_data}" if extra_data else ""))
                elif level == 'INFO':
                    self.logger.info(message + (f" | {extra_data}" if extra_data else ""))
                elif level == 'WARNING':
                    self.logger.warning(message + (f" | {extra_data}" if extra_data else ""))
                elif level == 'ERROR':
                    self.logger.error(message + (f" | {extra_data}" if extra_data else ""))
                else:
                    self.logger.info(message + (f" | {extra_data}" if extra_data else ""))
            else:
                self._write_raw(log_entry)
        except Exception:
            # Fallback: escribir raw
            self._write_raw(log_entry)

    def log_info(self, message: str, extra_data: dict = None):
        self.log('INFO', message, extra_data)

    def log_warning(self, message: str, extra_data: dict = None):
        self.log('WARNING', message, extra_data)

    def log_error(self, message: str, extra_data: dict = None):
        # Incluir traceback si se pasa una excepción en extra_data
        if extra_data and isinstance(extra_data.get('exc'), Exception):
            tb = traceback.format_exc()
            extra_data = dict(extra_data)
            extra_data['traceback'] = tb
        self.log('ERROR', message, extra_data)

    def log_debug(self, message: str, extra_data: dict = None):
        self.log('DEBUG', message, extra_data)

    def dump_config(self, datos_ref):
        try:
            cfg = datos_ref.get_config()
            self.log_info("DUMP DE CONFIGURACIÓN DE NOTIFICACIONES", {
                "habilitadas": cfg.get("enabled"),
                "total_entradas": len(cfg.get("entries", [])),
                "ultima_enviada": cfg.get("last_sent", ""),
            })
        except Exception as e:
            self.log_error(f"Error dumpando config: {e}", {"exc": e})

    def clear_log(self):
        try:
            self.log_file.write_text('', encoding='utf-8')
            self.log_info('LOG LIMPIADO')
        except Exception as e:
            print(f"Error limpiando log: {e}")

    def get_recent_logs(self, lines: int = 20) -> list:
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            return all_lines[-lines:]
        except Exception:
            return []

    def print_logs(self, lines: int = 50):
        logs = self.get_recent_logs(lines)
        print('\n=== NOTIFICACIONES DEBUG LOG ===')
        for log in logs:
            print(log.rstrip())
        print('================================\n')


# Instancia global para usar desde debug/ solamente
notif_debug = NotificacionesDebugger()
