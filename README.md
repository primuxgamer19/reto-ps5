
# 💰 Reto PS5 - App de Finanzas Personales

> Una aplicación móvil para gestionar tus finanzas personales de forma divertida y desafiante, con un toque de humor y sarcasmo.

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-green.svg)
![Kivy](https://img.shields.io/badge/kivy-2.3.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## 🎯 ¿Qué es Reto PS5?

**Reto PS5** es una aplicación gamificada para el control de finanzas personales. No es una app bancaria formal, sino un **asistente sarcástico y motivador** que te ayuda a:

- 💳 Registrar y controlar tu ahorro
- 🚫 Confesar tus "pecados" financieros (gastos innecesarios)
- 🎁 Rastrear regalos e inversiones
- 📊 Visualizar tu progreso con gráficas interactivas
- 💸 Gestionar gastos fijos y presupuestos
- 🔔 Recibir notificaciones motivacionales (¡a veces sarcásticas!)

---

## ✨ Características Principales

### 📱 Pantallas Disponibles

1. **Calculadora/Reporte** - Tu ahorro actual y cálculo de presupuesto
2. **El Confesionario** - Registra tus gastos impulsivos con humor
3. **Presupuesto** - Gestiona metas y límites de gasto
4. **Gastos Fijos** - Control de gastos mensuales obligatorios
5. **Regalos e Inversiones** - Compras positivas y reinversiones
6. **Historial** - Revisa todas tus transacciones
7. **Gráficas Financieras** - Visualización interactiva de tu progreso
8. **Notificaciones** - Alertas motivacionales (con efectos de sonido)

### 🎮 Funcionalidades Especiales

- ✅ **Validación inteligente**: Detecta inconsistencias contables
- 🔊 **Efectos de sonido**: Feedback auditivo para cada acción
- 📈 **Gráficas interactivas**: Zoom, pan y estadísticas en tiempo real
- 🎭 **Mensajes sarcásticos**: La app tiene personalidad
- 🔐 **Almacenamiento local**: Tus datos permanecen en tu teléfono

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.11+
- Pip (gestor de paquetes de Python)
- Para compilar a Android: Buildozer, Java 17+

### Opción 1: Ejecutar desde fuente (Desarrollo)

```bash
# Clonar el repositorio
git clone https://github.com/primuxgamer19/reto-ps5.git
cd reto-ps5

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
python main.py
```

### Opción 2: Compilar a APK (Android)

```bash
# Instalar Buildozer
pip install buildozer cython

# Compilar
buildozer android debug

# El APK estará en: bin/retops5-2.0-debug.apk
```

### Opción 3: Usar GitHub Actions (Compilación Automática)

Cuando hagas push a `main`, GitHub Actions compilará automáticamente el APK y lo publicará en Releases.

---

## 📁 Estructura del Proyecto

```
reto-ps5/
├── main.py                      # Entrada principal de la app
├── buildozer.spec              # Configuración para compilar a Android
├── requirements.txt            # Dependencias de Python
│
├── ui/                         # Interfaz de usuario (Kivy)
│   ├── ui_calculadora.py      # Pantalla principal de reporte
│   ├── ui_pecado.py           # El confesionario
│   ├── ui_presupuesto.py      # Gestión de presupuesto
│   ├── ui_gastos_fijos.py     # Gastos mensuales
│   ├── ui_regalo.py           # Regalos e inversiones
│   ├── ui_historial.py        # Historial de transacciones
│   ├── ui_estadistica.py      # Gráficas y análisis
│   ├── ui_notificaciones.py   # Centro de notificaciones
│   ├── ui_widgets.py          # Componentes reutilizables
│   ├── ui_grafica_core.py     # Motor de gráficas interactivas
│   ├── ui_grafica_render.py   # Renderizado de gráficas
│   ├── touch_controls.py      # Control táctil para gráficas
│   └── ui_config.py           # Configuración centralizada de UI
│
├── logic/                       # Lógica de negocio
│   ├── motor_datos.py          # Gestor de datos y persistencia
│   ├── motor_matematico.py     # Cálculos financieros
│   ├── feedback_logic.py       # Sistema de retroalimentación sarcástica
│   ├── filtro_nombres.py       # Validación de nombres/gastos
│   └── filtros_ui/            # Filtros especializados
│       ├── regalo_filter.py
│       ├── pecado_filter.py
│       └── gasto_fijo_filter.py
│
├── mat/                         # Módulos matemáticos
│   ├── mat_geometria.py        # Cálculos geométricos para gráficas
│   └── mat_historia.py         # Historial temporal de datos
│
├── debug/                       # Utilidades de depuración
│   └── debug_overlay.py        # Overlay de debugging en desarrollo
│
├── resources/                   # Recursos multimedia
│   ├── images.py              # Gestor de imágenes
│   ├── images/                # Carpeta de imágenes
│   │   ├── grafica_icon.png
│   │   └── icons/
│   ├── audio/                 # Efectos de sonido y música
│   │   ├── alerta.wav
│   │   ├── acierto.mp3
│   │   ├── pum.mp3
│   │   └── letania13.mp3
│   └── data/                  # Datos persistentes
│       └── datos.json         # Base de datos local
│
├── .github/
│   └── workflows/
│       └── android.yml        # Workflow de compilación automática
│
├── icon.png                    # Icono de la app
├── portada_img.png            # Splash screen
└── README.md                   # Este archivo
```

---

## 🛠️ Configuración y Uso

### Variables de Entorno

```bash
# Opcional: Habilitar modo debug
export DEBUG_MODE=1
python main.py
```

### Archivos de Configuración

- **`buildozer.spec`**: Configuración de compilación para Android
- **`ui/ui_config.py`**: Parámetros de UI (colores, tamaños, etc.)
- **`requirements.txt`**: Dependencias del proyecto

---

## 📊 Guía de Uso

### 1. **Registrar tu Ahorro**
   - Abre la **Calculadora**
   - Ingresa tu cantidad ahorrada actual
   - Toca **CALCULAR REPORTE**

### 2. **Confesar un Gasto Impulsivo**
   - Ve a **El Confesionario**
   - Añade filas con nombre y monto del gasto
   - Toca **CONFESAR TODO**
   - La app te dirá cuál sería tu castigo 😂

### 3. **Gestionar Presupuesto**
   - En **Presupuesto**, establece tu salario e ingresos
   - Define tu meta de ahorro
   - La app calculará cuánto puedes gastar

### 4. **Ver tu Progreso**
   - Toca la **GRÁFICA** en cualquier pantalla
   - Explora con tu dedo (zoom, pan)
   - Visualiza proyecciones futuras

---

## 🔧 Desarrollo

### Instalar Dependencias de Desarrollo

```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

### Formato de Código

```bash
black .
```

### Linting

```bash
flake8 .
```

### Ejecutar Tests (cuando los haya)

```bash
pytest
```

---

## 🐛 Solución de Problemas

### La app no inicia
```bash
# Limpia la caché de Kivy
rm -rf ~/.kivy/

# Reinstala las dependencias
pip install --force-reinstall -r requirements.txt
```

### El APK no compila
```bash
# Asegúrate de tener Buildozer actualizado
pip install --upgrade buildozer

# Intenta con verbose
buildozer -v android debug
```

### La gráfica no se muestra
- Verifica que `grafica_icon.png` exista en `resources/images/`
- Revisa la consola para mensajes de error
- Intenta reiniciar la app

---

## 🎨 Personalización

### Cambiar Colores de la App
Edita `ui/ui_config.py`:
```python
BUTTON_COLOR = (0.2, 0.6, 1, 1)  # RGB con alpha (0-1)
TEXT_COLOR = (1, 1, 1, 1)        # Blanco
```

### Cambiar Textos Sarcásticos
Edita `logic/feedback_logic.py` en la función `obtener_feedback_msg()`

### Agregar Nuevos Efectos de Sonido
1. Coloca el archivo en `resources/audio/`
2. Referencialo en el código:
   ```python
   self.audio.play_fx('tu_sonido.mp3')
   ```

---

## 📝 Notas de Desarrollo

### Hechas por IA (con supervisión humana)
Todas las funcionalidades fueron creadas con ayuda de IAs, pero bajo la dirección y ideas de:
- **Dueño del proyecto**: primuxgamer19 (las ideas)
- **Asistentes IA**: Generación de código

### Próximas Mejoras Planeadas
- [ ] Sincronización en la nube
- [ ] Exportar reportes a PDF
- [ ] Análisis predictivo avanzado
- [ ] Soporte multi-usuario
- [ ] Tests automatizados
- [ ] Documentación de API interna

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Ver `LICENSE` para más detalles.

---

## 🤝 Contribuciones

¿Quieres mejorar Reto PS5? ¡Las contribuciones son bienvenidas!

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/MiFeature`)
3. Commit tus cambios (`git commit -m 'Agrego MiFeature'`)
4. Push a la rama (`git push origin feature/MiFeature`)
5. Abre un Pull Request

---

## 📞 Contacto y Soporte

- **GitHub**: [@primuxgamer19](https://github.com/primuxgamer19)
- **Problemas**: [Abre un Issue](https://github.com/primuxgamer19/reto-ps5/issues)

---

## 🎉 Créditos

- **Framework**: [Kivy](https://kivy.org/)
- **Build Tool**: [Buildozer](https://buildozer.readthedocs.io/)
- **Python**: [Python Software Foundation](https://www.python.org/)
- **Idea & Desarrollo**: primuxgamer19 + IA

---

**¡Gracias por usar Reto PS5! 🚀**

*Recuerda: ¡El ahorro es un juego! Mantén tu dinero seguro y tus gastos bajo control. 💪*
