[app]
title = Reto PS5
package.name = retops5
package.domain = org.carlos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 1.0

# Requerimientos exactos. Kivy reproduce audios por defecto en Android, no necesitamos basura extra.
requirements = python3,kivy==2.3.0,pillow

orientation = portrait
fullscreen = 1

# --- CONFIGURACIÓN DE ANDROID ---
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

# Evita que el proceso se quede congelado pidiendo permisos en la consola
android.accept_sdk_license = True
android.allow_backup = True

# Archivos gráficos
icon.filename = icon.png
presplash.filename = portada_img.png

# Permisos
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.wakelock = True

# Secciones técnicas (Déjalas aunque estén vacías, Buildozer las busca)
android.meta_data =
android.library_references =
android.services =

[buildozer]
log_level = 2
warn_on_root = 1

[bootstrap]
[web]
[p4a]
