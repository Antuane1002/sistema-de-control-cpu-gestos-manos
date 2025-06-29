import subprocess
import pyautogui
import os
import time
import logging
from config import GESTURE_ACTIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemController:
    def __init__(self):
        # Configurar pyautogui para mayor seguridad
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Mapeo de comandos a funciones
        self.action_handlers = {
            'chrome': self._open_chrome,
            'alt+f4': self._close_active_window,
            'volume_up': self._increase_volume,
            'screenshot': self._take_screenshot,
            'f5': self._refresh_page
        }
    
    def execute_action(self, gesture):
        """Ejecutar la acción correspondiente al gesto"""
        if gesture not in GESTURE_ACTIONS:
            logger.warning(f"Gesto no reconocido: {gesture}")
            return False
        
        action_info = GESTURE_ACTIONS[gesture]
        command = action_info['command']
        description = action_info['description']
        
        try:
            logger.info(f"Ejecutando acción: {description}")
            
            if command in self.action_handlers:
                self.action_handlers[command]()
            else:
                logger.error(f"Comando no implementado: {command}")
                return False
            
            logger.info(f"Acción ejecutada exitosamente: {description}")
            return True
            
        except Exception as e:
            logger.error(f"Error al ejecutar acción {description}: {e}")
            return False
    
    def _open_chrome(self):
        """Abrir navegador Chrome"""
        try:
            # Intentar diferentes rutas de Chrome
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "chrome.exe"  # Si está en PATH
            ]
            
            for path in chrome_paths:
                try:
                    subprocess.Popen([path], shell=True)
                    logger.info("Chrome abierto exitosamente")
                    return
                except FileNotFoundError:
                    continue
            
            # Si no se encuentra Chrome, intentar con el comando genérico
            subprocess.Popen(["start", "chrome"], shell=True)
            
        except Exception as e:
            logger.error(f"Error al abrir Chrome: {e}")
            raise
    
    def _close_active_window(self):
        """Cerrar la ventana activa"""
        try:
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.5)  # Pequeña pausa para que se procese
        except Exception as e:
            logger.error(f"Error al cerrar ventana: {e}")
            raise
    
    def _increase_volume(self):
        """Aumentar el volumen del sistema"""
        try:
            pyautogui.press('volumeup')
            time.sleep(0.1)
            pyautogui.press('volumeup')  # Aumentar dos veces para efecto más notable
        except Exception as e:
            logger.error(f"Error al aumentar volumen: {e}")
            raise
    
    def _take_screenshot(self):
        """Tomar captura de pantalla"""
        try:
            # Crear directorio de capturas si no existe
            screenshots_dir = "screenshots"
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)
            
            # Generar nombre único para la captura
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{screenshots_dir}/captura_{timestamp}.png"
            
            # Tomar captura
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            logger.info(f"Captura de pantalla guardada: {filename}")
            
        except Exception as e:
            logger.error(f"Error al tomar captura de pantalla: {e}")
            raise
    
    def _refresh_page(self):
        """Refrescar la página actual (F5)"""
        try:
            pyautogui.press('f5')
            time.sleep(0.5)  # Pequeña pausa para que se procese
        except Exception as e:
            logger.error(f"Error al refrescar página: {e}")
            raise
    
    def get_available_actions(self):
        """Obtener lista de acciones disponibles"""
        return list(GESTURE_ACTIONS.keys())
    
    def get_action_description(self, gesture):
        """Obtener descripción de una acción"""
        if gesture in GESTURE_ACTIONS:
            return GESTURE_ACTIONS[gesture]['description']
        return "Acción no reconocida" 