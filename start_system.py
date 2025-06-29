#!/usr/bin/env python3
"""
Script de inicio del sistema de control por gestos
Maneja errores y proporciona información detallada del estado
"""

import sys
import time
import logging
import traceback
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    logger.info("🔍 Verificando dependencias...")
    
    required_packages = [
        'cv2',
        'mediapipe', 
        'flask',
        'numpy',
        'mysql.connector',
        'pyautogui',
        'pytz'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package}")
        except ImportError:
            logger.error(f"❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Paquetes faltantes: {', '.join(missing_packages)}")
        logger.info("💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    logger.info("✅ Todas las dependencias están instaladas")
    return True

def check_configuration():
    """Verificar configuración del sistema"""
    logger.info("🔍 Verificando configuración...")
    
    try:
        from config import GESTURE_ACTIONS, CAMERA_CONFIG, DB_CONFIG
        logger.info(f"✅ Configuración cargada - {len(GESTURE_ACTIONS)} gestos configurados")
        return True
    except Exception as e:
        logger.error(f"❌ Error en configuración: {e}")
        return False

def check_database():
    """Verificar conexión a la base de datos"""
    logger.info("🔍 Verificando base de datos...")
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        # Probar conexión
        stats = db.get_gesture_stats()
        logger.info("✅ Base de datos conectada")
        return True
    except Exception as e:
        logger.error(f"❌ Error en base de datos: {e}")
        logger.info("💡 Verifica:")
        logger.info("   - Que MySQL esté ejecutándose")
        logger.info("   - Las credenciales en .env")
        logger.info("   - Que la base de datos 'control_gestos' exista")
        return False

def check_camera():
    """Verificar acceso a la cámara"""
    logger.info("🔍 Verificando cámara...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            logger.error("❌ No se pudo abrir la cámara")
            logger.info("💡 Verifica:")
            logger.info("   - Que la cámara esté conectada")
            logger.info("   - Que no esté siendo usada por otra aplicación")
            logger.info("   - Los permisos de cámara en Windows")
            cap.release()
            return False
        
        # Leer un frame de prueba
        ret, frame = cap.read()
        if not ret or frame is None:
            logger.error("❌ No se pudo leer frame de la cámara")
            cap.release()
            return False
        
        logger.info(f"✅ Cámara funcionando - Resolución: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
        return True
        
    except Exception as e:
        logger.error(f"❌ Error con la cámara: {e}")
        return False

def start_flask_app():
    """Iniciar la aplicación Flask"""
    logger.info("🚀 Iniciando aplicación Flask...")
    
    try:
        from app import app
        
        logger.info("✅ Aplicación Flask iniciada")
        logger.info("🌐 Servidor disponible en: http://localhost:5000")
        logger.info("📊 Dashboard en: http://localhost:5000/dashboard")
        logger.info("⏹️  Presiona Ctrl+C para detener")
        
        # Iniciar el servidor
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Aplicación detenida por el usuario")
    except Exception as e:
        logger.error(f"❌ Error iniciando Flask: {e}")
        logger.error(traceback.format_exc())
        return False
    
    return True

def main():
    """Función principal"""
    logger.info("🎯 INICIANDO SISTEMA DE CONTROL POR GESTOS")
    logger.info("=" * 60)
    logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Verificaciones previas
    checks = [
        ("Dependencias", check_dependencies),
        ("Configuración", check_configuration),
        ("Base de Datos", check_database),
        ("Cámara", check_camera)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        logger.info(f"\n📋 {check_name}")
        logger.info("-" * 40)
        
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            logger.error(f"❌ Error en {check_name}: {e}")
            failed_checks.append(check_name)
    
    # Resumen de verificaciones
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESUMEN DE VERIFICACIONES")
    logger.info("=" * 60)
    
    if failed_checks:
        logger.error(f"❌ Verificaciones fallidas: {', '.join(failed_checks)}")
        logger.info("\n💡 Soluciones:")
        
        if "Dependencias" in failed_checks:
            logger.info("   • Ejecuta: pip install -r requirements.txt")
        
        if "Base de Datos" in failed_checks:
            logger.info("   • Verifica MySQL y configuración en .env")
        
        if "Cámara" in failed_checks:
            logger.info("   • Verifica conexión y permisos de cámara")
        
        logger.info("\n🔧 Ejecuta 'python test_system.py' para diagnóstico completo")
        return False
    
    logger.info("✅ Todas las verificaciones pasaron")
    
    # Preguntar si continuar
    try:
        response = input("\n¿Continuar con el inicio del sistema? (s/n): ").lower()
        if response != 's':
            logger.info("⏹️  Inicio cancelado por el usuario")
            return True
    except KeyboardInterrupt:
        logger.info("⏹️  Inicio cancelado por el usuario")
        return True
    
    # Iniciar aplicación
    logger.info("\n🚀 Iniciando sistema...")
    return start_flask_app()

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1) 