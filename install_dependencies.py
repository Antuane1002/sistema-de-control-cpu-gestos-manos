#!/usr/bin/env python3
"""
Script de instalación de dependencias para el Sistema de Control por Gestos
Maneja la instalación de forma robusta y verifica cada dependencia
"""

import subprocess
import sys
import os
import importlib

def check_python_version():
    """Verificar versión de Python"""
    print("🔍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("💡 Se requiere Python 3.8 o superior")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def install_package(package_name, pip_name=None):
    """Instalar un paquete específico"""
    if pip_name is None:
        pip_name = package_name
    
    print(f"📦 Instalando {package_name}...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pip_name, "--upgrade"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ {package_name} instalado correctamente")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Error instalando {package_name}")
        return False

def check_package(package_name):
    """Verificar si un paquete está instalado"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_dependencies():
    """Instalar todas las dependencias"""
    print("🚀 INICIANDO INSTALACIÓN DE DEPENDENCIAS")
    print("=" * 50)
    
    # Verificar Python
    if not check_python_version():
        return False
    
    # Lista de dependencias con nombres específicos
    dependencies = [
        ("opencv-python", "cv2"),
        ("mediapipe", "mediapipe"),
        ("flask", "flask"),
        ("mysql-connector-python", "mysql.connector"),
        ("pyautogui", "pyautogui"),
        ("numpy", "numpy"),
        ("python-dotenv", "dotenv"),
        ("protobuf", "google.protobuf")
    ]
    
    failed_installations = []
    
    for pip_name, import_name in dependencies:
        print(f"\n📋 {import_name}")
        print("-" * 30)
        
        # Verificar si ya está instalado
        if check_package(import_name):
            print(f"✅ {import_name} ya está instalado")
            continue
        
        # Instalar si no está presente
        if not install_package(import_name, pip_name):
            failed_installations.append(import_name)
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE INSTALACIÓN")
    print("=" * 50)
    
    if failed_installations:
        print(f"❌ Fallos en instalación: {', '.join(failed_installations)}")
        print("\n💡 Soluciones:")
        print("1. Ejecuta como administrador")
        print("2. Actualiza pip: python -m pip install --upgrade pip")
        print("3. Instala manualmente: pip install <paquete>")
        return False
    else:
        print("✅ Todas las dependencias instaladas correctamente")
        return True

def verify_installation():
    """Verificar que todas las dependencias funcionan"""
    print("\n🔍 VERIFICANDO INSTALACIÓN")
    print("=" * 50)
    
    test_imports = [
        ("cv2", "OpenCV"),
        ("mediapipe", "MediaPipe"),
        ("flask", "Flask"),
        ("mysql.connector", "MySQL Connector"),
        ("pyautogui", "PyAutoGUI"),
        ("numpy", "NumPy"),
        ("dotenv", "Python-dotenv")
    ]
    
    failed_imports = []
    
    for import_name, display_name in test_imports:
        try:
            module = importlib.import_module(import_name)
            print(f"✅ {display_name} - OK")
        except ImportError as e:
            print(f"❌ {display_name} - Error: {e}")
            failed_imports.append(display_name)
    
    if failed_imports:
        print(f"\n❌ Errores de importación: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ Todas las dependencias verificadas correctamente")
        return True

def main():
    """Función principal"""
    print("🎯 INSTALADOR DE DEPENDENCIAS - SISTEMA DE CONTROL POR GESTOS")
    print("=" * 60)
    
    # Instalar dependencias
    if not install_dependencies():
        print("\n❌ Instalación fallida")
        return False
    
    # Verificar instalación
    if not verify_installation():
        print("\n❌ Verificación fallida")
        return False
    
    print("\n🎉 ¡INSTALACIÓN COMPLETADA!")
    print("=" * 60)
    print("✅ Todas las dependencias están listas")
    print("🚀 Puedes ejecutar el sistema con: python start_system.py")
    print("🔧 Para pruebas: python test_system.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        sys.exit(1) 