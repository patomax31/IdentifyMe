import cv2
from time import monotonic
from typing import Callable, Optional

from src.application.auth_service import AuthService
from src.application.login_use_case import LoginUseCase
from src.core.config import get_recognition_settings
from database.sqlite_manager import load_staff_biometrics, log_access
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame
from src.infrastructure.recognition.matcher_adapter import FaceMatcherAdapter

def _notify(state_callback: Optional[Callable[[str], None]], message: str) -> None:
    if state_callback is not None:
        state_callback(message)


def login(state_callback: Optional[Callable[[str], None]] = None):
    _notify(state_callback, "Inicializando login biometrico...")
    recognition_settings = get_recognition_settings()
    matcher = FaceMatcherAdapter()
    use_case = LoginUseCase(
        auth_service=AuthService(SQLiteRepository()),
        matcher=matcher,
        pkl_repository=PklRepository(),
        tolerance=recognition_settings.tolerance,
        cooldown_seconds=recognition_settings.access_cooldown_seconds,
    )
    use_case.initialize()
    rostros_personal, nombres_personal, ids_personal, _roles_personal = load_staff_biometrics()
    rostros_estudiantes, nombres_estudiantes, ids_estudiantes = use_case.load_known_students()

    if not rostros_personal and not rostros_estudiantes:
        message = "No hay biometria registrada. Ejecuta primero bootstrap_admin.py o registrar.py"
        print(message)
        _notify(state_callback, message)
        return

    cap = open_camera()
    last_logged_by_staff_id = {}

    if cap is None:
        message = "No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo."
        print(message)
        _notify(state_callback, message)
        return

    _notify(state_callback, "Login biometrico activo. Presiona 'Q' para cerrar.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Guía visual
        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4))

        _, encodings = detect_face_encodings_from_frame(frame, scale=recognition_settings.scale)

        message = "ESPERANDO ROSTRO..."
        color = (255, 255, 255)

        for face_encoding in encodings:
            idx_personal = matcher.find_first_match(
                rostros_personal,
                face_encoding,
                tolerance=recognition_settings.tolerance,
            )
            if idx_personal >= 0:
                personal_id = ids_personal[idx_personal]
                personal_label = nombres_personal[idx_personal].upper()
                message = f"ACCESO PERSONAL CONCEDIDO: {personal_label}"
                color = (0, 255, 0)

                now = monotonic()
                last = last_logged_by_staff_id.get(personal_id, 0.0)
                if now - last >= recognition_settings.access_cooldown_seconds:
                    log_access(personal_id, True, tipo_usuario="PERSONAL")
                    last_logged_by_staff_id[personal_id] = now
                break

            if rostros_estudiantes:
                result = use_case.process_frame(
                    [face_encoding],
                    rostros_estudiantes,
                    nombres_estudiantes,
                    ids_estudiantes,
                )
                message = result.message
                color = result.color
                if color == (0, 255, 0):
                    break
            else:
                message = "ACCESO DENEGADO"
                color = (0, 0, 255)

        # Dibujar Interfaz
        cv2.ellipse(frame, centro, ejes, 0, 0, 360, color, 2)
        cv2.rectangle(frame, (0, 0), (ancho, 40), (0,0,0), -1)
        cv2.putText(frame, message, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2)

        cv2.imshow("Login Biometrico", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    _notify(state_callback, "Login biometrico finalizado.")

if __name__ == "__main__":
    login()