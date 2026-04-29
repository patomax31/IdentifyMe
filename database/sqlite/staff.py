import hashlib
import hmac
import sqlite3
from os import urandom
from typing import Dict, List, Optional, Tuple

from .connection import connect
from .encoding import encoding_to_text, text_to_encoding
from .migrations import initialize_database


PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 120_000


def hash_password(password: str) -> str:
    password_norm = password.strip()
    if len(password_norm) < 8:
        raise ValueError("La contrasena debe tener al menos 8 caracteres.")

    salt = urandom(16)
    digest = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password_norm.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return (
        f"pbkdf2_{PBKDF2_ALGORITHM}"
        f"${PBKDF2_ITERATIONS}"
        f"${salt.hex()}"
        f"${digest.hex()}"
    )


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations_raw, salt_hex, digest_hex = password_hash.split("$", 3)
        if not scheme.startswith("pbkdf2_"):
            return False

        algorithm = scheme.replace("pbkdf2_", "", 1)
        iterations = int(iterations_raw)
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False

    provided_digest = hashlib.pbkdf2_hmac(
        algorithm,
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(provided_digest, expected_digest)


def count_active_staff() -> int:
    initialize_database()
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM personal_administrativo WHERE estado_activo = 1"
        ).fetchone()
    return int(row[0]) if row else 0


def create_staff(
    *,
    num_empleado: str,
    nombre_completo: str,
    rol: str,
    correo: str,
    password_plain: str,
) -> int:
    initialize_database()

    num_empleado_norm = num_empleado.strip().upper()
    nombre_norm = nombre_completo.strip()
    rol_norm = rol.strip().upper()
    correo_norm = correo.strip().lower()

    if not num_empleado_norm:
        raise ValueError("El numero de empleado es obligatorio.")
    if not nombre_norm:
        raise ValueError("El nombre completo es obligatorio.")
    if not rol_norm:
        raise ValueError("El rol es obligatorio.")
    if "@" not in correo_norm:
        raise ValueError("El correo no es valido.")

    password_hash = hash_password(password_plain)

    with connect() as conn:
        try:
            conn.execute(
                """
                INSERT INTO personal_administrativo (
                    num_empleado,
                    nombre_completo,
                    rol,
                    correo,
                    password_hash,
                    estado_activo
                ) VALUES (?, ?, ?, ?, ?, 1)
                """,
                (num_empleado_norm, nombre_norm, rol_norm, correo_norm, password_hash),
            )
        except sqlite3.IntegrityError as exc:
            message = str(exc).lower()
            if "num_empleado" in message:
                raise ValueError("El numero de empleado ya existe.") from exc
            if "correo" in message:
                raise ValueError("El correo ya existe.") from exc
            raise

        row = conn.execute("SELECT last_insert_rowid()").fetchone()
    return int(row[0])


def save_staff_biometric(id_personal: int, encoding) -> None:
    initialize_database()
    vector_text = encoding_to_text(encoding)

    with connect() as conn:
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


def load_staff_biometrics() -> Tuple[List, List[str], List[int], List[str]]:
    initialize_database()

    encodings = []
    labels = []
    staff_ids = []
    roles = []

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                p.id_personal,
                p.nombre_completo,
                p.rol,
                d.vector_facial
            FROM datos_biometricos d
            JOIN personal_administrativo p
                ON p.id_personal = d.id_usuario_ref
            WHERE d.tipo_usuario = 'PERSONAL' AND p.estado_activo = 1
            ORDER BY p.id_personal ASC
            """
        ).fetchall()

    for id_personal, nombre_completo, rol, vector_text in rows:
        encodings.append(text_to_encoding(vector_text))
        labels.append(f"{nombre_completo} ({rol}) #{id_personal}")
        staff_ids.append(int(id_personal))
        roles.append(str(rol).upper())

    return encodings, labels, staff_ids, roles


def get_staff_identity(id_personal: int) -> Optional[Dict[str, str]]:
    initialize_database()

    with connect() as conn:
        row = conn.execute(
            """
            SELECT id_personal, num_empleado, nombre_completo, rol, correo
            FROM personal_administrativo
            WHERE id_personal = ? AND estado_activo = 1
            """,
            (id_personal,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id_personal": str(row[0]),
        "num_empleado": str(row[1]),
        "nombre_completo": str(row[2]),
        "rol": str(row[3]).upper(),
        "correo": str(row[4]).lower(),
    }
