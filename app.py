from flask import Flask, render_template, jsonify, request, Response
from database import DatabaseManager
from config import GESTURE_ACTIONS, CAMERA_CONFIG
import cv2
import mediapipe as mp
import numpy as np
import time
import logging
from gesture_detector import GestureDetector
from system_controller import SystemController
import threading
from datetime import datetime
import pytz
import gc

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar componentes
db = DatabaseManager()
gesture_detector = GestureDetector()
system_controller = SystemController()

# Variables globales para el último gesto detectado y frame
last_gesture = None
last_confidence = 0.0
last_frame = None
camera_running = False
camera_thread_instance = None
lock = threading.Lock()

# Añadir variable global para el índice de cámara
camera_index = 0

def camera_thread():
    global last_gesture, last_confidence, last_frame, camera_running, camera_index
    
    logger.info(f"Iniciando hilo de cámara con índice {camera_index}")
    
    while camera_running:  # Solo ejecutar mientras camera_running sea True
        cap = None
        try:
            # Liberar memoria antes de conectar
            gc.collect()
            
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # Usar DirectShow en Windows
            if not cap.isOpened():
                logger.error(f'No se pudo abrir la cámara {camera_index}')
                break  # Salir del bucle si no se puede abrir la cámara
                
            # Configurar cámara con valores más conservadores
            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 15)  # Reducir FPS para mayor estabilidad
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Desactivar autofocus
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Configurar exposición manual
            except Exception as e:
                logger.warning(f'Error al configurar cámara: {e}')
                
            # Verificar que la cámara esté funcionando
            ret, test_frame = cap.read()
            if not ret or test_frame is None:
                logger.error('La cámara no puede leer frames')
                break
                
            logger.info(f'Cámara {camera_index} conectada exitosamente')
            last_action_time = 0
            action_cooldown = 2.0  # segundos entre acciones
            last_gesture_executed = None
            consecutive_errors = 0
            max_consecutive_errors = 5  # Reducir tolerancia
            frame_count = 0
            last_gc_time = time.time()
            
            while camera_running:  # Verificar camera_running en cada iteración
                try:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        consecutive_errors += 1
                        if consecutive_errors > max_consecutive_errors:
                            logger.error(f'Demasiados errores consecutivos ({consecutive_errors}). Deteniendo cámara...')
                            break
                        else:
                            logger.warning(f'Error al leer frame (intento {consecutive_errors}/{max_consecutive_errors})')
                        time.sleep(0.1)
                        continue
                        
                    consecutive_errors = 0
                    frame_count += 1
                    
                    # Limpiar memoria cada 100 frames
                    if frame_count % 100 == 0:
                        current_time = time.time()
                        if current_time - last_gc_time > 5:  # Cada 5 segundos máximo
                            gc.collect()
                            last_gc_time = current_time
                    
                    # Procesar frame con manejo de errores mejorado
                    try:
                        processed_frame, gesture, confidence = gesture_detector.process_frame(frame)
                        
                        # Verificar que el frame procesado sea válido
                        if processed_frame is not None and processed_frame.size > 0:
                            with lock:
                                # Liberar memoria del frame anterior
                                if last_frame is not None:
                                    del last_frame
                                last_frame = processed_frame.copy()
                                last_gesture = gesture
                                last_confidence = confidence
                                
                            # Ejecutar acción si corresponde
                            current_time = time.time()
                            if gesture in GESTURE_ACTIONS:
                                min_conf = float(GESTURE_ACTIONS[gesture].get('min_confidence', 0.7))
                                if confidence >= min_conf:
                                    if (last_gesture_executed != gesture or (current_time - last_action_time) > action_cooldown):
                                        success = system_controller.execute_action(gesture)
                                        if success:
                                            action_info = GESTURE_ACTIONS[gesture]
                                            lima = pytz.timezone('America/Lima')
                                            now = datetime.now(lima).isoformat()
                                            db.insert_action(
                                                gesto=gesture,
                                                accion_ejecutada=action_info['description'],
                                                confianza=confidence,
                                                timestamp=now
                                            )
                                            logger.info(f"Acción ejecutada y registrada: {gesture}")
                                            last_action_time = current_time
                                            last_gesture_executed = gesture
                        else:
                            logger.warning("Frame procesado inválido, saltando...")
                            
                    except Exception as e:
                        logger.error(f'Error al procesar frame: {e}')
                        consecutive_errors += 1
                        if consecutive_errors > max_consecutive_errors:
                            break
                        continue
                        
                except Exception as e:
                    logger.error(f'Error general en hilo de cámara: {e}')
                    consecutive_errors += 1
                    if consecutive_errors > max_consecutive_errors:
                        logger.error('Demasiados errores, deteniendo cámara...')
                        break
                    time.sleep(0.1)
                    continue
                    
                time.sleep(0.05)  # ~20 FPS para mayor estabilidad
                
            # Limpiar recursos
            if cap:
                cap.release()
            logger.info('Hilo de cámara detenido')
            break  # Salir del bucle principal
            
        except Exception as e:
            logger.error(f'Error crítico en bucle de cámara: {e}')
            if cap:
                cap.release()
            break  # Salir del bucle principal

