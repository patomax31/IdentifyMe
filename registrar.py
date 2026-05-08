import cv2

from src.application.registration_service import RegistrationService
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame
from src.core.config import get_recognition_settings


def registrar_usuario():
    print("=== REGISTRO DE USUARIO ===")

    nombre = input("Nombre completo: ").strip()
    if not nombre:
        print("Nombre inválido")
        return

    grado = input("Grado (1-3): ").strip()
    letra = input("Grupo (A-Z): ").strip().upper()
    turno = input("Turno (MATUTINO/VESPERTINO): ").strip().upper()

    settings = get_recognition_settings()

    service = RegistrationService(SQLiteRepository())
    service.initialize()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    print("\nColoca tu rostro y presiona 'S' para capturar")
    print("Presiona 'Q' para cancelar")

    encoding_capturado = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.putText(frame, "Presiona S para capturar",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2)

        cv2.imshow("Registro Facial", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            _, encodings = detect_face_encodings_from_frame(
                frame,
                scale=settings.scale
            )

            if len(encodings) != 1:
                print("Debe haber exactamente un rostro")
                continue

            encoding_capturado = encodings[0]
            break

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if encoding_capturado is None:
        print("Registro cancelado")
        return

    try:
        student_id = service.register_student_with_encoding(
            int(grado),
            letra,
            turno,
            encoding_capturado
        )

        print(f"\nUsuario registrado con éxito")
        print(f"ID: {student_id}")
        print(f"Nombre: {nombre}")

    except Exception as e:
        print(f"Error al registrar: {e}")


if __name__ == "__main__":
    registrar_usuario()