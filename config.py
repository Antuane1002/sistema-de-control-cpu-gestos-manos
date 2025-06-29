import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'control_gestos'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Configuración de la cámara
CAMERA_CONFIG = {
    'width': 640,
    'height': 480,
    'fps': 30
}

# Configuración de detección de gestos
GESTURE_CONFIG = {
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.4,
    'gesture_hold_time': 0.5
}

# Mapeo de gestos a acciones
GESTURE_ACTIONS = {
    'mano_abierta': {
        'action': 'abrir_navegador',
        'description': 'Abrir navegador Chrome',
        'command': 'chrome'
    },
    'puño_cerrado': {
        'action': 'cerrar_ventana',
        'description': 'Cerrar ventana activa',
        'command': 'alt+f4'
    },
    'pulgar_arriba': {
        'action': 'subir_volumen',
        'description': 'Subir volumen del sistema',
        'command': 'volume_up'
    },
    'dos_dedos': {
        'action': 'captura_pantalla',
        'description': 'Tomar captura de pantalla',
        'command': 'screenshot'
    },
    'rock_roll': {
        'action': 'refrescar',
        'description': 'Refrescar página (F5)',
        'command': 'f5'
    }
} 