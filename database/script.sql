-- ==============================================================================
-- PROYECTO: SISTEMA BIOMETRICO FACIAL BASADO EN RASPBERRY PI PARA CONTROL DE ACCESO
-- MOTOR: SQLite 3
-- DESCRIPCION: Esquema fisico local (sin internet, un solo dispositivo)
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- ==============================================================================
-- MODULO: CATALOGOS ESCOLARES
-- ==============================================================================

CREATE TABLE grados (
    id_grado INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE grupos (
    id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE
);

CREATE TABLE turnos (
    id_turno INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL UNIQUE
);

-- ==============================================================================
-- MODULO: ENTORNO ESCOLAR Y USUARIOS
-- ==============================================================================

CREATE TABLE estudiantes (
    id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    id_grado INTEGER NOT NULL,
    id_grupo INTEGER NOT NULL,
    id_turno INTEGER NOT NULL,
    estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1)),
    FOREIGN KEY (id_grado) REFERENCES grados(id_grado) ON DELETE RESTRICT,
    FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo) ON DELETE RESTRICT,
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno) ON DELETE RESTRICT
);

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
-- MODULO: BIOMETRIA Y HARDWARE (TABLAS POLIMORFICAS)
-- ==============================================================================

CREATE TABLE datos_biometricos (
    id_biometria INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
    id_usuario_ref INTEGER NOT NULL,
    vector_facial TEXT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- MODULO: TRANSACCIONES
-- ==============================================================================

CREATE TABLE logs_acceso (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
    id_usuario_ref INTEGER NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_evento TEXT NOT NULL CHECK (tipo_evento IN ('Entrada', 'Salida')),
    acceso_concedido INTEGER NOT NULL CHECK (acceso_concedido IN (0, 1))
);

-- ==============================================================================
-- CATALOGOS BASE
-- ==============================================================================

INSERT INTO grados (clave, nombre) VALUES
    ('1', 'PRIMERO'),
    ('2', 'SEGUNDO'),
    ('3', 'TERCERO');

INSERT INTO turnos (clave, nombre) VALUES
    ('MATUTINO', 'MATUTINO'),
    ('VESPERTINO', 'VESPERTINO');

-- ==============================================================================
-- INDICES
-- ==============================================================================

CREATE UNIQUE INDEX ux_datos_biometricos_usuario
ON datos_biometricos (tipo_usuario, id_usuario_ref);

CREATE INDEX ix_logs_acceso_usuario_fecha
ON logs_acceso (tipo_usuario, id_usuario_ref, fecha_hora DESC);