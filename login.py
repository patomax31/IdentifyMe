import cv2
import face_recognition
import pickle
import os
import time
from picamera2 import Picamera2
from database.sqlite_manager import initialize_database, load_student_biometrics, log_access, get_student_info
from configBase import load_config

def abrir_camara(config):
    """Inicializa la cámara de Raspberry Pi"""
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

def cargar_base_datos():
    """Carga biometría de archivos .pkl como respaldo"""
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

def dibujar_cuadro_amigable(frame, top, right, bottom, left, color, grosor):
    """Dibuja un cuadro redondeado amigable sin parpadeos"""
    # Cuadro principal
    cv2.rectangle(frame, (left, top), (right, bottom), color, grosor)
    
    # Puntos de énfasis en esquinas
    radio = 12
    cv2.circle(frame, (left, top), radio, color, -1)
    cv2.circle(frame, (right, top), radio, color, -1)
    cv2.circle(frame, (left, bottom), radio, color, -1)
    cv2.circle(frame, (right, bottom), radio, color, -1)

def dibujar_barra_estado(frame, mensaje, color, ancho_frame):
    """Dibuja barra de estado superior"""
    alto_barra = 80
    cv2.rectangle(frame, (0, 0), (ancho_frame, alto_barra), (0, 0, 0), -1)
    cv2.putText(frame, mensaje, (30, 55), cv2.FONT_HERSHEY_DUPLEX, 1.3, color, 2)

def dibujar_datos_estudiante(frame, nombre, grado, letra, turno, id_estudiante, alto_frame, ancho_frame):
    """Muestra datos del estudiante con fondo semi-transparente"""
    overlay = frame.copy()
    alto_box = 150
    y_start = alto_frame // 2 - alto_box // 2
    
    cv2.rectangle(overlay, (40, y_start), (ancho_frame - 40, y_start + alto_box), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    
    # Textos con datos
    y_offset = y_start + 35
    cv2.putText(frame, f"NOMBRE: {nombre}", (60, y_offset), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 0), 2)
    cv2.putText(frame, f"GRADO: {grado}{letra}", (60, y_offset + 40), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 0), 2)
    cv2.putText(frame, f"TURNO: {turno}", (60, y_offset + 80), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 0), 2)
    cv2.putText(frame, f"ID: #{id_estudiante}", (60, y_offset + 80), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 0), 2)

