import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establecer conexión con la base de datos MySQL"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                logger.info("Conexión exitosa a MySQL")
        except Error as e:
            logger.error(f"Error al conectar a MySQL: {e}")
            raise
    
    def create_tables(self):
        """Crear las tablas necesarias si no existen"""
        try:
            cursor = self.connection.cursor()
            
            # Crear tabla de acciones
            create_table_query = """
            CREATE TABLE IF NOT EXISTS acciones (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT DEFAULT 1,
                gesto VARCHAR(50) NOT NULL,
                accion_ejecutada VARCHAR(100) NOT NULL,
                confianza DECIMAL(5,2) NOT NULL,
                timestamp VARCHAR(40) NOT NULL
            )
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("Tabla 'acciones' creada/verificada exitosamente")
            
        except Error as e:
            logger.error(f"Error al crear tablas: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def insert_action(self, gesto, accion_ejecutada, confianza, usuario_id=1, timestamp=None):
        """Insertar una nueva acción en la base de datos, usando hora de Perú en formato ISO 8601 si se provee.
        IMPORTANTE: El campo 'timestamp' en la tabla 'acciones' debe ser VARCHAR(40) para soportar zona horaria.
        """
        try:
            cursor = self.connection.cursor()
            if timestamp is not None:
                insert_query = """
                INSERT INTO acciones (usuario_id, gesto, accion_ejecutada, confianza, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (usuario_id, gesto, accion_ejecutada, confianza, timestamp))
            else:
                insert_query = """
                INSERT INTO acciones (usuario_id, gesto, accion_ejecutada, confianza)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_query, (usuario_id, gesto, accion_ejecutada, confianza))
            self.connection.commit()
            logger.info(f"Acción registrada: {gesto} -> {accion_ejecutada}")
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error al insertar acción: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_recent_actions(self, limit=50):
        """Obtener las acciones más recientes"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=True)
            select_query = """
            SELECT * FROM acciones 
            ORDER BY timestamp DESC 
            LIMIT %s
            """
            cursor.execute(select_query, (limit,))
            actions = cursor.fetchall()
            return actions
        except Error as e:
            logger.error(f"Error al obtener acciones: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def get_gesture_stats(self):
        """Obtener estadísticas de gestos"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=True)
            stats_query = """
            SELECT 
                gesto,
                COUNT(*) as total_uses,
                AVG(confianza) as avg_confidence,
                MAX(timestamp) as last_used
            FROM acciones 
            GROUP BY gesto 
            ORDER BY total_uses DESC
            """
            cursor.execute(stats_query)
            stats = cursor.fetchall()
            return stats
        except Error as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """Cerrar la conexión a la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Conexión a MySQL cerrada") 