# Función para iniciar el hilo de cámara de forma segura
def start_camera_thread():
    global camera_running, camera_thread_instance
    
    if camera_thread_instance and camera_thread_instance.is_alive():
        logger.warning("Hilo de cámara ya está ejecutándose")
        return False
    
    camera_running = True
    camera_thread_instance = threading.Thread(target=camera_thread, daemon=True)
    camera_thread_instance.start()
    logger.info("Hilo de cámara iniciado")
    return True

# Función para detener el hilo de cámara de forma segura
def stop_camera_thread():
    global camera_running, camera_thread_instance
    
    camera_running = False
    
    if camera_thread_instance and camera_thread_instance.is_alive():
        camera_thread_instance.join(timeout=3.0)  # Esperar máximo 3 segundos
        if camera_thread_instance.is_alive():
            logger.warning("Hilo de cámara no se detuvo correctamente")
        else:
            logger.info("Hilo de cámara detenido correctamente")
    
    camera_thread_instance = None

@app.route('/')
def index():
    return render_template('index.html', camera_index=camera_index)

@app.route('/video_feed')
def video_feed():
    def gen_frames():
        consecutive_empty_frames = 0
        max_empty_frames = 10
        
        while True:
            try:
                with lock:
                    frame = last_frame.copy() if last_frame is not None else None
                    
                if frame is not None and frame.size > 0:
                    consecutive_empty_frames = 0
                    # Comprimir con menor calidad para mejor rendimiento
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                    ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                    
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    else:
                        logger.warning("Error al codificar frame")
                        
                else:
                    consecutive_empty_frames += 1
                    if consecutive_empty_frames > max_empty_frames:
                        logger.warning("Demasiados frames vacíos, reiniciando stream...")
                        consecutive_empty_frames = 0
                        
                time.sleep(0.05)  # ~20 FPS
                
            except Exception as e:
                logger.error(f"Error en video_feed: {e}")
                time.sleep(0.1)
                continue
                
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/start_camera')
def start_camera():
    success = start_camera_thread()
    return jsonify({'success': success, 'message': 'Cámara iniciada' if success else 'Cámara ya está ejecutándose'})

@app.route('/api/stop_camera')
def stop_camera():
    stop_camera_thread()
    return jsonify({'success': True, 'message': 'Cámara detenida'})

@app.route('/api/camera_status')
def camera_status():
    with lock:
        gesture = last_gesture
        confidence = last_confidence
    
    is_running = camera_thread_instance is not None and camera_thread_instance.is_alive()
    
    return jsonify({
        'is_streaming': is_running,
        'current_gesture': gesture,
        'current_confidence': confidence,
        'gesture_info': GESTURE_ACTIONS.get(gesture, {}) if gesture else {}
    })

@app.route('/api/actions')
def get_actions():
    try:
        limit = request.args.get('limit', 50, type=int)
        actions = db.get_recent_actions(limit)
        return jsonify({'success': True, 'actions': actions})
    except Exception as e:
        logger.error(f"Error al obtener acciones: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats')
def get_stats():
    try:
        stats = db.get_gesture_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/gestures')
def get_gestures():
    try:
        gestures = []
        for gesture, info in GESTURE_ACTIONS.items():
            gestures.append({
                'name': gesture,
                'description': info['description'],
                'action': info['action']
            })
        return jsonify({'success': True, 'gestures': gestures})
    except Exception as e:
        logger.error(f"Error al obtener gestos: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/set_camera', methods=['POST'])
def set_camera():
    global camera_index
    data = request.get_json()
    idx = data.get('camera_index', 0)
    try:
        idx = int(idx)
        
        # Detener cámara actual si está ejecutándose
        if camera_running:
            stop_camera_thread()
            time.sleep(1)  # Esperar a que se libere la cámara
        
        camera_index = idx
        
        # Reiniciar cámara con nuevo índice
        start_camera_thread()
        
        return jsonify({'success': True, 'camera_index': camera_index})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000) 