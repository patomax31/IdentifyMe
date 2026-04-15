from typing import List, Protocol, Tuple


class AuthRepositoryPort(Protocol):
    def initialize(self) -> None:
        ...

    def load_active_student_biometrics(self) -> Tuple[List, List[str], List[int]]:
        ...

    def log_student_access(self, id_estudiante: int, acceso_concedido: bool) -> None:
        ...


class RegistrationRepositoryPort(Protocol):
    def initialize(self) -> None:
        ...

    def create_student(self, grado: int, letra: str, turno: str) -> int:
        ...

    def save_student_biometric(self, id_estudiante: int, encoding) -> None:
        ...
