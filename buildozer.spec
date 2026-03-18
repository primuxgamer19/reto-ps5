[app]
title = Reto PS5
package.name = retops5
package.domain = org.carlos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 1.0

# CORRECCIÓN: Volvemos a los requerimientos originales limpios. Kivy ya reproduce audio solo.
requirements = python3,kivy==2.3.0,pillow

orientation = portrait
fullscreen = 1

# Configuraciones que SÍ arreglan la compatibilidad
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True

icon.filename = icon.png
presplash.filename = portada_img.png

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.wakelock = True

[buildozer]
log_level = 2
warn_on_root = 1
