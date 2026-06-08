## Importar / Exportar JSON

La aplicación soporta dos modos de importación/exportación de respaldos JSON:

1) Modo compilado (APK / Android):
   - La app intenta usar la funcionalidad nativa de compartir (plyer.share) para abrir el menú de compartir
     del sistema (Drive, WhatsApp, Telegram, etc.). Esto evita problemas con permisos y scoped storage.
   - Requiere que el dispositivo permita que la app acceda al archivo de datos, y en algunos Android modernos
     puede requerir Storage Access Framework o permisos adicionales.

2) Modo en código fuente (Pydroid 3 / PC):
   - Se usa la carpeta local "JSON exportados" dentro del directorio base del proyecto y los diálogos
     de export/import incluidos en la UI. Este modo es el recomendado cuando ejecutas la app desde el
     código fuente o desde Pydroid, ya que las APIs nativas pueden no estar disponibles.

Notas importantes:
- La detección de si la app está compilada se realiza comprobando variables de entorno como
  `ANDROID_ARGUMENT` o `ANDROID_PRIVATE`. Si la app está compilada, prioriza el flujo nativo.
- Si exportas un archivo cuyo nombre ya existe, la app añadirá un sufijo con timestamp para evitar
  sobrescribir sin querer.
- En caso de importación la app valida que el JSON tenga las claves mínimas esperadas: `presupuesto`,
  `ingresos`, `gastos` y `notificaciones`. Si faltan claves, verás un mensaje indicando cuáles faltan.

## Debug (solo en carpeta debug/)

Todas las utilidades y logs de depuración se colocan dentro de la carpeta `debug/` para no mezclar
archivos de debugging con la lógica principal de la aplicación. Para ejecutar la app en modo debug,
usa `debug/main_debug.py`.

- Logs de notificaciones de debug: `debug/resources/data/notificaciones_debug.log`

## DEBUG_MODE

Puedes habilitar un modo de depuración exportando la variable de entorno `DEBUG_MODE=1` antes de
iniciar la app (útil al ejecutar desde el código fuente). En este modo se mostrarán mensajes más
verbosos y ciertos errores escribirán trazas en los logs dentro de `debug/`.
