import cv2
from time import monotonic

from database.sqlite_manager import load_staff_biometrics, log_access
from src.application.auth_service import AuthService
from src.application.login_use_case import LoginUseCase
from src.core.config import get_recognition_settings
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame
from src.infrastructure.recognition.matcher_adapter import FaceMatcherAdapter


def login():
    print("Iniciando login facial...")

    settings = get_recognition_settings()

    matcher = FaceMatcherAdapter()
    use_case = LoginUseCase(
        auth_service=AuthService(SQLiteRepository()),
        matcher=matcher,
        pkl_repository=PklRepository(),
        tolerance=settings.tolerance,
        cooldown_seconds=settings.access_cooldown_seconds,
    )

    use_case.initialize()

    rostros_personal, nombres_personal, ids_personal, _ = load_staff_biometrics()
    rostros_estudiantes, nombres_estudiantes, ids_estudiantes = use_case.load_known_students()

    if not rostros_personal and not rostros_estudiantes:
        print("No hay biometría registrada.")
        return

    cap = open_camera()
    if cap is None:
        print("No se pudo abrir la cámara.")
        return

    last_logged = {}

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            _, encodings = detect_face_encodings_from_frame(frame, scale=settings.scale)

            message = "Esperando rostro..."
            color = (255, 255, 255)

            for encoding in encodings:
                idx = matcher.find_first_match(
                    rostros_personal,
                    encoding,
                    tolerance=settings.tolerance,
                )

                if idx >= 0:
                    user_id = ids_personal[idx]
                    nombre = nombres_personal[idx]

                    message = f"Acceso concedido: {nombre}"
                    color = (0, 255, 0)

                    now = monotonic()
                    if now - last_logged.get(user_id, 0) > settings.access_cooldown_seconds:
                        log_access(user_id, True, tipo_usuario="PERSONAL")
                        last_logged[user_id] = now

                    break

                if rostros_estudiantes:
                    result = use_case.process_frame(
                        [encoding],
                        rostros_estudiantes,
                        nombres_estudiantes,
                        ids_estudiantes,
                    )
                    message = result.message
                    color = result.color

            cv2.putText(frame, message, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            cv2.imshow("Login Facial", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    login()