"""
Módulo de servicio de autenticación facial
Contiene la lógica de negocio para verificación y gestión de acceso
"""
import pickle
import os
import time
from typing import List, Tuple, Optional, Dict

try:
    from src.application.auth_service import AuthService
    from src.infrastructure.camera.opencv_camera import open_camera
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
    from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame, find_first_match
    USE_ADVANCED = True
except ImportError:
    USE_ADVANCED = False


class FaceLoginService:
    """
    Servicio de autenticación facial.
    Maneja la lógica de verificación, carga de datos y registro de acceso.
    """
    
    def __init__(self):
        """Inicializa el servicio de login"""
        self.rostros_db: List = []
        self.nombres_db: List[str] = []
        self.ids_db: List[int] = []
        self.datos_estudiantes: Dict = {}
        self.ultima_bitacora: Dict[int, float] = {}
        self.cooldown_segundos = 3.0
        
        # Cargar datos iniciales
        self._load_recognition_data()
    
    def _load_recognition_data(self) -> None:
        """Carga los datos de reconocimiento facial desde la base de datos"""
        try:
            if USE_ADVANCED:
                auth_service = AuthService(SQLiteRepository())
                auth_service.initialize()
                self.rostros_db, self.nombres_db, self.ids_db = auth_service.load_known_students()
            
            # Fallback: usar archivos .pkl
            if not self.rostros_db:
                self._load_pkl_database()
        
        except Exception as e:
            print(f"Error cargando datos de reconocimiento: {e}")
    
    def _load_pkl_database(self) -> None:
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
    
    def get_users_count(self) -> int:
        """Retorna la cantidad de usuarios registrados"""
        return len(self.rostros_db)
    
    def has_users(self) -> bool:
        """Verifica si hay usuarios registrados"""
        return len(self.rostros_db) > 0
    
    def verify_face(self, encoding) -> Tuple[bool, Optional[Dict]]:
        """
        Verifica un encoding facial contra la base de datos.
        
        Args:
            encoding: Encoding del rostro a verificar
            
        Returns:
            Tuple (encontrado, datos_usuario)
            - encontrado (bool): Si se encontró coincidencia
            - datos_usuario (dict): Datos del usuario si se encontró
        """
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
    
    def log_access(self, user_id: int, success: bool) -> bool:
        """
        Registra un intento de acceso en la base de datos.
        Implementa cooldown para evitar duplicados.
        
        Args:
            user_id (int): ID del usuario
            success (bool): Si el acceso fue exitoso
            
        Returns:
            bool: Si se registró correctamente
        """
        if user_id <= 0:
            return False
        
        try:
            ahora = time.monotonic()
            ultimo = self.ultima_bitacora.get(user_id, 0.0)
            
            # Verificar cooldown
            if ahora - ultimo < self.cooldown_segundos:
                return False
            
            # Registrar acceso
            if USE_ADVANCED:
                auth = AuthService(SQLiteRepository())
                auth.log_access(user_id, success)
            
            self.ultima_bitacora[user_id] = ahora
            return True
        
        except Exception as e:
            print(f"Error registrando acceso: {e}")
            return False
    
    def detect_face_in_frame(self, frame) -> Tuple[list, list]:
        """
        Detecta rostros en un frame.
        
        Args:
            frame: Frame de OpenCV
            
        Returns:
            Tuple (face_locations, encodings)
        """
        try:
            if USE_ADVANCED:
                face_locations, encodings = detect_face_encodings_from_frame(frame, scale=0.25)
                return face_locations, encodings
            else:
                return [], []
        
        except Exception as e:
            print(f"Error detectando rostro: {e}")
            return [], []
    
    def get_database_status(self) -> Dict:
        """
        Retorna el estado de la base de datos de reconocimiento.
        
        Returns:
            Dict con información de estado
        """
        return {
            "users_count": self.get_users_count(),
            "has_users": self.has_users(),
            "last_access_attempts": len(self.ultima_bitacora)
        }
