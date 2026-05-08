import os
import pickle
import sqlite3
from typing import List, Tuple

from .connection import connect
from .encoding import encoding_to_text, text_to_encoding
from .migrations import initialize_database


def _normalize_grade(grado: int) -> str:
    return str(int(grado))


def _normalize_group(letra: str) -> str:
    return letra.strip().upper()[:1]


def _normalize_shift(turno: str) -> str:
    turno_norm = turno.strip().upper()
    if turno_norm in {"MAT", "MATUTINO"}:
        return "MATUTINO"
    if turno_norm in {"VESP", "VESPERTINO", "VERPERTINO"}:
        return "VESPERTINO"
    raise ValueError("Turno invalido. Usa MATUTINO o VESPERTINO.")


def ensure_grade(conn: sqlite3.Connection, grado: int) -> int:
    grado_clave = _normalize_grade(grado)
    row = conn.execute("SELECT id_grado FROM grados WHERE clave = ?", (grado_clave,)).fetchone()
    if row:
        return row[0]

    nombre = {
        "1": "PRIMERO",
        "2": "SEGUNDO",
        "3": "TERCERO",
    }.get(grado_clave, f"GRADO {grado_clave}")
    conn.execute("INSERT INTO grados (clave, nombre) VALUES (?, ?)", (grado_clave, nombre))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def ensure_group(conn: sqlite3.Connection, letra: str) -> int:
    grupo_clave = _normalize_group(letra)
    row = conn.execute("SELECT id_grupo FROM grupos WHERE clave = ?", (grupo_clave,)).fetchone()
    if row:
        return row[0]

    conn.execute("INSERT INTO grupos (clave) VALUES (?)", (grupo_clave,))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def ensure_shift(conn: sqlite3.Connection, turno: str) -> int:
    turno_clave = _normalize_shift(turno)
    row = conn.execute("SELECT id_turno FROM turnos WHERE clave = ?", (turno_clave,)).fetchone()
    if row:
        return row[0]

    conn.execute("INSERT INTO turnos (clave, nombre) VALUES (?, ?)", (turno_clave, turno_clave))
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def create_student(nombre: str, grado: int, letra: str, turno: str) -> int:
    initialize_database()
    nombre_norm = nombre.strip()
    if not nombre_norm:
        raise ValueError("El nombre del estudiante es obligatorio.")

    with connect() as conn:
        id_grado = ensure_grade(conn, grado)
        id_grupo = ensure_group(conn, letra)
        id_turno = ensure_shift(conn, turno)

        existing = conn.execute(
            """
            SELECT id_estudiante
            FROM estudiantes
            WHERE UPPER(TRIM(nombre)) = UPPER(?)
              AND id_grado = ?
              AND id_grupo = ?
              AND id_turno = ?
            """,
            (nombre_norm, id_grado, id_grupo, id_turno),
        ).fetchone()
        if existing:
            raise ValueError("El estudiante ya existe en la base de datos.")

        try:
            conn.execute(
                """
                INSERT INTO estudiantes (nombre, id_grado, id_grupo, id_turno, estado_activo)
                VALUES (?, ?, ?, ?, 1)
                """,
                (nombre_norm, id_grado, id_grupo, id_turno),
            )
        except sqlite3.IntegrityError as exc:
            if "ya existe" in str(exc).lower():
                raise ValueError("El estudiante ya existe en la base de datos.") from exc
            raise
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
            SELECT e.id_estudiante, e.nombre, gd.clave, gp.clave, tr.clave, d.vector_facial
            FROM datos_biometricos d
            JOIN estudiantes e ON e.id_estudiante = d.id_usuario_ref
            JOIN grados gd ON gd.id_grado = e.id_grado
            JOIN grupos gp ON gp.id_grupo = e.id_grupo
            JOIN turnos tr ON tr.id_turno = e.id_turno
            WHERE d.tipo_usuario = 'ESTUDIANTE' AND e.estado_activo = 1
            """
        ).fetchall()

    for student_id, nombre, grado, letra, turno, vector_text in rows:
        encodings.append(text_to_encoding(vector_text))
        etiquetas.append(f"{nombre} ({grado}{letra}-{turno}) #{student_id}")
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
    default_nombre: str = "ESTUDIANTE",
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
            nombre_migrado = f"{default_nombre} {nombre.upper()}"
            id_estudiante = create_student(nombre_migrado, default_grado, default_letra, default_turno)

        save_student_biometric(id_estudiante, encoding)
        migrados += 1

    return migrados
