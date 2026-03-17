[app]
title = Reto PS5
package.name = retops5
package.domain = org.carlos
source.dir = .
# OJO: Aquí incluimos el JSON y los audios
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 1.0

# Requerimientos (Pillow es para las imágenes)
requirements = python3,kivy,pillow

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.allow_backup = True

# Icono y Portada (usando tus nombres de archivo)
icon.filename = icon.png
presplash.filename = portada_img.png

# Permisos básicos
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Para que no se duerma la pantalla mientras calculas
android.wakelock = True

[buildozer]
log_level = 2
warn_on_root = 1
