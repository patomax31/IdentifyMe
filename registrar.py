import cv2
import face_recognition
import pickle
import os
from database.sqlite_manager import initialize_database, save_user_biometric


def abrir_camara():
    # En Windows, CAP_DSHOW suele ser mas estable que MSMF con algunas webcams.
    intentos = [
        (0, cv2.CAP_DSHOW),
        (1, cv2.CAP_DSHOW),
        (0, cv2.CAP_MSMF),
        (1, cv2.CAP_MSMF),
        (0, None),
        (1, None),
    ]

    for indice, backend in intentos:
        cap = cv2.VideoCapture(indice) if backend is None else cv2.VideoCapture(indice, backend)
        if cap.isOpened():
            return cap
        cap.release()

    return None

def registrar_usuario():
    initialize_database()

    # Crear carpeta de datos si no existe
    if not os.path.exists('data'):
        os.makedirs('data')

    nombre = input("Introduce el nombre del usuario: ").lower()
    cap = abrir_camara()

    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return

    print(f"Registrando a {nombre}. Presiona 'S' para capturar o 'Q' para salir.")

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

                # Guardar en SQLite (fuente principal)
                save_user_biometric(nombre, encoding)
                
                # Guardar respaldo en .pkl
                with open(f"data/{nombre}.pkl", "wb") as f:
                    pickle.dump(encoding, f)
                
                print(f"¡Éxito! Usuario '{nombre}' registrado.")
                break
            else:
                print("Error: Asegúrate de que solo haya UN rostro y esté bien iluminado.")

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    registrar_usuario()