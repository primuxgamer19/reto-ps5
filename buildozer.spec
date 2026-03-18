[app]
# (Sección General)
title = Reto PS5
package.name = retops5
package.domain = org.carlos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 1.0

# Requerimientos: Solo lo que usas. Kivy 2.3.0 es la más estable para Android 14.
requirements = python3,kivy==2.3.0,pillow

orientation = portrait
fullscreen = 1

# --- CONFIGURACIÓN DE ANDROID ---
android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.skip_update = False

# Icono y Portada (Verificados con tu lista)
icon.filename = icon.png
presplash.filename = portada_img.png

# Permisos
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.wakelock = True

# Secciones técnicas obligatorias para evitar errores de parseo
android.meta_data =
android.library_references =
android.services =
android.add_treble_support = True

[buildozer]
log_level = 2
warn_on_root = 1

# No borres estas secciones aunque estén vacías, buildozer las busca
[bootstrap]
[web]
[p4a]
