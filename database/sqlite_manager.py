import json
import os
import sqlite3
import pickle
from typing import List, Tuple


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "face_recognition.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "script.sql")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _encoding_to_text(encoding) -> str:
    return json.dumps(encoding.tolist())


def _text_to_encoding(vector_text: str):
    import numpy as np

    return np.array(json.loads(vector_text), dtype=float)


def initialize_database() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with _connect() as conn:
        existe_grupos = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'grupos'"
        ).fetchone()

        if not existe_grupos:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
                conn.executescript(schema_file.read())
            return

        _migrate_local_schema(conn)


def _migrate_local_schema(conn: sqlite3.Connection) -> None:
    # Elimina tablas obsoletas de la version conectada a internet.
    conn.execute("DROP TABLE IF EXISTS estudiante_tutor")
    conn.execute("DROP TABLE IF EXISTS tutores")

    # Si estudiantes tiene columnas legacy (matricula/nombre/apellidos), se reconstruye.
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

    # Si logs_acceso aun depende de id_dispositivo, se reconstruye sin esa columna.
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

    # Asegura indices clave para consultas frecuentes en Raspberry Pi.
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


def _ensure_default_group(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id_grupo FROM grupos LIMIT 1").fetchone()
    if row:
        return row[0]

    conn.execute(
        "INSERT INTO grupos (grado, letra, turno) VALUES (?, ?, ?)",
        (1, "A", "MATUTINO"),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def _ensure_group(conn: sqlite3.Connection, grado: int, letra: str, turno: str) -> int:
    letra_norm = letra.strip().upper()[:1]
    turno_norm = turno.strip().upper()

    row = conn.execute(
        "SELECT id_grupo FROM grupos WHERE grado = ? AND letra = ? AND turno = ?",
        (grado, letra_norm, turno_norm),
    ).fetchone()
    if row:
        return row[0]

    conn.execute(
        "INSERT INTO grupos (grado, letra, turno) VALUES (?, ?, ?)",
        (grado, letra_norm, turno_norm),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def create_student(grado: int, letra: str, turno: str) -> int:
    initialize_database()

    with _connect() as conn:
        id_grupo = _ensure_group(conn, grado, letra, turno)
        conn.execute(
            "INSERT INTO estudiantes (id_grupo, estado_activo) VALUES (?, 1)",
            (id_grupo,),
        )
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def save_student_biometric(id_estudiante: int, encoding) -> None:
    initialize_database()

    with _connect() as conn:
        vector_text = _encoding_to_text(encoding)

        conn.execute(
            "DELETE FROM datos_biometricos WHERE tipo_usuario = 'ESTUDIANTE' AND id_usuario_ref = ?",
            (id_estudiante,),
        )
        conn.execute(
            """
            INSERT INTO datos_biometricos (tipo_usuario, id_usuario_ref, vector_facial)
            VALUES ('ESTUDIANTE', ?, ?)
            """,
            (id_estudiante, vector_text),
        )


def load_student_biometrics() -> Tuple[List, List[str], List[int]]:
    initialize_database()

    encodings = []
    etiquetas = []
    student_ids = []

    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT e.id_estudiante, g.grado, g.letra, g.turno, d.vector_facial
            FROM datos_biometricos d
            JOIN estudiantes e ON e.id_estudiante = d.id_usuario_ref
            JOIN grupos g ON g.id_grupo = e.id_grupo
            WHERE d.tipo_usuario = 'ESTUDIANTE' AND e.estado_activo = 1
            """
        ).fetchall()

    for student_id, grado, letra, turno, vector_text in rows:
        encodings.append(_text_to_encoding(vector_text))
        etiquetas.append(f"{grado}{letra}-{turno} #{student_id}")
        student_ids.append(student_id)

    return encodings, etiquetas, student_ids


def get_student_info(id_estudiante: int) -> Tuple[int, str, str, str]:
    """
    Obtiene información del estudiante (grado, letra, turno).
    Retorna: (id_estudiante, grado, letra, turno)
    Retorna None si el estudiante no existe
    """
    initialize_database()

    with _connect() as conn:
        row = conn.execute(
            """
            SELECT e.id_estudiante, g.grado, g.letra, g.turno
            FROM estudiantes e
            JOIN grupos g ON g.id_grupo = e.id_grupo
            WHERE e.id_estudiante = ? AND e.estado_activo = 1
            """,
            (id_estudiante,),
        ).fetchone()

    if row:
        return row  # (id_estudiante, grado, letra, turno)
    return None


def log_access(
    id_usuario_ref: int,
    acceso_concedido: bool,
    tipo_evento: str = "Entrada",
    tipo_usuario: str = "ESTUDIANTE",
) -> None:
    initialize_database()

    tipo_usuario_norm = tipo_usuario.upper()
    if tipo_usuario_norm not in {"ESTUDIANTE", "PERSONAL"}:
        raise ValueError("tipo_usuario debe ser 'ESTUDIANTE' o 'PERSONAL'")

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO logs_acceso (
                tipo_usuario, id_usuario_ref, tipo_evento, acceso_concedido
            ) VALUES (?, ?, ?, ?)
            """,
            (tipo_usuario_norm, id_usuario_ref, tipo_evento, 1 if acceso_concedido else 0),
        )


def _student_exists(conn: sqlite3.Connection, id_estudiante: int) -> bool:
    row = conn.execute(
        "SELECT id_estudiante FROM estudiantes WHERE id_estudiante = ?",
        (id_estudiante,),
    ).fetchone()
    return row is not None


def migrate_pickle_biometrics(
    data_dir: str,
    default_grado: int = 1,
    default_letra: str = "A",
    default_turno: str = "MATUTINO",
) -> int:
    initialize_database()

    if not os.path.isdir(data_dir):
        return 0

    migrados = 0
    for archivo in os.listdir(data_dir):
        if not archivo.endswith(".pkl"):
            continue

        ruta = os.path.join(data_dir, archivo)
        nombre = os.path.splitext(archivo)[0]

        with open(ruta, "rb") as f:
            encoding = pickle.load(f)

        id_estudiante = None
        if nombre.lower().startswith("est_"):
            posible_id = nombre[4:]
            if posible_id.isdigit():
                with _connect() as conn:
                    candidato = int(posible_id)
                    if _student_exists(conn, candidato):
                        id_estudiante = candidato

        if id_estudiante is None:
            id_estudiante = create_student(default_grado, default_letra, default_turno)

        save_student_biometric(id_estudiante, encoding)
        migrados += 1

    return migrados
