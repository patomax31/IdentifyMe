import cv2
import face_recognition
import pickle
import os
from picamera2 import Picamera2
from database.sqlite_manager import initialize_database, create_student, save_student_biometric
from configBase import load_config


def abrir_camara(config):
    # Usar Picamera2 para Raspberry Pi
    try:
        picam2 = Picamera2()
        width = config["camera"]["width"]
        height = config["camera"]["height"]
        
        cam_config = picam2.create_preview_configuration(
            main={"format": 'XRGB8888', "size": (width, height)}
        )
        picam2.configure(cam_config)
        picam2.start()
        return picam2
    except Exception as e:
        print(f"Error al iniciar Picamera2: {e}")
        return None


def solicitar_datos_grupo():
    nombre = input("Nombre del estudiante: ").strip().upper()
    if not nombre or len(nombre) < 2:
        print("Dato inválido. El nombre debe tener al menos 2 caracteres.")
        return solicitar_datos_grupo()

    while True:
        grado_raw = input("Grado del estudiante (1-3): ").strip()
        if grado_raw in {"1", "2", "3"}:
            grado = int(grado_raw)
            break
        print("Dato inválido. El grado debe ser 1, 2 o 3.")

    while True:
        letra = input("Letra del grupo (A-Z): ").strip().upper()
        if len(letra) == 1 and letra.isalpha():
            break
        print("Dato inválido. Ingresa una sola letra (A-Z).")

    while True:
        turno_raw = input("Turno (M=MATUTINO / V=VESPERTINO): ").strip().upper()
        if turno_raw == "M":
            turno = "MATUTINO"
            break
        elif turno_raw == "V":
            turno = "VESPERTINO"
            break
        print("Dato inválido. Usa M para MATUTINO o V para VESPERTINO.")

    return nombre, grado, letra, turno

def registrar_usuario():
    # Cargar configuración desde configBase
    config = load_config()
    
    initialize_database()

    # Crear carpeta de datos si no existe
    if not os.path.exists('data'):
        os.makedirs('data')

    nombre, grado, letra, turno = solicitar_datos_grupo()
    cap = abrir_camara(config)

    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return

    print(f"Registrando a {nombre} ({grado}{letra}-{turno}). Presiona 'S' para capturar o 'Q' para salir.")

    # Configación del óvalo (desde configBase)
    oval_width_ratio = config["registro"]["oval_width_ratio"]
    oval_height_ratio = config["registro"]["oval_height_ratio"]
    line_thickness = config["registro"]["line_thickness"]

    while True:
        frame = cap.capture_array()
        if frame is None: break

        # Configuración del óvalo guía (desde config)
        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * oval_width_ratio), int(alto * oval_height_ratio))
        
        # Dibujar Interfaz (Óvalo y texto)
        cv2.ellipse(frame, centro, ejes, 0, 0, 360, (255, 255, 0), line_thickness)
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

                id_estudiante = create_student(nombre, grado, letra, turno)

                # Guardar en SQLite (fuente principal)
                save_student_biometric(id_estudiante, encoding)
                
                # Guardar respaldo en .pkl
                nombre_archivo = f"est_{id_estudiante}.pkl"
                with open(f"data/{nombre_archivo}", "wb") as f:
                    pickle.dump(encoding, f)
                
                print(f"[OK] Registro exitoso. {nombre} #{id_estudiante} ({grado}{letra}-{turno}).")
                break
            else:
                print("Error: Asegúrate de que solo haya UN rostro y esté bien iluminado.")

        if key == ord('q'):
            break

    cap.stop()

if __name__ == "__main__":
    registrar_usuario()