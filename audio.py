from kivy.core.audio import SoundLoader

# --- MOTOR DE AUDIO OPTIMIZADO ---
class AudioManager:
    def __init__(self):
        self.bg_music = None
        self.music_13 = None
        self.is_playing_13 = False
        self.cache = {}

    def play_fx(self, file_name):
        if file_name not in self.cache:
            self.cache[file_name] = SoundLoader.load(file_name)
        
        sound = self.cache[file_name]
        if sound:
            sound.stop()
            sound.play()

    def play_bg(self, file_name):
        if not self.bg_music:
            self.bg_music = SoundLoader.load(file_name)
        if self.bg_music and self.bg_music.state == 'stop':
            self.bg_music.loop = True
            self.bg_music.volume = 0.3
            self.bg_music.play()

    def stop_bg(self):
        if self.bg_music: self.bg_music.stop()

    def stop_13(self):
        self.is_playing_13 = False
        if self.music_13: self.music_13.stop()

    def load_13_music(self, file_name):
        if not self.music_13:
            self.music_13 = SoundLoader.load(file_name)
