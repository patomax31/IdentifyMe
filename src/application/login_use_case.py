from dataclasses import dataclass
from time import monotonic
from typing import Dict, List, Optional, Tuple

from src.application.auth_service import AuthService
from src.domain.ports import FaceMatcherPort, PklBiometricRepositoryPort


@dataclass
class LoginFrameResult:
    message: str
    color: Tuple[int, int, int]


class LoginUseCase:
    def __init__(
        self,
        auth_service: AuthService,
        matcher: FaceMatcherPort,
        pkl_repository: Optional[PklBiometricRepositoryPort] = None,
        tolerance: float = 0.5,
        cooldown_seconds: float = 8.0,
    ) -> None:
        self.auth_service = auth_service
        self.matcher = matcher
        self.pkl_repository = pkl_repository
        self.tolerance = tolerance
        self.cooldown_seconds = cooldown_seconds
        self._last_logged_by_student_id: Dict[int, float] = {}

    def initialize(self) -> None:
        self.auth_service.initialize()

    def load_known_students(self):
        known_encodings, known_labels, known_ids = self.auth_service.load_known_students()
        if known_encodings:
            return known_encodings, known_labels, known_ids

        if self.pkl_repository is None:
            return known_encodings, known_labels, known_ids

        pkl_encodings, pkl_labels, pkl_ids = self.pkl_repository.load_student_biometrics()
        if not pkl_ids:
            pkl_ids = [0] * len(pkl_labels)
        return pkl_encodings, pkl_labels, pkl_ids

    def process_frame(self, encodings, known_encodings: List, known_labels: List[str], known_ids: List[int]) -> LoginFrameResult:
        message = "ESPERANDO ROSTRO..."
        color = (255, 255, 255)

        for face_encoding in encodings:
            idx = self.matcher.find_first_match(known_encodings, face_encoding, tolerance=self.tolerance)
            if idx >= 0:
                student_label = known_labels[idx].upper()
                message = f"ACCESO CONCEDIDO: {student_label}"
                color = (0, 255, 0)
                self._log_access_with_cooldown(idx, known_ids)
            else:
                message = "ACCESO DENEGADO"
                color = (0, 0, 255)

        return LoginFrameResult(message=message, color=color)

    def _log_access_with_cooldown(self, idx: int, known_ids: List[int]) -> None:
        if idx >= len(known_ids):
            return

        student_id = known_ids[idx]
        if student_id <= 0:
            return

        now = monotonic()
        last = self._last_logged_by_student_id.get(student_id, 0.0)
        if now - last < self.cooldown_seconds:
            return

        self.auth_service.log_access(student_id, True)
        self._last_logged_by_student_id[student_id] = now
