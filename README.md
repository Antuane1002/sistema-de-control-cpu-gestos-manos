# 🖐️ Sistema de Control de CPU con Gestos de Manos

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-orange.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-purple.svg)](https://mediapipe.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema inteligente de control de computadora mediante detección de gestos usando **OpenCV**, **MediaPipe** y **Flask**. Controla tu PC con gestos de mano en tiempo real.

## ✨ Características

- 🎯 **Detección de 5 gestos** en tiempo real
- 🌐 **Dashboard web** con interfaz moderna
- 📊 **Estadísticas y logs** detallados
- 🗄️ **Base de datos MySQL** para registro
- 🔧 **Configuración flexible** y personalizable
- 🛡️ **Manejo robusto de errores** y recuperación automática
- 📱 **Responsive design** para diferentes dispositivos

## 🎮 Gestos Soportados

| Gesto | Acción | Descripción |
|-------|--------|-------------|
| ✋ **Mano abierta** | `abrir_navegador` | Abre el navegador Chrome |
| ✊ **Puño cerrado** | `cerrar_ventana` | Cierra la ventana activa |
| 👍 **Pulgar arriba** | `subir_volumen` | Aumenta el volumen del sistema |
| ✌ **Dos dedos** | `captura_pantalla` | Toma una captura de pantalla |
| 🤘 **Rock & roll** | `refrescar` | Refresca la página actual |

## 🚀 Instalación Rápida

### Prerrequisitos

- Python 3.8 o superior
- MySQL/MariaDB
- Cámara web
- Windows 10/11

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sistema-control-cpu-gestos-manos.git
cd sistema-control-cpu-gestos-manos
```

### 2. Instalar dependencias

```bash
# Opción A: Instalador automático
python install_dependencies.py

# Opción B: Instalación manual
pip install -r requirements.txt
```

### 3. Configurar base de datos

```bash
# Crear base de datos
mysql -u root -p < setup_database.sql

# Configurar variables de entorno
copy env_example.txt .env
# Editar .env con tus credenciales
```

### 4. Ejecutar el sistema

```bash
# Inicio con verificación automática
python start_system.py

# O inicio directo
python app.py
```

### 5. Abrir en el navegador

```
http://localhost:5000
```

## 📖 Uso

1. **Iniciar cámara**: Haz clic en "Iniciar Cámara" en el dashboard
2. **Realizar gestos**: Mantén tu mano a 30-50cm de la cámara
3. **Ver acciones**: Observa las acciones ejecutadas en tiempo real
4. **Monitorear**: Revisa estadísticas en el dashboard

### Consejos para mejor detección

- ✅ **Buena iluminación** - Evita sombras
- ✅ **Fondo liso** - Evita fondos complejos
- ✅ **Distancia óptima** - 30-50cm de la cámara
- ✅ **Gestos claros** - Mantén los gestos estables

## 🛠️ Configuración

### Personalizar gestos

Edita `config.py` para agregar nuevos gestos:

```python
GESTURE_ACTIONS = {
    'nuevo_gesto': {
        'action': 'mi_accion',
        'description': 'Descripción de la acción',
        'command': 'comando_a_ejecutar',
        'min_confidence': 0.7
    }
}
```

### Ajustar sensibilidad

```python
GESTURE_CONFIG = {
    'min_detection_confidence': 0.7,  # Más alto = más preciso
    'min_tracking_confidence': 0.4,   # Más alto = más estable
    'gesture_hold_time': 0.5          # Tiempo de estabilidad
}
```

## 📁 Estructura del Proyecto

```
sistema-control-cpu-gestos-manos/
├── app.py                 # Aplicación Flask principal
├── gesture_detector.py    # Detector de gestos con MediaPipe
├── system_controller.py   # Controlador de acciones del sistema
├── database.py           # Gestión de base de datos
├── config.py             # Configuración del sistema
├── start_system.py       # Script de inicio mejorado
├── test_system.py        # Pruebas del sistema
├── test_cameras.py       # Pruebas de cámaras
├── install_dependencies.py # Instalador de dependencias
├── templates/            # Plantillas HTML
│   ├── index.html       # Dashboard principal
│   └── dashboard.html   # Página de estadísticas
├── screenshots/          # Capturas de pantalla
├── requirements.txt      # Dependencias
├── setup_database.sql   # Script de configuración de BD
├── env_example.txt      # Variables de entorno de ejemplo
└── README.md            # Este archivo
```

## 🔧 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Página principal |
| `GET` | `/dashboard` | Dashboard de estadísticas |
| `GET` | `/video_feed` | Stream de video |
| `POST` | `/api/start_camera` | Iniciar cámara |
| `POST` | `/api/stop_camera` | Detener cámara |
| `GET` | `/api/camera_status` | Estado de la cámara |
| `GET` | `/api/actions` | Historial de acciones |
| `GET` | `/api/stats` | Estadísticas |
| `POST` | `/set_camera` | Cambiar cámara |

## 🧪 Pruebas

```bash
# Pruebas del sistema completo
python test_system.py

# Pruebas de cámaras
python test_cameras.py

# Pruebas de gestos
python test_gestures.py
```

## 🐛 Solución de Problemas

### Cámara no funciona
```bash
# Verificar permisos en Windows
# Configuración > Privacidad > Cámara > Permitir acceso
```

### Base de datos no conecta
```bash
# Verificar MySQL ejecutándose
# Revisar credenciales en .env
```

### Dependencias faltantes
```bash
# Ejecutar como administrador
pip install -r requirements.txt
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [MediaPipe](https://mediapipe.dev/) por el framework de detección de manos
- [OpenCV](https://opencv.org/) por el procesamiento de video
- [Flask](https://flask.palletsprojects.com/) por el framework web
- [Bootstrap](https://getbootstrap.com/) por el diseño de la interfaz

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Ejecuta `python test_system.py` para diagnosticar
3. Abre un issue en el repositorio

---

**¡Disfruta controlando tu computadora con gestos!** 🎉

⭐ **Si te gusta este proyecto, dale una estrella en GitHub** 

## 👩‍💻 Autora

**Antuane del Rosario Huamani Bernabel** 