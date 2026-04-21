from .connection import connect
from .migrations import initialize_database


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

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO logs_acceso (
                tipo_usuario, id_usuario_ref, tipo_evento, acceso_concedido
            ) VALUES (?, ?, ?, ?)
            """,
            (tipo_usuario_norm, id_usuario_ref, tipo_evento, 1 if acceso_concedido else 0),
        )
