from dataclasses import dataclass
from typing import Optional

from src.application.registration_service import RegistrationService
from src.domain.ports import PklBiometricRepositoryPort


@dataclass
class RegistrationResult:
    success: bool
    message: str
    student_id: Optional[int] = None


class RegistrationUseCase:
    def __init__(
        self,
        registration_service: RegistrationService,
        pkl_repository: PklBiometricRepositoryPort,
    ) -> None:
        self.registration_service = registration_service
        self.pkl_repository = pkl_repository

    def initialize(self) -> None:
        self.registration_service.initialize()

    def register_from_detected_faces(self, grado: int, letra: str, turno: str, encodings) -> RegistrationResult:
        if len(encodings) == 0:
            return RegistrationResult(
                success=False,
                message="Error: No se detecto ningun rostro. Intenta de nuevo.",
            )

        if len(encodings) > 1:
            return RegistrationResult(
                success=False,
                message="Error: Se detectaron multiples rostros. Debe haber solo uno.",
            )

        encoding = encodings[0]
        student_id = self.registration_service.register_student_with_encoding(grado, letra, turno, encoding)
        self.pkl_repository.save_student_biometric(student_id, encoding)

        return RegistrationResult(
            success=True,
            student_id=student_id,
            message=f"Registro exitoso. Estudiante #{student_id} ({grado}{letra}-{turno}).",
        )
