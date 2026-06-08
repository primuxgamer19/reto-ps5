# dat_notificaciones.py
import datetime

class NotificacionesMixin:
    """
    Estructura:
    "notificaciones": {
        "enabled": True,
        "entries": [{"hora":"09:00","mensaje":"..."}],
        "last_sent": ""
    }
    """

    def init_notificaciones(self):
        self.notificaciones = {
            "enabled": False,
            "entries": [],
            "last_sent": ""
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

        normalized_entries = []
        for e in entries:
            if not isinstance(e, dict):
                continue
            hora = str(e.get("hora", "")).strip()
            mensaje = str(e.get("mensaje", "")).strip()
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
                normalized_entries.append({"hora": hora, "mensaje": mensaje})

        self.notificaciones = {
            "enabled": bool(enabled),
            "entries": normalized_entries,
            "last_sent": str(last_sent) if last_sent else ""
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
            if hora:
                entries.append({"hora": hora, "mensaje": mensaje})

        if getattr(self, "last_notif_date", ""):
            self.notificaciones["last_sent"] = self.last_notif_date
        else:
            self.notificaciones["last_sent"] = self.notificaciones.get("last_sent", "")

        return {
            "notificaciones": {
                "enabled": bool(getattr(self, "notificaciones", {}).get("enabled", False)),
                "entries": entries,
                "last_sent": str(getattr(self, "notificaciones", {}).get("last_sent", "")) or ""
            }
        }

    def set_notificaciones_enabled(self, enabled: bool):
        self.notificaciones["enabled"] = bool(enabled)

    def add_entry(self, hora: str, mensaje: str = ""):
        hora = (hora or "").strip()
        mensaje = (mensaje or "").strip()
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

        # Ahora permitimos múltiples entradas con la misma hora (no deduplicamos)
        self.notificaciones.setdefault("entries", []).append({"hora": hora, "mensaje": mensaje})
        return True

    def remove_entry(self, hora: str):
        hora = (hora or "").strip()
        before = len(self.notificaciones.get("entries", []))
        # Eliminamos todas las entradas que coincidan con la hora dada
        self.notificaciones["entries"] = [e for e in self.notificaciones.get("entries", []) if e.get("hora") != hora]
        return len(self.notificaciones.get("entries", [])) < before

    def clear_entries(self):
        self.notificaciones["entries"] = []

    def get_entries(self):
        return list(self.notificaciones.get("entries", []))

    def get_config(self):
        return {
            "enabled": bool(self.notificaciones.get("enabled", False)),
            "entries": list(self.notificaciones.get("entries", [])),
            "last_sent": str(self.notificaciones.get("last_sent", ""))
        }

    def set_last_sent_date(self, date_iso: str):
        self.notificaciones["last_sent"] = date_iso
        self.last_notif_date = date_iso

    def should_send_for_today(self) -> bool:
        if not self.notificaciones.get("enabled", False):
            return False
        hoy = datetime.date.today().strftime("%Y-%m-%d")
        return self.notificaciones.get("last_sent", "") != hoy