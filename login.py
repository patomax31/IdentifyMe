import cv2
import face_recognition
import pickle
import os
import time
from picamera2 import Picamera2
from database.sqlite_manager import initialize_database, load_student_biometrics, log_access

def abrir_camara():
    # Usar Picamera2 para Raspberry Pi
    try:
        picam2 = Picamera2()
        width = int(os.getenv("CAMERA_WIDTH", "480"))
        height = int(os.getenv("CAMERA_HEIGHT", "800"))
        
        config = picam2.create_preview_configuration(
            main={"format": 'XRGB8888', "size": (width, height)}
        )
        picam2.configure(config)
        picam2.start()
        return picam2
    except Exception as e:
        print(f"Error al iniciar Picamera2: {e}")
        return None

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
    initialize_database()
    rostros_db, nombres_db, ids_db = load_student_biometrics()

    # Compatibilidad: usar archivos .pkl si aun no hay biometria en SQLite.
    if not rostros_db:
        rostros_db, nombres_db = cargar_base_datos()
        ids_db = [0] * len(nombres_db)

    if not rostros_db:
        print("No hay biometria registrada. Ejecuta primero registrar.py")
        return

    cap = abrir_camara()

    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return

    # Evita registrar el mismo acceso en cada frame
    ultima_bitacora = {}
    cooldown_segundos = 8.0
    
    # ⚡ OPTIMIZACIONES DE RENDIMIENTO
    frame_count = 0
    process_every_n_frames = 3  # Procesar solo cada 3 frames (reduce lag)
    consecutive_confirmed = 0
    frames_to_confirm = 2  # Necesita 2 frames consecutivos para confirmar
    last_recognized_idx = -1
    scan_state = "waiting"  # Estados: waiting, scanning, recognized, denied

    while True:
        frame = cap.capture_array()
        if frame is None: 
            break

        frame_count += 1
        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4))
        
        # Variables por defecto
        color_mensaje = (255, 255, 255)  # Blanco
        mensaje = "ESPERANDO ROSTRO..."
        rostros_detectados = []
        
        # 🔍 SOLO PROCESAR CADA N FRAMES para optimización
        if frame_count % process_every_n_frames == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            boxes = face_recognition.face_locations(rgb_small)
            encodings = face_recognition.face_encodings(rgb_small, boxes)
            
            if len(boxes) > 0:
                # Hay rostros detectados
                scan_state = "scanning"
                
                for i, face_encoding in enumerate(encodings):
                    # Escalar bounding box de vuelta al tamaño original
                    top, right, bottom, left = boxes[i]
                    top, right, bottom, left = top*4, right*4, bottom*4, left*4
                    rostros_detectados.append((top, right, bottom, left))
                    
                    # Comparar con base de datos
                    matches = face_recognition.compare_faces(rostros_db, face_encoding, tolerance=0.5)
                    
                    if True in matches:
                        idx = matches.index(True)
                        consecutive_confirmed += 1
                        last_recognized_idx = idx
                        
                        # Si alcanza confirmación
                        if consecutive_confirmed >= frames_to_confirm:
                            scan_state = "recognized"
                            nombre_usuario = nombres_db[idx].upper()
                            mensaje = f"✓ ACCESO CONCEDIDO: {nombre_usuario}"
                            color_mensaje = (0, 255, 0)  # Verde
                            
                            if idx < len(ids_db) and ids_db[idx] > 0:
                                id_estudiante = ids_db[idx]
                                ahora = time.monotonic()
                                ultimo = ultima_bitacora.get(id_estudiante, 0.0)
                                if ahora - ultimo >= cooldown_segundos:
                                    log_access(id_estudiante, True, tipo_usuario="ESTUDIANTE")
                                    ultima_bitacora[id_estudiante] = ahora
                    else:
                        # Rostro desconocido
                        scan_state = "denied"
                        mensaje = "✗ ACCESO DENEGADO"
                        color_mensaje = (0, 0, 255)  # Rojo
                        consecutive_confirmed = 0
            else:
                # No hay rostros en este frame
                scan_state = "waiting"
                mensaje = "ESPERANDO ROSTRO..."
                consecutive_confirmed = 0
                color_mensaje = (255, 255, 255)  # Blanco
        
        # 🎨 DIBUJAR BOUNDING BOXES alrededor de rostros detectados
        if len(rostros_detectados) > 0:
            if scan_state == "scanning":
                # Amarillo: Escaneando
                estado_color = (0, 255, 255)
                for (top, right, bottom, left) in rostros_detectados:
                    cv2.rectangle(frame, (left, top), (right, bottom), estado_color, 3)
                    cv2.putText(frame, "ESCANNEANDO - NO MOVERSE", (left, top-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, estado_color, 2)
            
            elif scan_state == "recognized":
                # Verde: Acceso concedido
                estado_color = (0, 255, 0)
                for (top, right, bottom, left) in rostros_detectados:
                    cv2.rectangle(frame, (left, top), (right, bottom), estado_color, 3)
                    cv2.putText(frame, "ESTUDIANTE VERIFICADO", (left, top-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, estado_color, 2)
            
            elif scan_state == "denied":
                # Rojo: Acceso denegado
                estado_color = (0, 0, 255)
                for (top, right, bottom, left) in rostros_detectados:
                    cv2.rectangle(frame, (left, top), (right, bottom), estado_color, 3)
                    cv2.putText(frame, "ROSTRO DESCONOCIDO", (left, top-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, estado_color, 2)
            
            else:  # waiting - Rostro detectado sin identificación
                # Gris/Negro: Detectado pero sin identificación
                estado_color = (100, 100, 100)
                for (top, right, bottom, left) in rostros_detectados:
                    cv2.rectangle(frame, (left, top), (right, bottom), estado_color, 2)
                    cv2.putText(frame, "DETECTADO", (left, top-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, estado_color, 1)
        
        # 🖼️ Dibujar interfaz principal
        cv2.ellipse(frame, centro, ejes, 0, 0, 360, color_mensaje, 2)
        
        # Barra de estado arriba
        cv2.rectangle(frame, (0, 0), (ancho, 60), (0, 0, 0), -1)
        cv2.putText(frame, mensaje, (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.9, color_mensaje, 2)
        
        # Información del estado (abajo)
        estado_texto = f"Estado: {scan_state.upper()} | FPS: {frame_count//3} | Presiona Q para salir"
        cv2.putText(frame, estado_texto, (10, alto - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        cv2.imshow("Login Biometrico", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    login()