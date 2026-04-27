import cv2
import face_recognition
import pickle
import os
import time
from database.sqlite_manager import initialize_database, load_student_biometrics, log_access


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
        
        # Procesar frame (escala 1/4 para velocidad)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, boxes)

        color_oval = (255, 255, 255) # Blanco por defecto
        mensaje = "ESPERANDO ROSTRO..."

        for face_encoding in encodings:
            # Comparar con la base de datos
            matches = face_recognition.compare_faces(rostros_db, face_encoding, tolerance=0.5)
            
            if True in matches:
                idx = matches.index(True)
                nombre_usuario = nombres_db[idx].upper()
                mensaje = f"ACCESO CONCEDIDO: {nombre_usuario}"
                color_oval = (0, 255, 0) # Verde
                if idx < len(ids_db) and ids_db[idx] > 0:
                    id_estudiante = ids_db[idx]
                    ahora = time.monotonic()
                    ultimo = ultima_bitacora.get(id_estudiante, 0.0)
                    if ahora - ultimo >= cooldown_segundos:
                        log_access(id_estudiante, True, tipo_usuario="ESTUDIANTE")
                        ultima_bitacora[id_estudiante] = ahora
            else:
                mensaje = "ACCESO DENEGADO"
                color_oval = (0, 0, 255) # Rojo

        # Dibujar Interfaz
        cv2.ellipse(frame, centro, ejes, 0, 0, 360, color_oval, 2)
        cv2.rectangle(frame, (0, 0), (ancho, 40), (0,0,0), -1)
        cv2.putText(frame, mensaje, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, color_oval, 2)
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