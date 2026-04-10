-- ==============================================================================
-- PROYECTO: SISTEMA BIOMÉTRICO FACIAL BASADO EN RASPBERRY PI PARA CONTROL DE ACCESO
-- MOTOR: SQLite 3
-- DESCRIPCION: Esquema fisico local (sin internet, un solo dispositivo)
-- ==============================================================================

-- 0. Habilitar la integridad referencial (Obligatorio en SQLite)
PRAGMA foreign_keys = ON;

-- ==============================================================================
-- MÓDULO: ENTORNO ESCOLAR Y USUARIOS
-- ==============================================================================

-- 1. Tabla: grupos
CREATE TABLE grupos (
    id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
    grado INTEGER NOT NULL CHECK (grado IN (1, 2, 3)),
    letra TEXT NOT NULL,
    turno TEXT NOT NULL
);

-- 2. Tabla: estudiantes
CREATE TABLE estudiantes (
    id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    id_grupo INTEGER NOT NULL,
    estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1)),
    FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo) ON DELETE RESTRICT
);

-- 3. Tabla: personal_administrativo
CREATE TABLE personal_administrativo (
    id_personal INTEGER PRIMARY KEY AUTOINCREMENT,
    num_empleado TEXT NOT NULL UNIQUE,
    nombre_completo TEXT NOT NULL,
    rol TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1))
);

-- ==============================================================================
-- MÓDULO: BIOMETRÍA Y HARDWARE (Tablas Polimórficas)
-- ==============================================================================

-- 4. Tabla: datos_biometricos 
-- Almacena vectores faciales tanto de estudiantes como de personal
CREATE TABLE datos_biometricos (
    id_biometria INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
    id_usuario_ref INTEGER NOT NULL,
    vector_facial TEXT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- MÓDULO: TRANSACCIONES
-- ==============================================================================

-- 5. Tabla: logs_acceso 
-- Registra entradas y salidas de estudiantes y personal
CREATE TABLE logs_acceso (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
    id_usuario_ref INTEGER NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_evento TEXT NOT NULL CHECK (tipo_evento IN ('Entrada', 'Salida')),
    acceso_concedido INTEGER NOT NULL CHECK (acceso_concedido IN (0, 1))
);

-- ============================================================================== 
-- INDICES PARA EFICIENCIA EN CONSULTAS FRECUENTES (RASPBERRY PI)
-- ==============================================================================

-- Acelera la carga de vectores para autenticacion y evita duplicados por usuario/tipo.
CREATE UNIQUE INDEX ux_datos_biometricos_usuario
ON datos_biometricos (tipo_usuario, id_usuario_ref);

-- Acelera auditoria e historicos por usuario y por fecha.
CREATE INDEX ix_logs_acceso_usuario_fecha
ON logs_acceso (tipo_usuario, id_usuario_ref, fecha_hora DESC);