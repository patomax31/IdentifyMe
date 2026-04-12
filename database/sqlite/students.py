import os
import pickle
import sqlite3
from typing import List, Tuple

from .connection import connect
from .encoding import encoding_to_text, text_to_encoding
from .migrations import initialize_database


def ensure_group(conn: sqlite3.Connection, grado: int, letra: str, turno: str) -> int:
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

    with connect() as conn:
        id_grupo = ensure_group(conn, grado, letra, turno)
        conn.execute(
            "INSERT INTO estudiantes (id_grupo, estado_activo) VALUES (?, 1)",
            (id_grupo,),
        )
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def save_student_biometric(id_estudiante: int, encoding) -> None:
    initialize_database()

    with connect() as conn:
        vector_text = encoding_to_text(encoding)

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

    with connect() as conn:
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
        encodings.append(text_to_encoding(vector_text))
        etiquetas.append(f"{grado}{letra}-{turno} #{student_id}")
        student_ids.append(student_id)

    return encodings, etiquetas, student_ids


def student_exists(conn: sqlite3.Connection, id_estudiante: int) -> bool:
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
                with connect() as conn:
                    candidato = int(posible_id)
                    if student_exists(conn, candidato):
                        id_estudiante = candidato

        if id_estudiante is None:
            id_estudiante = create_student(default_grado, default_letra, default_turno)

        save_student_biometric(id_estudiante, encoding)
        migrados += 1

    return migrados
