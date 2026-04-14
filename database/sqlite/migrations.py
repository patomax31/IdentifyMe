import os
import sqlite3

from .connection import connect
from .paths import DB_PATH, SCHEMA_PATH


def initialize_database() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with connect() as conn:
        existe_grupos = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'grupos'"
        ).fetchone()

        if not existe_grupos:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
                conn.executescript(schema_file.read())
            return

        migrate_local_schema(conn)


def migrate_local_schema(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TABLE IF EXISTS estudiante_tutor")
    conn.execute("DROP TABLE IF EXISTS tutores")

    estudiantes_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(estudiantes)").fetchall()
    }
    if {"matricula", "nombre", "apellidos"}.issubset(estudiantes_columns):
        conn.execute(
            """
            CREATE TABLE estudiantes_new (
                id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
                id_grupo INTEGER NOT NULL,
                estado_activo INTEGER NOT NULL DEFAULT 1 CHECK (estado_activo IN (0, 1)),
                FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo) ON DELETE RESTRICT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO estudiantes_new (id_estudiante, id_grupo, estado_activo)
            SELECT id_estudiante, id_grupo, estado_activo
            FROM estudiantes
            """
        )
        conn.execute("DROP TABLE estudiantes")
        conn.execute("ALTER TABLE estudiantes_new RENAME TO estudiantes")

    log_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(logs_acceso)").fetchall()
    }
    if "id_dispositivo" in log_columns:
        conn.execute(
            """
            CREATE TABLE logs_acceso_new (
                id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('ESTUDIANTE', 'PERSONAL')),
                id_usuario_ref INTEGER NOT NULL,
                fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_evento TEXT NOT NULL CHECK (tipo_evento IN ('Entrada', 'Salida')),
                acceso_concedido INTEGER NOT NULL CHECK (acceso_concedido IN (0, 1))
            )
            """
        )
        conn.execute(
            """
            INSERT INTO logs_acceso_new (
                id_log, tipo_usuario, id_usuario_ref, fecha_hora, tipo_evento, acceso_concedido
            )
            SELECT id_log, tipo_usuario, id_usuario_ref, fecha_hora, tipo_evento, acceso_concedido
            FROM logs_acceso
            """
        )
        conn.execute("DROP TABLE logs_acceso")
        conn.execute("ALTER TABLE logs_acceso_new RENAME TO logs_acceso")

    conn.execute("DROP TABLE IF EXISTS dispositivos_raspberry")

    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_datos_biometricos_usuario
        ON datos_biometricos (tipo_usuario, id_usuario_ref)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_logs_acceso_usuario_fecha
        ON logs_acceso (tipo_usuario, id_usuario_ref, fecha_hora DESC)
        """
    )
