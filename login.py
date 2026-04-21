import cv2
import pickle
import os
import time
from src.application.auth_service import AuthService
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame, find_first_match


def cargar_base_datos():
    rostros = []
    nombres = []
    if not os.path.isdir("data"):
        return rostros, nombres

    for archivo in os.listdir("data"):
        if archivo.endswith(".pkl"):
            with open(f"data/{archivo}", "rb") as f:
                rostros.append(pickle.load(f))
                nombres.append(archivo.replace(".pkl", ""))
    return rostros, nombres

def login():
    auth_service = AuthService(SQLiteRepository())
    auth_service.initialize()
    rostros_db, nombres_db, ids_db = auth_service.load_known_students()

    # Compatibilidad: usar archivos .pkl si aun no hay biometria en SQLite.
    if not rostros_db:
        rostros_db, nombres_db = cargar_base_datos()
        ids_db = [0] * len(nombres_db)

    if not rostros_db:
        print("No hay biometria registrada. Ejecuta primero registrar.py")
        return

    cap = open_camera()

    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return

    # Evita registrar el mismo acceso en cada frame mientras la persona sigue frente a camara.
    ultima_bitacora = {}
    cooldown_segundos = 8.0

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Guía visual
        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4))
        
        _, encodings = detect_face_encodings_from_frame(frame, scale=0.25)

        color_oval = (255, 255, 255) # Blanco por defecto
        mensaje = "ESPERANDO ROSTRO..."

        for face_encoding in encodings:
            # Comparar con la base de datos
            idx = find_first_match(rostros_db, face_encoding, tolerance=0.5)

            if idx >= 0:
                nombre_usuario = nombres_db[idx].upper()
                mensaje = f"ACCESO CONCEDIDO: {nombre_usuario}"
                color_oval = (0, 255, 0) # Verde
                if idx < len(ids_db) and ids_db[idx] > 0:
                    id_estudiante = ids_db[idx]
                    ahora = time.monotonic()
                    ultimo = ultima_bitacora.get(id_estudiante, 0.0)
                    if ahora - ultimo >= cooldown_segundos:
                        auth_service.log_access(id_estudiante, True)
                        ultima_bitacora[id_estudiante] = ahora
            else:
                mensaje = "ACCESO DENEGADO"
                color_oval = (0, 0, 255) # Rojo

        # Dibujar Interfaz
        cv2.ellipse(frame, centro, ejes, 0, 0, 360, color_oval, 2)
        cv2.rectangle(frame, (0, 0), (ancho, 40), (0,0,0), -1)
        cv2.putText(frame, mensaje, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, color_oval, 2)

        cv2.imshow("Login Biometrico", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    login()