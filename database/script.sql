-- ==============================================================================
-- PROYECTO: SISTEMA BIOMÉTRICO FACIAL BASADO EN RASPBERRY PI PARA CONTROL DE ACCESO
-- MOTOR: SQLite 3
-- DESCRIPCIÓN: Esquema físico de la base de datos
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
    matricula TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    id_grupo INTEGER NOT NULL,
    estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1)),
    FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo) ON DELETE RESTRICT
);

-- 3. Tabla: tutores
CREATE TABLE tutores (
    id_tutor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    telefono TEXT NOT NULL,
    correo TEXT
);

-- 4. Tabla Intermedia: estudiante_tutor (Relación N:M)
CREATE TABLE estudiante_tutor (
    id_estudiante INTEGER NOT NULL,
    id_tutor INTEGER NOT NULL,
    parentesco TEXT NOT NULL,
    contacto_emergencia INTEGER NOT NULL DEFAULT 0 CHECK (contacto_emergencia IN (0, 1)),
    autorizado_recoger INTEGER NOT NULL DEFAULT 0 CHECK (autorizado_recoger IN (0, 1)),
    PRIMARY KEY (id_estudiante, id_tutor),
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (id_tutor) REFERENCES tutores(id_tutor) ON DELETE CASCADE
);

-- 5. Tabla: personal_administrativo
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

-- 6. Tabla: datos_biometricos 
-- Almacena vectores faciales tanto de estudiantes como de personal
CREATE TABLE datos_biometricos (
    id_biometria INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
    id_usuario_ref INTEGER NOT NULL,
    vector_facial TEXT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 7. Tabla: dispositivos_raspberry
CREATE TABLE dispositivos_raspberry (
    id_dispositivo INTEGER PRIMARY KEY AUTOINCREMENT,
    mac_address TEXT NOT NULL UNIQUE,
    ubicacion TEXT NOT NULL,
    estado_red INTEGER NOT NULL DEFAULT 1 CHECK (estado_red IN (0, 1))
);

-- ==============================================================================
-- MÓDULO: TRANSACCIONES
-- ==============================================================================

-- 8. Tabla: logs_acceso 
-- Registra entradas y salidas de estudiantes y personal
CREATE TABLE logs_acceso (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
    id_usuario_ref INTEGER NOT NULL,
    id_dispositivo INTEGER NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_evento TEXT NOT NULL CHECK (tipo_evento IN ('Entrada', 'Salida')),
    acceso_concedido INTEGER NOT NULL CHECK (acceso_concedido IN (0, 1)),
    FOREIGN KEY (id_dispositivo) REFERENCES dispositivos_raspberry(id_dispositivo) ON DELETE RESTRICT
);