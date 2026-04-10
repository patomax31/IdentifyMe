import cv2
import face_recognition
import pickle
import os
from database.sqlite_manager import initialize_database, create_student, save_student_biometric


def abrir_camara():
    # Perfil dual:
    # - WINDOWS_STABLE: evita bloqueos usando DirectShow.
    # - RASPBERRY_PI: prioriza V4L2 para camara local embebida.
    camera_index = int(os.getenv("CAMERA_INDEX", "0"))
    profile = os.getenv("CAMERA_PROFILE", "AUTO").strip().upper()
    if profile == "AUTO":
        profile = "WINDOWS_STABLE" if os.name == "nt" else "RASPBERRY_PI"

    if profile == "WINDOWS_STABLE":
        intentos = [
            (camera_index, cv2.CAP_DSHOW),
            (1 - camera_index, cv2.CAP_DSHOW),
        ]
    else:
        intentos = [
            (camera_index, cv2.CAP_V4L2),
            (1 - camera_index, cv2.CAP_V4L2),
            (camera_index, None),
        ]

    for indice, backend in intentos:
        cap = cv2.VideoCapture(indice) if backend is None else cv2.VideoCapture(indice, backend)
        if cap.isOpened():
            # Ajustes de captura para balancear consumo/rendimiento en embebido.
            width = int(os.getenv("CAMERA_WIDTH", "640"))
            height = int(os.getenv("CAMERA_HEIGHT", "480"))
            fps = int(os.getenv("CAMERA_FPS", "20"))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            cap.set(cv2.CAP_PROP_FPS, fps)
            return cap
        cap.release()

    return None


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
    initialize_database()

    # Crear carpeta de datos si no existe
    if not os.path.exists('data'):
        os.makedirs('data')

    grado, letra, turno = solicitar_datos_grupo()
    cap = abrir_camara()

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
            # Convertir a RGB para face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb_frame)
            
            if len(boxes) == 1:
                # Extraer encoding
                encoding = face_recognition.face_encodings(rgb_frame, boxes)[0]

                id_estudiante = create_student(grado, letra, turno)

                # Guardar en SQLite (fuente principal)
                save_student_biometric(id_estudiante, encoding)
                
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