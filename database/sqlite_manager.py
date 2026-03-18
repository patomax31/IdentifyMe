import json
import os
import sqlite3
import hashlib
import pickle
from typing import List, Tuple


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "face_recognition.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "script.sql")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _slugify(text: str) -> str:
    return "".join(c for c in text.lower() if c.isalnum()) or "usuario"


def _name_to_employee_code(name: str) -> str:
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]
    return f"EMP-{digest.upper()}"


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

        if existe_grupos:
            return

        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            conn.executescript(schema_file.read())


def _ensure_default_group(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT id_grupo FROM grupos LIMIT 1").fetchone()
    if row:
        return row[0]

    conn.execute(
        "INSERT INTO grupos (grado, letra, turno) VALUES (?, ?, ?)",
        (1, "A", "MATUTINO"),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def _ensure_personal(conn: sqlite3.Connection, nombre_usuario: str) -> int:
    row = conn.execute(
        "SELECT id_personal FROM personal_administrativo WHERE nombre_completo = ?",
        (nombre_usuario,),
    ).fetchone()
    if row:
        return row[0]

    slug = _slugify(nombre_usuario)
    num_empleado = _name_to_employee_code(nombre_usuario)
    correo = f"{slug}@sistema.local"

    conn.execute(
        """
        INSERT INTO personal_administrativo (
            num_empleado, nombre_completo, rol, correo, password_hash, estado_activo
        ) VALUES (?, ?, ?, ?, ?, 1)
        """,
        (num_empleado, nombre_usuario, "OPERADOR", correo, "N/A"),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def save_user_biometric(nombre_usuario: str, encoding) -> None:
    initialize_database()

    with _connect() as conn:
        id_personal = _ensure_personal(conn, nombre_usuario)
        vector_text = _encoding_to_text(encoding)

        conn.execute(
            "DELETE FROM datos_biometricos WHERE tipo_usuario = 'PERSONAL' AND id_usuario_ref = ?",
            (id_personal,),
        )
        conn.execute(
            """
            INSERT INTO datos_biometricos (tipo_usuario, id_usuario_ref, vector_facial)
            VALUES ('PERSONAL', ?, ?)
            """,
            (id_personal, vector_text),
        )


def load_biometrics() -> Tuple[List, List[str], List[int]]:
    initialize_database()

    encodings = []
    nombres = []
    user_ids = []

    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT p.id_personal, p.nombre_completo, d.vector_facial
            FROM datos_biometricos d
            JOIN personal_administrativo p ON p.id_personal = d.id_usuario_ref
            WHERE d.tipo_usuario = 'PERSONAL' AND p.estado_activo = 1
            """
        ).fetchall()

    for user_id, nombre, vector_text in rows:
        encodings.append(_text_to_encoding(vector_text))
        nombres.append(nombre)
        user_ids.append(user_id)

    return encodings, nombres, user_ids


def ensure_device(mac_address: str = "LOCAL-DEVICE", ubicacion: str = "ACCESO_PRINCIPAL") -> int:
    initialize_database()

    with _connect() as conn:
        row = conn.execute(
            "SELECT id_dispositivo FROM dispositivos_raspberry WHERE mac_address = ?",
            (mac_address,),
        ).fetchone()
        if row:
            return row[0]

        conn.execute(
            "INSERT INTO dispositivos_raspberry (mac_address, ubicacion, estado_red) VALUES (?, ?, 1)",
            (mac_address, ubicacion),
        )
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def log_access(id_usuario_ref: int, acceso_concedido: bool, tipo_evento: str = "Entrada") -> None:
    initialize_database()
    id_dispositivo = ensure_device()

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO logs_acceso (
                tipo_usuario, id_usuario_ref, id_dispositivo, tipo_evento, acceso_concedido
            ) VALUES ('PERSONAL', ?, ?, ?, ?)
            """,
            (id_usuario_ref, id_dispositivo, tipo_evento, 1 if acceso_concedido else 0),
        )


def migrate_pickle_biometrics(data_dir: str) -> int:
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

        save_user_biometric(nombre, encoding)
        migrados += 1

    return migrados
