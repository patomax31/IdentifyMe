<<<<<<< HEAD
import cv2
import pickle
import os
import time
from src.application.auth_service import AuthService
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame, find_first_match


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

def dibujar_cuadro_amigable(frame, top, right, bottom, left, color, grosor=3):
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
    auth_service = AuthService(SQLiteRepository())
    auth_service.initialize()
    rostros_db, nombres_db, ids_db = auth_service.load_known_students()

    # Compatibilidad: usar archivos .pkl si aun no hay biometria en SQLite.
    if not rostros_db:
        rostros_db, nombres_db = cargar_base_datos()
        ids_db = [0] * len(nombres_db)
=======
"""
Módulo de lógica de autenticación facial - LÓGICA PURA

Contiene solo la lógica de negocio para:
- Carga de datos biométricos
- Verificación de rostros
- Registro de acceso
- Detección facial
>>>>>>> 2e2d95e (UI de la cargainicial de dependencias test_setup.py)

La interfaz gráfica está en login_ui.py
"""
import pickle
import os
import time

# Importaciones del proyecto
try:
    from src.application.auth_service import AuthService
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
    from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame, find_first_match
    USE_ADVANCED = True
except ImportError:
    USE_ADVANCED = False


<<<<<<< HEAD
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
=======
# ═══════════════════════════════════════════════════════════════════════════════
# SERVICIO DE AUTENTICACIÓN FACIAL
# ═══════════════════════════════════════════════════════════════════════════════
class FaceLoginService:
    """
    Servicio de autenticación facial - LÓGICA DE NEGOCIO PURA
    
    Responsabilidades:
    - Cargar datos biométricos
    - Verificar rostros contra la base de datos
    - Registrar acceso
    - Detectar rostros en frames
    """
    
    def __init__(self):
        """Inicializa el servicio de login"""
        self.rostros_db = []
        self.nombres_db = []
        self.ids_db = []
        self.datos_estudiantes = {}
        self.ultima_bitacora = {}
        self.cooldown_segundos = 3.0
        self._load_recognition_data()
    
    def _load_recognition_data(self):
        """Carga los datos de reconocimiento facial desde la base de datos"""
        try:
            if USE_ADVANCED:
                auth_service = AuthService(SQLiteRepository())
                auth_service.initialize()
                self.rostros_db, self.nombres_db, self.ids_db = auth_service.load_known_students()
            
            if not self.rostros_db:
                self._load_pkl_database()
        except Exception as e:
            print(f"Error cargando datos de reconocimiento: {e}")
    
    def _load_pkl_database(self):
        """Carga base de datos desde archivos .pkl como fallback"""
        if not os.path.isdir("data"):
            return
        
        for archivo in sorted(os.listdir("data")):
            if archivo.endswith(".pkl"):
                try:
                    with open(f"data/{archivo}", "rb") as f:
                        self.rostros_db.append(pickle.load(f))
                        nombre = archivo.replace(".pkl", "")
                        self.nombres_db.append(nombre)
                        self.ids_db.append(0)
                except Exception as e:
                    print(f"Error cargando {archivo}: {e}")
    
    def get_users_count(self):
        """Retorna la cantidad de usuarios registrados"""
        return len(self.rostros_db)
    
    def has_users(self):
        """Verifica si hay usuarios registrados"""
        return len(self.rostros_db) > 0
    
    def verify_face(self, encoding):
        """Verifica un encoding facial contra la base de datos"""
        try:
            if USE_ADVANCED:
                idx = find_first_match(self.rostros_db, encoding, tolerance=0.5)
            else:
                idx = -1
            
            if idx >= 0 and idx < len(self.nombres_db):
                name = self.nombres_db[idx]
                user_id = self.ids_db[idx] if idx < len(self.ids_db) else 0
                
                user_data = {
                    "nombre": name,
                    "id": user_id,
                    "salon": "---",
                    "edad": "---"
                }
                return True, user_data
            
            return False, None
        except Exception as e:
            print(f"Error verificando rostro: {e}")
            return False, None
    
    def log_access(self, user_id, success):
        """Registra un intento de acceso en la base de datos"""
        if user_id <= 0:
            return False
        
        try:
            ahora = time.monotonic()
            ultimo = self.ultima_bitacora.get(user_id, 0.0)
            
            if ahora - ultimo < self.cooldown_segundos:
                return False
            
            if USE_ADVANCED:
                auth = AuthService(SQLiteRepository())
                auth.log_access(user_id, success)
            
            self.ultima_bitacora[user_id] = ahora
            return True
        except Exception as e:
            print(f"Error registrando acceso: {e}")
            return False
    
    def detect_face_in_frame(self, frame):
        """Detecta rostros en un frame"""
        try:
            if USE_ADVANCED:
                face_locations, encodings = detect_face_encodings_from_frame(frame, scale=0.25)
                return face_locations, encodings
            else:
                return [], []
        except Exception as e:
            print(f"Error detectando rostro: {e}")
            return [], []

>>>>>>> 2e2d95e (UI de la cargainicial de dependencias test_setup.py)

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTACIÓN DE UI Y PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════
def login(parent=None):
    """
    Inicia la interfaz de login con reconocimiento facial.
    
    The UI logic is in login_ui.py, this module only has the business logic.
    
    Args:
        parent: Widget padre Tkinter (opcional)
    """
    from login_ui import FaceLoginUI
    
    # Crear servicio con lógica pura
    service = FaceLoginService()
    
    # Crear UI y pasar el servicio
    ui = FaceLoginUI(login_service=service, parent=parent)
    
    # Iniciar aplicación
    ui.run()


if __name__ == "__main__":
    login()
