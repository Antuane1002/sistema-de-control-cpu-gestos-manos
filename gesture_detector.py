import cv2
import mediapipe as mp
import numpy as np
import time
from config import GESTURE_CONFIG, GESTURE_ACTIONS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,  # Reducido de 0.9 para mayor estabilidad
            min_tracking_confidence=GESTURE_CONFIG['min_tracking_confidence']
        )
        
        self.current_gesture = None
        self.gesture_start_time = None
        self.last_action_time = 0
        self.action_cooldown = 2.0  # segundos entre acciones
        self.gesture_hold_time = 1.0  # Exigir 1 segundo de estabilidad
        
    def detect_gesture(self, hand_landmarks):
        """Detectar el gesto basado en los landmarks de la mano"""
        if not hand_landmarks:
            return None, 0.0
            
        try:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z])
            
            landmarks = np.array(landmarks)
            
            # Detectar gestos específicos
            gesture, confidence = self._classify_gesture(landmarks)
            
            return gesture, confidence
        except Exception as e:
            logger.error(f"Error en detect_gesture: {e}")
            return None, 0.0
    
    def _classify_gesture(self, landmarks):
        """Clasificar el gesto basado en la posición de los dedos"""
        try:
            # Obtener puntos clave de los dedos
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]
            
            # Puntos de referencia (base de los dedos)
            thumb_base = landmarks[2]
            index_base = landmarks[5]
            middle_base = landmarks[9]
            ring_base = landmarks[13]
            pinky_base = landmarks[17]
            
            # Calcular si los dedos están extendidos
            fingers_extended = []
            
            # Pulgar (comparar con el eje X)
            thumb_extended = thumb_tip[0] > thumb_base[0]
            fingers_extended.append(thumb_extended)
            
            # Otros dedos (comparar con el eje Y)
            for tip, base in [(index_tip, index_base), (middle_tip, middle_base), 
                              (ring_tip, ring_base), (pinky_tip, pinky_base)]:
                finger_extended = tip[1] < base[1]
                fingers_extended.append(finger_extended)
            
            # Clasificar gestos
            gesture, confidence = self._identify_gesture(fingers_extended, landmarks)
            
            return gesture, confidence
        except Exception as e:
            logger.error(f"Error en _classify_gesture: {e}")
            return None, 0.0
    
    def _identify_gesture(self, fingers_extended, landmarks):
        """Identificar el gesto específico basado en los dedos extendidos"""
        try:
            # Contar dedos extendidos
            extended_count = sum(fingers_extended)
            
            # Mano abierta: todos los dedos extendidos
            if extended_count == 5:
                return 'mano_abierta', 0.95
            
            # Puño cerrado: ningún dedo extendido
            elif extended_count == 0:
                return 'puño_cerrado', 0.90
            
            # Pulgar arriba: solo pulgar extendido (índice 0)
            elif fingers_extended[0] and not any(fingers_extended[1:]):
                return 'pulgar_arriba', 0.85
            
            # Dos dedos: índice y medio extendidos
            elif fingers_extended[1] and fingers_extended[2] and not fingers_extended[3] and not fingers_extended[4]:
                return 'dos_dedos', 0.88
            
            # Rock & roll: índice y meñique extendidos
            elif fingers_extended[1] and fingers_extended[4] and not fingers_extended[2] and not fingers_extended[3]:
                return 'rock_roll', 0.82
            
            # Casos adicionales para mejor reconocimiento
            # Pulgar arriba con variaciones menores
            elif fingers_extended[0] and sum(fingers_extended[1:]) <= 1:
                return 'pulgar_arriba', 0.80
            
            # Mano semi-abierta (3-4 dedos)
            elif extended_count >= 3:
                return 'mano_abierta', 0.85
            
            # Gesto no reconocido
            else:
                return None, 0.0
        except Exception as e:
            logger.error(f"Error en _identify_gesture: {e}")
            return None, 0.0
    
    def process_frame(self, frame):
        """Procesar un frame de la cámara y detectar gestos"""
        try:
            # Verificar que el frame sea válido
            if frame is None or frame.size == 0:
                logger.warning("Frame inválido recibido")
                return frame, None, 0.0
            
            # Convertir BGR a RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Procesar con MediaPipe
            results = self.hands.process(rgb_frame)
            
            gesture = None
            confidence = 0.0
            fingers_extended = [False]*5
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    try:
                        gesture, confidence, fingers_extended = self.detect_gesture_debug(hand_landmarks)
                        
                        # Dibujar landmarks
                        self.mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style()
                        )
                        
                        # Mostrar vector de dedos y confianza en pantalla
                        info_text = f"Dedos: {fingers_extended} | Confianza: {confidence:.2f}"
                        cv2.putText(frame, info_text, (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        
                        # Mostrar el gesto detectado y la confianza en el overlay del video
                        gesture_text = f"Gesto: {gesture if gesture else 'Ninguno'} | Confianza: {confidence:.2f}"
                        cv2.putText(frame, gesture_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        
                        # Log en archivo para depuración (solo si hay gesto detectado)
                        if gesture:
                            with open('debug_gestos.txt', 'a') as f:
                                f.write(f"{time.strftime('%H:%M:%S')} - Dedos: {fingers_extended} | Confianza: {confidence:.2f} | Gesto: {gesture}\n")
                        
                        break  # Solo procesar la primera mano
                        
                    except Exception as e:
                        logger.error(f"Error procesando landmarks: {e}")
                        continue
            else:
                # Si no hay mano detectada, mostrar info
                info_text = f"Dedos: {fingers_extended} | Confianza: {confidence:.2f}"
                cv2.putText(frame, info_text, (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                gesture_text = f"Gesto: Ninguno | Confianza: 0.00"
                cv2.putText(frame, gesture_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            return frame, gesture, confidence
            
        except Exception as e:
            logger.error(f"Error en process_frame: {e}")
            # Retornar el frame original sin procesar en caso de error
            return frame, None, 0.0
    
    def detect_gesture_debug(self, hand_landmarks):
        try:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y, lm.z])
            landmarks = np.array(landmarks)
            
            # Obtener puntos clave de los dedos
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]
            
            # Puntos de referencia (base de los dedos)
            thumb_base = landmarks[2]
            index_base = landmarks[5]
            middle_base = landmarks[9]
            ring_base = landmarks[13]
            pinky_base = landmarks[17]
            
            # Calcular si los dedos están extendidos
            fingers_extended = []
            
            # Pulgar (comparar con el eje X) - ajustado para mejor detección
            thumb_extended = thumb_tip[0] < thumb_base[0] + 0.02
            fingers_extended.append(thumb_extended)
            
            # Otros dedos (comparar con el eje Y) - ajustado para mejor detección
            for tip, base in [(index_tip, index_base), (middle_tip, middle_base), 
                              (ring_tip, ring_base), (pinky_tip, pinky_base)]:
                finger_extended = tip[1] < base[1] + 0.02
                fingers_extended.append(finger_extended)
            
            # Clasificar gestos usando la lógica correcta
            gesture, confidence = self._identify_gesture(fingers_extended, landmarks)
            
            return gesture, confidence, fingers_extended
            
        except Exception as e:
            logger.error(f"Error en detect_gesture_debug: {e}")
            return None, 0.0, [False]*5
    
    def should_execute_action(self, gesture, confidence):
        """Determinar si se debe ejecutar una acción basado en el gesto"""
        current_time = time.time()
        
        # Verificar si el gesto ha cambiado
        if gesture != self.current_gesture:
            self.current_gesture = gesture
            self.gesture_start_time = current_time
            return False
        
        # Verificar si el gesto se ha mantenido por el tiempo requerido
        if (self.gesture_start_time and 
            current_time - self.gesture_start_time >= self.gesture_hold_time):
            
            # Verificar cooldown entre acciones
            if current_time - self.last_action_time >= self.action_cooldown:
                self.last_action_time = current_time
                return True
        
        return False
    
    def get_gesture_info(self, gesture):
        """Obtener información sobre un gesto específico"""
        if gesture in GESTURE_ACTIONS:
            return GESTURE_ACTIONS[gesture]
        return None
    
    def release(self):
        """Liberar recursos"""
        try:
            if self.hands:
                self.hands.close()
        except Exception as e:
            logger.error(f"Error al liberar recursos: {e}") 