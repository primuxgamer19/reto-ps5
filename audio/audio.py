import os
from kivy.core.audio import SoundLoader

# --- MOTOR DE AUDIO OPTIMIZADO ---
class AudioManager:
    def __init__(self):
        self.bg_music = None
        self.music_13 = None
        self.is_playing_13 = False
        self.cache = {}

        # Resolver rutas de recursos basadas en la estructura del proyecto
        audio_pkg_dir = os.path.dirname(os.path.abspath(__file__))   # .../audio
        project_root = os.path.dirname(audio_pkg_dir)
        self.resources_audios = os.path.join(project_root, "resources", "audios")
        self.resources_music = os.path.join(project_root, "resources", "music")

    def _resolve_fx(self, file_name):
        # intenta en resources/audios, luego en cwd como fallback
        p = os.path.join(self.resources_audios, file_name)
        if os.path.exists(p):
            return p
        # también intentar con subcarpeta si el usuario pasó 'music/ps5.mp3' por error
        p2 = os.path.join(self.resources_music, file_name)
        if os.path.exists(p2):
            return p2
        return file_name

    def _resolve_music(self, file_name):
        p = os.path.join(self.resources_music, file_name)
        if os.path.exists(p):
            return p
        # fallback a audios por si el archivo está en audios
        p2 = os.path.join(self.resources_audios, file_name)
        if os.path.exists(p2):
            return p2
        return file_name

    def play_fx(self, file_name):
        path = self._resolve_fx(file_name)
        if path not in self.cache:
            self.cache[path] = SoundLoader.load(path)
        
        sound = self.cache[path]
        if sound:
            sound.stop()
            sound.play()

    def play_bg(self, file_name):
        path = self._resolve_music(file_name)
        if not self.bg_music:
            self.bg_music = SoundLoader.load(path)
        if self.bg_music and getattr(self.bg_music, "state", None) == 'stop':
            self.bg_music.loop = True
            self.bg_music.volume = 0.3
            try:
                self.bg_music.play()
            except Exception:
                # algunos backends pueden lanzar; no queremos romper la app
                pass

    def stop_bg(self):
        if self.bg_music: 
            try:
                self.bg_music.stop()
            except:
                pass

    def stop_13(self):
        self.is_playing_13 = False
        if self.music_13:
            try:
                self.music_13.stop()
            except:
                pass

    def load_13_music(self, file_name):
        path = self._resolve_music(file_name)
        if not self.music_13:
            self.music_13 = SoundLoader.load(path)
