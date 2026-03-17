[app]
# (Sección General)
title = Reto PS5
package.name = retops5
package.domain = org.carlos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 1.0

# Requerimientos para 2026: Kivy estable y soporte de audio completo
requirements = python3,kivy,pillow,sdl2_mixer,ffpyplayer

orientation = portrait
fullscreen = 1

# --- CONFIGURACIÓN DE ANDROID 2026 ---
# Dejamos que buildozer elija el NDK pero forzamos API 34 para compatibilidad
android.api = 34
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a
android.allow_backup = True

# Archivos multimedia (Verificados)
icon.filename = icon.png
presplash.filename = portada_img.png

# Permisos requeridos para Android moderno
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, FOREGROUND_SERVICE
android.wakelock = True

# Configuración avanzada para evitar cierres
android.meta_data =
android.library_references =
android.services =

[buildozer]
log_level = 2
warn_on_root = 1

