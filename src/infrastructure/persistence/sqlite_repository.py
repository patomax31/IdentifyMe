from typing import List, Tuple

from database.sqlite_manager import (
    initialize_database,
    load_student_biometrics,
    create_student,
    save_student_biometric,
    log_access,
)


class SQLiteRepository:
    """Adapter that exposes persistence operations used by application services."""

    def initialize(self) -> None:
        initialize_database()

    def load_active_student_biometrics(self) -> Tuple[List, List[str], List[int]]:
        return load_student_biometrics()

    def create_student(self, grado: int, letra: str, turno: str) -> int:
        return create_student(grado, letra, turno)

    def save_student_biometric(self, id_estudiante: int, encoding) -> None:
        save_student_biometric(id_estudiante, encoding)

    def log_student_access(self, id_estudiante: int, acceso_concedido: bool) -> None:
        log_access(id_estudiante, acceso_concedido, tipo_usuario="ESTUDIANTE")
