# data/dat_notificaciones.py
"""
Sistema mejorado de notificaciones con dos tipos:
1. POPUP: Solo aparece mientras la app está abierta (para Pydroid)
2. ANDROID: Notificaciones nativas de Android (compiladas)
"""
import datetime

class NotificacionesMixin:
    """
    Estructura:
    "notificaciones": {
        "enabled": True,
        "entries": [
            {
                "hora":"09:00",
                "mensaje":"...",
                "tipo":"popup"  # "popup" o "android"
            }
        ],
        "last_sent": "",
        "last_sent_timestamp": 0
    }
    """

    def init_notificaciones(self):
        self.notificaciones = {
            "enabled": False,
            "entries": [],
            "last_sent": "",
            "last_sent_timestamp": 0
        }
        self.last_notif_date = self.notificaciones.get("last_sent", "")
        self.is_first_run = True

    def cargar_notificaciones(self, data: dict):
        cfg = data.get("notificaciones", None)
        if not cfg:
            if data.get("last_notif_date"):
                self.notificaciones["last_sent"] = data.get("last_notif_date", "")
                self.last_notif_date = self.notificaciones["last_sent"]
            return

        enabled = cfg.get("enabled", False)
        entries = cfg.get("entries", [])
        last_sent = cfg.get("last_sent", "")
        last_sent_ts = cfg.get("last_sent_timestamp", 0)

        normalized_entries = []
        for e in entries:
            if not isinstance(e, dict):
                continue
            
            hora = str(e.get("hora", "")).strip()
            mensaje = str(e.get("mensaje", "")).strip()
            tipo = str(e.get("tipo", "popup")).strip()  # popup o android
            
            # Validar tipo
            if tipo not in ("popup", "android"):
                tipo = "popup"
            
            if hora:
                parts = hora.split(":")
                if len(parts) == 2:
                    try:
                        hh = int(parts[0]); mm = int(parts[1])
                        if 0 <= hh <= 23 and 0 <= mm <= 59:
                            hora = f"{hh:02d}:{mm:02d}"
                        else:
                            hora = ""
                    except:
                        hora = ""
                else:
                    hora = ""
            
            if hora:
                normalized_entries.append({
                    "hora": hora,
                    "mensaje": mensaje,
                    "tipo": tipo
                })

        self.notificaciones = {
            "enabled": bool(enabled),
            "entries": normalized_entries,
            "last_sent": str(last_sent) if last_sent else "",
            "last_sent_timestamp": int(last_sent_ts) if last_sent_ts else 0
        }

        self.last_notif_date = self.notificaciones.get("last_sent", "")
        if data.get("last_notif_date"):
            self.last_notif_date = data.get("last_notif_date", "")
            self.notificaciones["last_sent"] = self.last_notif_date

    def guardar_notificaciones(self) -> dict:
        entries = []
        for e in getattr(self, "notificaciones", {}).get("entries", []):
            hora = e.get("hora", "").strip()
            mensaje = e.get("mensaje", "").strip()
            tipo = e.get("tipo", "popup").strip()
            if hora:
                entries.append({
                    "hora": hora,
                    "mensaje": mensaje,
                    "tipo": tipo
                })

        if getattr(self, "last_notif_date", ""):
            self.notificaciones["last_sent"] = self.last_notif_date
        else:
            self.notificaciones["last_sent"] = self.notificaciones.get("last_sent", "")

        return {
            "notificaciones": {
                "enabled": bool(getattr(self, "notificaciones", {}).get("enabled", False)),
                "entries": entries,
                "last_sent": str(getattr(self, "notificaciones", {}).get("last_sent", "")) or "",
                "last_sent_timestamp": int(getattr(self, "notificaciones", {}).get("last_sent_timestamp", 0)) or 0
            }
        }

    def set_notificaciones_enabled(self, enabled: bool):
        self.notificaciones["enabled"] = bool(enabled)

    def add_entry(self, hora: str, mensaje: str = "", tipo: str = "popup"):
        """
        Añade una entrada de notificación.
        
        Args:
            hora: Formato HH:MM
            mensaje: Texto del recordatorio
            tipo: "popup" (solo en app abierta) o "android" (notificación nativa)
        
        Returns:
            bool: True si se añadió correctamente
        """
        hora = (hora or "").strip()
        mensaje = (mensaje or "").strip()
        tipo = (tipo or "popup").strip()
        
        # Validar tipo
        if tipo not in ("popup", "android"):
            tipo = "popup"
        
        parts = hora.split(":")
        if len(parts) != 2:
            return False
        
        try:
            hh = int(parts[0]); mm = int(parts[1])
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                return False
            hora = f"{hh:02d}:{mm:02d}"
        except:
            return False

        self.notificaciones.setdefault("entries", []).append({
            "hora": hora,
            "mensaje": mensaje,
            "tipo": tipo
        })
        return True

    def remove_entry(self, hora: str):
        """Elimina todas las entradas que coincidan con la hora dada"""
        hora = (hora or "").strip()
        before = len(self.notificaciones.get("entries", []))
        self.notificaciones["entries"] = [
            e for e in self.notificaciones.get("entries", [])
            if e.get("hora") != hora
        ]
        return len(self.notificaciones.get("entries", [])) < before

    def clear_entries(self):
        """Limpia todas las entradas"""
        self.notificaciones["entries"] = []

    def get_entries(self):
        """Devuelve todas las entradas"""
        return list(self.notificaciones.get("entries", []))

    def get_entries_by_type(self, tipo: str) -> list:
        """
        Devuelve entradas filtradas por tipo.
        
        Args:
            tipo: "popup" o "android"
        
        Returns:
            list: Entradas del tipo especificado
        """
        return [
            e for e in self.notificaciones.get("entries", [])
            if e.get("tipo") == tipo
        ]

    def get_config(self):
        return {
            "enabled": bool(self.notificaciones.get("enabled", False)),
            "entries": list(self.notificaciones.get("entries", [])),
            "last_sent": str(self.notificaciones.get("last_sent", "")),
            "last_sent_timestamp": int(self.notificaciones.get("last_sent_timestamp", 0))
        }

    def set_last_sent_date(self, date_iso: str):
        """
        Actualiza la última fecha de envío.
        
        Args:
            date_iso: Formato YYYY-MM-DD
        """
        self.notificaciones["last_sent"] = date_iso
        self.notificaciones["last_sent_timestamp"] = int(datetime.datetime.now().timestamp())
        self.last_notif_date = date_iso

    def should_send_for_today(self) -> bool:
        """
        Verifica si se debe enviar notificación hoy.
        
        Returns:
            bool: True si las notificaciones están habilitadas y no se han enviado hoy
        """
        if not self.notificaciones.get("enabled", False):
            return False
        
        hoy = datetime.date.today().strftime("%Y-%m-%d")
        last_sent = self.notificaciones.get("last_sent", "")
        
        return last_sent != hoy

    def get_next_notification_entry(self, ahora_dt: datetime.datetime = None):
        """
        Obtiene la próxima entrada de notificación que debería enviarse.
        
        Args:
            ahora_dt: datetime actual (si es None, usa datetime.now())
        
        Returns:
            tuple: (entry_dict, delta_segundos) o (None, None) si no hay próxima
        """
        if ahora_dt is None:
            ahora_dt = datetime.datetime.now()
        
        proxima = None
        min_delta = 61  # Más de 60 segundos
        
        for e in self.notificaciones.get("entries", []):
            hora = e.get("hora")
            if not hora:
                continue
            
            try:
                hh, mm = map(int, hora.split(":"))
                target_dt = ahora_dt.replace(hour=hh, minute=mm, second=0, microsecond=0)
                delta = abs((ahora_dt - target_dt).total_seconds())
                
                if delta <= 60 and delta < min_delta:
                    min_delta = delta
                    proxima = e
            except:
                continue
        
        if proxima:
            return (proxima, min_delta)
        return (None, None)
