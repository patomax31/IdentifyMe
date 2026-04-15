import cv2
from src.application.auth_service import AuthService
from src.application.login_use_case import LoginUseCase
from src.core.config import get_recognition_settings
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame
from src.infrastructure.recognition.matcher_adapter import FaceMatcherAdapter

def login():
    recognition_settings = get_recognition_settings()
    use_case = LoginUseCase(
        auth_service=AuthService(SQLiteRepository()),
        matcher=FaceMatcherAdapter(),
        pkl_repository=PklRepository(),
        tolerance=recognition_settings.tolerance,
        cooldown_seconds=recognition_settings.access_cooldown_seconds,
    )
    use_case.initialize()
    rostros_db, nombres_db, ids_db = use_case.load_known_students()

    if not rostros_db:
        print("No hay biometria registrada. Ejecuta primero registrar.py")
        return

    cap = open_camera()

    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Guía visual
        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4))
        
        _, encodings = detect_face_encodings_from_frame(frame, scale=recognition_settings.scale)
        result = use_case.process_frame(encodings, rostros_db, nombres_db, ids_db)

        # Dibujar Interfaz
        cv2.ellipse(frame, centro, ejes, 0, 0, 360, result.color, 2)
        cv2.rectangle(frame, (0, 0), (ancho, 40), (0,0,0), -1)
        cv2.putText(frame, result.message, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, result.color, 2)

        cv2.imshow("Login Biometrico", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    login()