[app]
title = Reto PS5
package.name = retops5
package.domain = org.carlos
source.dir = .
# Incluir todas las extensiones necesarias y las nuevas carpetas
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
# Incluir explícitamente todas las carpetas del proyecto
source.include_patterns = ui/*,logic/*,mat/*,debug/*,resources/*,.github/*

version = 2.0

# Requerimientos puros
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
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/portada_img.png

# Permisos necesarios
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.wakelock = True

# Configuración de metadatos
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

[buildozer]
log_level = 2
warn_on_root = 1

[bootstrap]
[web]
[p4a]
