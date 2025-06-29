-- Script para configurar la base de datos del sistema de control por gestos
-- Ejecutar este script en MySQL para crear la base de datos y tabla necesarias

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS control_gestos;
USE control_gestos;

-- Crear la tabla de acciones
CREATE TABLE IF NOT EXISTS acciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT DEFAULT 1,
    gesto VARCHAR(50) NOT NULL,
    accion_ejecutada VARCHAR(100) NOT NULL,
    confianza DECIMAL(5,2) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_gesto ON acciones(gesto);
CREATE INDEX idx_timestamp ON acciones(timestamp);
CREATE INDEX idx_usuario_id ON acciones(usuario_id);

-- Insertar algunos datos de ejemplo (opcional)
INSERT INTO acciones (gesto, accion_ejecutada, confianza) VALUES
('mano_abierta', 'Abrir navegador Chrome', 0.95),
('puño_cerrado', 'Cerrar ventana activa', 0.88),
('pulgar_arriba', 'Subir volumen del sistema', 0.92),
('dos_dedos', 'Tomar captura de pantalla', 0.85),
('rock_roll', 'Refrescar página (F5)', 0.90);

-- Verificar que la tabla se creó correctamente
SELECT * FROM acciones LIMIT 5; 