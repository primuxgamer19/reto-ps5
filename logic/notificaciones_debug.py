# logic/notificaciones_debug.py
"""
Sistema de debugging para notificaciones.
Permite loguear y monitorear el sistema de notificaciones en tiempo real.
"""
import datetime
import json
from pathlib import Path

class NotificacionesDebugger:
    """
    Herramienta para debuggear y loguear el sistema de notificaciones.
    Los logs se guardan en: resources/data/notificaciones_debug.log
    """
    
    def __init__(self):
        self.log_file = Path("resources/data/notificaciones_debug.log")
        self.ensure_log_file()
    
    def ensure_log_file(self):
        """Crea el archivo de log si no existe"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            self.log_file.touch()
    
    def log(self, level: str, message: str, extra_data: dict = None):
        """
        Registra un evento en el log.
        
        Args:
            level: "INFO", "WARNING", "ERROR", "DEBUG"
            message: Mensaje a loguear
            extra_data: Datos adicionales en formato dict (se convierte a JSON)
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        log_entry = f"[{timestamp}] [{level}] {message}"
        if extra_data:
            log_entry += f" | {json.dumps(extra_data)}"
        
        log_entry += "\n"
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error escribiendo en log: {e}")
    
    def log_info(self, message: str, extra_data: dict = None):
        self.log("INFO", message, extra_data)
    
    def log_warning(self, message: str, extra_data: dict = None):
        self.log("WARNING", message, extra_data)
    
    def log_error(self, message: str, extra_data: dict = None):
        self.log("ERROR", message, extra_data)
    
    def log_debug(self, message: str, extra_data: dict = None):
        self.log("DEBUG", message, extra_data)
    
    def dump_config(self, datos_ref):
        """
        Vuelca el estado actual de las notificaciones al log.
        Útil para debuggear.
        """
        try:
            cfg = datos_ref.get_config()
            self.log_info("DUMP DE CONFIGURACIÓN DE NOTIFICACIONES", {
                "habilitadas": cfg.get("enabled"),
                "total_entradas": len(cfg.get("entries", [])),
                "entradas": cfg.get("entries", []),
                "ultima_enviada": cfg.get("last_sent", ""),
            })
        except Exception as e:
            self.log_error(f"Error dumpando config: {str(e)}")
    
    def clear_log(self):
        """Limpia el archivo de log"""
        try:
            self.log_file.write_text("")
            self.log_info("LOG LIMPIADO")
        except Exception as e:
            print(f"Error limpiando log: {e}")
    
    def get_recent_logs(self, lines: int = 20) -> list:
        """Devuelve las últimas N líneas del log"""
        try:
            with open(self.log_file, "r") as f:
                all_lines = f.readlines()
            return all_lines[-lines:]
        except:
            return []
    
    def print_logs(self):
        """Imprime los logs recientes en consola (útil para debugging)"""
        logs = self.get_recent_logs(50)
        print("\n=== NOTIFICACIONES DEBUG LOG ===")
        for log in logs:
            print(log.rstrip())
        print("================================\n")


# Instancia global para usar en toda la app
notif_debug = NotificacionesDebugger()
