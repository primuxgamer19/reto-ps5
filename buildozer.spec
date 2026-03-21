[app]
title = Reto PS5
package.name = retops5
package.domain = org.carlos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 1.0

# Requerimientos puros.
requirements = python3,kivy==2.3.0,pillow

orientation = portrait
fullscreen = 1

# --- CONFIGURACIÓN DE ANDROID ---
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

# Aceptamos licencias desde adentro para no usar el "yes" en Linux
android.accept_sdk_license = True
android.allow_backup = True

# Archivos gráficos verificados
icon.filename = icon.png
presplash.filename = portada_img.png

# Permisos
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.wakelock = True

# Secciones técnicas
# ¡CORRECCIÓN!: Si se dejan con el "=" y vacías, rompen el AndroidManifest.xml. 
# Es mejor comentarlas si no se usan para que Buildozer haga el trabajo limpio.
# android.meta_data =
# android.library_references =
# android.services =

[buildozer]
log_level = 2
warn_on_root = 1

[bootstrap]
[web]
[p4a]