def login():
    # Cargar configuración desde configBase
    config = load_config()
    
    initialize_database()
    rostros_db, nombres_db, ids_db = load_student_biometrics()

    if not rostros_db:
        rostros_db, nombres_db = cargar_base_datos()
        ids_db = [0] * len(nombres_db)

    if not rostros_db:
        print("No hay biometria registrada. Ejecuta primero registrar.py")
        return

    cap = abrir_camara(config)

    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return

    # 🔧 CONFIGURACIÓN DE ESTADO (desde configBase)
    ultima_bitacora = {}
    cooldown_segundos = config["login"]["cooldown_seconds"]
    scanning_time_seconds = config["login"]["scanning_time_seconds"]
    state_display_seconds = config["login"]["state_display_seconds"]
    
    frame_count = 0
    process_every_n_frames = config["login"]["process_every_n_frames"]
    consecutive_confirmed = 0
    frames_to_confirm = config["login"]["frames_to_confirm"]
    tolerance = config["login"]["tolerance"]
    line_thickness = config["ui"]["line_thickness"]
    
    # Estados: esperando, detectado, escaneando, verificado, rechazado
    estado_actual = "esperando"
    tiempo_cambio_estado = time.time()
    
    estudiante_confirmado_id = None
    estudiante_confirmado_data = None

    while True:
        frame = cap.capture_array()
        if frame is None: 
            break

        frame_count += 1
        alto, ancho, _ = frame.shape
        
        color_cuadro = (100, 100, 100)  # Gris por defecto
        color_mensaje = (255, 255, 255)  # Blanco
        mensaje = "ESPERANDO ROSTRO..."
        rostros_detectados = []
        
        # 🔍 PROCESAR CADA N FRAMES
        if frame_count % process_every_n_frames == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            boxes = face_recognition.face_locations(rgb_small)
            encodings = face_recognition.face_encodings(rgb_small, boxes)
            
            if len(boxes) > 0 and len(encodings) > 0:
                for i, face_encoding in enumerate(encodings):
                    top, right, bottom, left = boxes[i]
                    top, right, bottom, left = top*4, right*4, bottom*4, left*4
                    rostros_detectados.append((top, right, bottom, left))
                    
                    # Comparar con BD
                    matches = face_recognition.compare_faces(rostros_db, face_encoding, tolerance=0.5)
                    
                    if True in matches:
                        idx = matches.index(True)
                        consecutive_confirmed += 1
                        
                        if consecutive_confirmed >= frames_to_confirm and estado_actual != "verificado":
                            estado_actual = "verificado"
                            tiempo_cambio_estado = time.time()
                            estudiante_confirmado_id = ids_db[idx]
                            estudiante_confirmado_data = get_student_info(estudiante_confirmado_id)
                            
                            if estudiante_confirmado_id > 0:
                                ahora = time.monotonic()
                                ultimo = ultima_bitacora.get(estudiante_confirmado_id, 0.0)
                                if ahora - ultimo >= cooldown_segundos:
                                    log_access(estudiante_confirmado_id, True, tipo_usuario="ESTUDIANTE")
                                    ultima_bitacora[estudiante_confirmado_id] = ahora
                    else:
                        if estado_actual not in ["rechazado", "verificado"]:
                            estado_actual = "rechazado"
                            tiempo_cambio_estado = time.time()
                        consecutive_confirmed = 0
            else:
                if estado_actual == "detectado" or estado_actual == "escaneando":
                    estado_actual = "esperando"
                    tiempo_cambio_estado = time.time()
                consecutive_confirmed = 0
        
        # ⏱️ LÓGICA DE TRANSICIONES SUAVE
        tiempo_en_estado = time.time() - tiempo_cambio_estado
        
        if estado_actual == "esperando":
            mensaje = "ESPERANDO ROSTRO..."
            color_mensaje = (255, 255, 255)
            if len(rostros_detectados) > 0 and tiempo_en_estado > 0.1:
                estado_actual = "detectado"
                tiempo_cambio_estado = time.time()
        
        elif estado_actual == "detectado":
            if tiempo_en_estado > 1.2:  # Espera suave
                estado_actual = "escaneando"
                tiempo_cambio_estado = time.time()
            color_mensaje = (0, 255, 255)
            color_cuadro = (0, 255, 255)
            
            # Si pasó el tiempo de escaneo, reintentar
            if tiempo_en_estado > scanning_time_seconds:
                estado_actual = "esperando"
                tiempo_cambio_estado = time.time()
                consecutive_confirmed = 0
            color_mensaje = (100, 100, 100)
            color_cuadro = (100, 100, 100)
        
        elif estado_actual == "escaneando":
            mensaje = "ESCANEANDO - NO MOVERSE"
            color_mensaje = (0, 255, 255)
            color_cuadro = (0, 255, 255)
        
        elif estado_actual == "verificado":
            mensaje = "ACCESO CONCEDIDO ✓ - Q: Salir | R: Reintentar"
            color_mensaje = (0, 255, 0)
            color_cuadro = (0, 255, 0)
            
            if estudiante_confirmado_data and rostros_detectados:
                id_est, nombre, grado, letra, turno = estudiante_confirmado_data
                dibujar_datos_estudiante(frame, nombre, grado, letra, turno, id_est, alto, ancho)
        
        elif estado_actual == "rechazado":
            if tiempo_en_estado > 2.0:
                estado_actual = "esperando"
                tiempo_cambio_estado = time.time()
                consecutive_confirmed = 0
            mensaje = "ROSTRO NO RECONOCIDO - R: REINTENTAR"
            color_mensaje = (0, 0, 255)
            color_cuadro = (0, 0, 255)
        
        # 📦 DIBUJAR CUADROS SIN PARPADEO
        if len(rostros_detectados) > 0:
            for (top, right, bottom, left) in rostros_detectados:
                dibujar_cuadro_amigable(frame, top, right, bottom, left, color_cuadro, grosor=3)
        
        # 📝 BARRA DE ESTADO
        dibujar_barra_estado(frame, mensaje, color_mensaje, ancho)
        
        # 📌 INSTRUCCIONES
        instrucciones = "Q: Salir | R: Reintentar"
        cv2.putText(frame, instrucciones, (20, alto - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

        cv2.imshow("Login Biometrico", frame)

        # ⌨️ CONTROL DE TECLADO
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            estado_actual = "esperando"
            tiempo_cambio_estado = time.time()
            consecutive_confirmed = 0
            estudiante_confirmado_id = None
            estudiante_confirmado_data = None

    cap.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    login()
