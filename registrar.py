import cv2
import pickle
import os
from src.application.registration_service import RegistrationService
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import encode_single_face_from_frame


def solicitar_datos_grupo():
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

    return grado, letra, turno

def registrar_usuario():
    registration_service = RegistrationService(SQLiteRepository())
    registration_service.initialize()

    # Crear carpeta de datos si no existe
    if not os.path.exists('data'):
        os.makedirs('data')

    grado, letra, turno = solicitar_datos_grupo()
    cap = open_camera()

    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return

    print(f"Registrando estudiante de {grado}{letra}-{turno}. Presiona 'S' para capturar o 'Q' para salir.")

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
            encoding = encode_single_face_from_frame(frame)

            if encoding is not None:

                id_estudiante = registration_service.register_student_with_encoding(
                    grado,
                    letra,
                    turno,
                    encoding,
                )
                
                # Guardar respaldo en .pkl
                nombre_archivo = f"est_{id_estudiante}.pkl"
                with open(f"data/{nombre_archivo}", "wb") as f:
                    pickle.dump(encoding, f)
                
                print(f"Registro exitoso. Estudiante #{id_estudiante} ({grado}{letra}-{turno}).")
                break
            else:
                print("Error: Asegúrate de que solo haya UN rostro y esté bien iluminado.")

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    registrar_usuario()