import cv2
from typing import Callable, Optional

from src.application.registration_service import RegistrationService
from src.application.registration_use_case import RegistrationUseCase
from src.core.config import get_recognition_settings
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame


def solicitar_datos_estudiante_y_grupo():
    while True:
        nombre = input("Nombre del estudiante: ").strip()
        if nombre:
            break
        print("Dato invalido. El nombre es obligatorio.")

    while True:
        grado_raw = input("Grado del estudiante (1-3): ").strip()
        if grado_raw in {"1", "2", "3"}:
            grado = int(grado_raw)
            break
        print("Dato invalido. El grado debe ser 1, 2 o 3.")

    while True:
        letra = input("Letra del grupo (A-Z): ").strip().upper()
        if len(letra) == 1 and letra.isalpha():
            break
        print("Dato invalido. Ingresa una sola letra (A-Z).")

    while True:
        turno = input("Turno (MATUTINO/VESPERTINO): ").strip().upper()
        if turno in {"MATUTINO", "VESPERTINO"}:
            break
        print("Dato invalido. Usa MATUTINO o VESPERTINO.")

    return nombre, grado, letra, turno

def _notify(state_callback: Optional[Callable[[str], None]], message: str) -> None:
    if state_callback is not None:
        state_callback(message)


def registrar_usuario(state_callback: Optional[Callable[[str], None]] = None):
    _notify(state_callback, "Inicializando registro biometrico...")
    recognition_settings = get_recognition_settings()
    use_case = RegistrationUseCase(
        registration_service=RegistrationService(SQLiteRepository()),
        pkl_repository=PklRepository(),
    )
    use_case.initialize()

    nombre, grado, letra, turno = solicitar_datos_estudiante_y_grupo()
    cap = open_camera()

    if cap is None:
        message = "No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo."
        print(message)
        _notify(state_callback, message)
        return

    start_message = f"Registrando a {nombre} en {grado}{letra}-{turno}. Presiona 'S' para capturar o 'Q' para salir."
    print(start_message)
    _notify(state_callback, start_message)

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Configuración del óvalo guía
        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4)) # Proporción para el rostro
        
        # Dibujar Interfaz (Óvalo y texto)
        cv2.ellipse(frame, centro, ejes, 0, 0, 360, (255, 255, 0), 2)
        cv2.putText(frame, "Encuadra tu rostro aqui", (centro[0]-120, centro[1]-ejes[1]-20), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 0), 1)
        cv2.putText(frame, "Presiona 'S' para Guardar", (10, alto - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Registro Biometrico", frame)

        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            _, encodings = detect_face_encodings_from_frame(frame, scale=recognition_settings.scale)
            result = use_case.register_from_detected_faces(nombre, grado, letra, turno, encodings)

            if result.success:
                print(result.message)
                _notify(state_callback, result.message)
                break

            print(result.message)
            _notify(state_callback, result.message)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    _notify(state_callback, "Registro biometrico finalizado.")

if __name__ == "__main__":
    registrar_usuario()