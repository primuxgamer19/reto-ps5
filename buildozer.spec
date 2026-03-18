[app]
# (Información General)
title = Reto PS5
package.name = retops5
package.domain = org.carlos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 1.0

# Requerimientos limpios (Kivy 2.3.0 es la versión estable para este entorno)
requirements = python3,kivy==2.3.0,pillow

orientation = portrait
fullscreen = 1

# --- CONFIGURACIÓN DE ANDROID 2026 ---
android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.skip_update = False

# Recursos Multimedia
icon.filename = icon.png
presplash.filename = portada_img.png

# Permisos necesarios
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, FOREGROUND_SERVICE
android.wakelock = True

# Secciones técnicas (obligatorias para Buildozer 1.5+)
android.meta_data =
android.library_references =
android.services =
android.add_treble_support = True

[buildozer]
log_level = 2
warn_on_root = 1

[bootstrap]
[web]
[p4a]
