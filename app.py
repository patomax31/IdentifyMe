#!/usr/bin/env python3
"""
Sistema de Acceso Facial Identifyme - Ventana única unificada
Todos los componentes (menú, login, registro) en una sola ventana
"""

import cv2
import pickle
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import numpy as np

# Intentar importar módulos avanzados
try:
    import face_recognition
    USE_FACE_RECOGNITION = True
except ImportError:
    USE_FACE_RECOGNITION = False

try:
    from src.application.auth_service import AuthService
    from src.infrastructure.camera.opencv_camera import open_camera
    from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
    from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame, find_first_match
    USE_ADVANCED = True
except ImportError:
    USE_ADVANCED = False


# ═══════════════════════════════════════════════════════════════════════════════
# PALETA DE COLORES
# ═══════════════════════════════════════════════════════════════════════════════
COLOR_PRIMARY = "#008f39"      # Verde oscuro
COLOR_SECONDARY = "#48a259"    # Verde medio
COLOR_TERTIARY = "#70b578"     # Verde claro
COLOR_ACCENT = "#95c799"       # Verde muy claro
COLOR_LIGHT = "#b8daba"        # Gris verdoso claro
COLOR_LIGHTER = "#dbeddc"      # Gris verdoso muy claro
COLOR_WHITE = "#ffffff"        # Blanco
COLOR_DARKER = "#1a2741"       # Azul oscuro

COLOR_RED = "#ef4444"
COLOR_ORANGE = "#f97316"

BG_DARK = "#0f172a"
BG_CARD = "#1e293b"


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADOS DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
class UIState:
    """Estados de la interfaz"""
    IDLE = "idle"
    WAITING = "waiting"
    DETECTING = "detecting"
    VERIFYING = "verifying"
    POSITIONING = "positioning"
    GRANTED = "granted"
    DENIED = "denied"
    RESTRICTED = "restricted"
    ERROR = "error"


# ═══════════════════════════════════════════════════════════════════════════════
# APLICACIÓN PRINCIPAL - VENTANA ÚNICA
# ═══════════════════════════════════════════════════════════════════════════════
class MainApplication:
    """Aplicación unificada con una sola ventana y múltiples vistas"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Sistema de Acceso Facial - Identifyme")
        self.root.geometry("600x1024")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        
        # Centrar ventana
        self.root.update_idletasks()
        ancho = self.root.winfo_width()
        alto = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.root.winfo_screenheight() // 2) - (alto // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Variables compartidas
        self.current_frame = None
        self.camera_active = False
        self.cap = None
        
        # Crear frames
        self.frames = {}
        self._create_frames()
        
        # Mostrar menú inicial
        self.show_frame("MenuFrame")
    
    def _create_frames(self):
        """Crea todos los frames de la aplicación"""
        container = tk.Frame(self.root, bg=BG_DARK)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        for F in (MenuFrame, LoginFrame, RegisterFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
    
    def show_frame(self, cont, **kwargs):
        """Muestra un frame específico"""
        # Si hay cámara activa, detenerla
        if self.camera_active:
            self.stop_camera()
        
        # Ocultar frame actual
        if self.current_frame:
            self.frames[self.current_frame].grid_remove()
        
        # Mostrar nuevo frame
        frame = self.frames[cont]
        frame.grid()
        frame.tkraise()
        self.current_frame = cont
        
        # Llamar método de inicialización si existe
        if hasattr(frame, 'on_show'):
            frame.on_show(**kwargs)
    
    def start_camera(self, callback=None):
        """Inicia la cámara"""
        if self.camera_active:
            return
        
        try:
            if USE_ADVANCED:
                self.cap = open_camera()
            else:
                self.cap = cv2.VideoCapture(0)
            
            if self.cap is None or not self.cap.isOpened():
                messagebox.showerror("Error", "No se puede acceder a la cámara")
                return False
            
            self.camera_active = True
            self.camera_callback = callback
            
            # Inicia thread de captura
            threading.Thread(target=self._camera_loop, daemon=True).start()
            return True
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar cámara: {e}")
            print(f"Error: {e}")
            return False
    
    def stop_camera(self):
        """Detiene la cámara"""
        self.camera_active = False
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def _camera_loop(self):
        """Loop principal de captura"""
        while self.camera_active and self.cap:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame = cv2.resize(frame, (640, 480))
                
                # Llamar callback del frame actual
                frame_name = self.current_frame
                if frame_name in self.frames:
                    frame_obj = self.frames[frame_name]
                    if hasattr(frame_obj, 'process_frame'):
                        frame_obj.process_frame(frame)
                
                time.sleep(0.03)
            
            except Exception as e:
                print(f"Error en camera loop: {e}")
                break
        
        if self.cap:
            self.cap.release()


# ═══════════════════════════════════════════════════════════════════════════════
# FRAME 1: MENÚ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
class MenuFrame(tk.Frame):
    """Frame del menú principal"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=BG_DARK)
        self.controller = controller
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz del menú"""
        
        # ── Panel Superior ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLOR_PRIMARY, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔐",
            font=("Segoe UI", 48),
            fg=COLOR_WHITE,
            bg=COLOR_PRIMARY
        ).pack(pady=(10, 0))
        
        tk.Label(
            header,
            text="IDENTIFYME",
            font=("Segoe UI", 22, "bold"),
            fg=COLOR_WHITE,
            bg=COLOR_PRIMARY
        ).pack()
        
        tk.Label(
            header,
            text="Sistema de Acceso Facial",
            font=("Segoe UI", 10),
            fg=COLOR_LIGHTER,
            bg=COLOR_PRIMARY
        ).pack(pady=(0, 10))
        
        # ── Separador ───────────────────────────────────────────────────────
        sep = tk.Frame(self, bg=COLOR_SECONDARY, height=2)
        sep.pack(fill="x", pady=20)
        
        # ── Panel de opciones ───────────────────────────────────────────────
        content = tk.Frame(self, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=30, pady=20)
        
        tk.Label(
            content,
            text="¿Qué deseas hacer?",
            font=("Segoe UI", 14, "bold"),
            fg=COLOR_WHITE,
            bg=BG_DARK
        ).pack(pady=(0, 30))
        
        # ── Botón Login ─────────────────────────────────────────────────────
        btn_login = tk.Button(
            content,
            text="🔓 INICIAR SESIÓN",
            font=("Segoe UI", 13, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_WHITE,
            activebackground=COLOR_SECONDARY,
            activeforeground=COLOR_WHITE,
            padx=40,
            pady=20,
            command=lambda: self.controller.show_frame("LoginFrame"),
            relief="flat",
            cursor="hand2"
        )
        btn_login.pack(fill="x", pady=10)
        
        tk.Label(
            content,
            text="Accesa con tu rostro registrado",
            font=("Segoe UI", 9),
            fg=COLOR_LIGHT,
            bg=BG_DARK
        ).pack(anchor="w", padx=10)
        
        # ── Separador visual ────────────────────────────────────────────────
        sep2 = tk.Frame(content, bg=COLOR_ACCENT, height=1)
        sep2.pack(fill="x", pady=20)
        
        # ── Botón Registro ──────────────────────────────────────────────────
        btn_register = tk.Button(
            content,
            text="✏ REGISTRAR NUEVO USUARIO",
            font=("Segoe UI", 13, "bold"),
            bg=COLOR_SECONDARY,
            fg=COLOR_WHITE,
            activebackground=COLOR_TERTIARY,
            activeforeground=COLOR_WHITE,
            padx=40,
            pady=20,
            command=lambda: self.controller.show_frame("RegisterFrame"),
            relief="flat",
            cursor="hand2"
        )
        btn_register.pack(fill="x", pady=10)
        
        tk.Label(
            content,
            text="Registra tu biometría facial",
            font=("Segoe UI", 9),
            fg=COLOR_LIGHT,
            bg=BG_DARK
        ).pack(anchor="w", padx=10)
        
        # ── Footer ──────────────────────────────────────────────────────────
        footer = tk.Frame(self, bg=COLOR_DARKER, height=50)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        tk.Label(
            footer,
            text="© 2026 Identifyme - Sistema de Reconocimiento Facial",
            font=("Segoe UI", 8),
            fg=COLOR_LIGHT,
            bg=COLOR_DARKER
        ).pack(pady=15)


# ═══════════════════════════════════════════════════════════════════════════════
# FRAME 2: LOGIN CON RECONOCIMIENTO FACIAL
# ═══════════════════════════════════════════════════════════════════════════════
class LoginFrame(tk.Frame):
    """Frame de login con reconocimiento facial"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=BG_DARK)
        self.controller = controller
        
        # Variables de estado
        self.state = UIState.IDLE
        self.user_data = None
        self.last_frame = None
        
        # Datos de reconocimiento
        self.rostros_db = []
        self.nombres_db = []
        self.ids_db = []
        self.datos_estudiantes = {}
        
        # Control de cooldown
        self.ultima_bitacora = {}
        self.cooldown_segundos = 3.0
        
        self._build_ui()
        self._load_recognition_data()
    
    def _build_ui(self):
        """Construye la interfaz de login"""
        
        # ── Panel Superior ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLOR_PRIMARY, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔐 Sistema de Acceso Facial",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_WHITE,
            bg=COLOR_PRIMARY
        ).pack(pady=5)
        
        # ── Canvas para Video ───────────────────────────────────────────────
        video_frame = tk.Frame(self, bg=BG_CARD)
        video_frame.pack(pady=5, padx=5, fill="both", expand=False)
        
        self.video_canvas = tk.Canvas(
            video_frame,
            width=480,
            height=360,
            bg="black",
            highlightthickness=2,
            highlightbackground=COLOR_PRIMARY
        )
        self.video_canvas.pack()
        
        # ── Información del Usuario ─────────────────────────────────────────
        info_frame = tk.Frame(self, bg=COLOR_ACCENT, height=60)
        info_frame.pack(pady=3, padx=5, fill="x")
        info_frame.pack_propagate(False)
        
        photo_frame = tk.Frame(info_frame, bg=COLOR_ACCENT)
        photo_frame.pack(side="left", padx=5, pady=3)
        
        self.photo_label = tk.Label(
            photo_frame,
            width=6,
            height=3,
            bg=COLOR_LIGHTER,
            fg=COLOR_PRIMARY,
            font=("Segoe UI", 8, "bold"),
            text="📷",
            highlightthickness=1,
            highlightbackground=COLOR_PRIMARY
        )
        self.photo_label.pack()
        
        # Datos del usuario
        data_frame = tk.Frame(info_frame, bg=COLOR_ACCENT)
        data_frame.pack(side="left", fill="both", expand=True, padx=10, pady=3)
        
        self.label_nombre = tk.Label(
            data_frame,
            text="Nombre: ---",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_ACCENT
        )
        self.label_nombre.pack(anchor="w", pady=1)
        
        self.label_salon = tk.Label(
            data_frame,
            text="Salón: ---",
            font=("Segoe UI", 8),
            fg=COLOR_PRIMARY,
            bg=COLOR_ACCENT
        )
        self.label_salon.pack(anchor="w", pady=0)
        
        self.label_edad = tk.Label(
            data_frame,
            text="Edad: ---",
            font=("Segoe UI", 8),
            fg=COLOR_PRIMARY,
            bg=COLOR_ACCENT
        )
        self.label_edad.pack(anchor="w", pady=0)
        
        self.label_id = tk.Label(
            data_frame,
            text="ID: ---",
            font=("Segoe UI", 8),
            fg=COLOR_PRIMARY,
            bg=COLOR_ACCENT
        )
        self.label_id.pack(anchor="w", pady=0)
        
        # ── Área de Mensajes ────────────────────────────────────────────────
        msg_frame = tk.Frame(self, bg=BG_DARK, height=40)
        msg_frame.pack(pady=2, padx=5, fill="x")
        msg_frame.pack_propagate(False)
        
        self.message_label = tk.Label(
            msg_frame,
            text="ESPERANDO ROSTRO...",
            font=("Segoe UI", 10, "bold"),
            fg=COLOR_SECONDARY,
            bg=BG_DARK,
            wraplength=300
        )
        self.message_label.pack(pady=5)
        
        # ── Panel de Controles ──────────────────────────────────────────────
        button_frame = tk.Frame(self, bg=BG_DARK)
        button_frame.pack(pady=3, padx=5, fill="x")
        
        self.btn_start = tk.Button(
            button_frame,
            text="▶ Iniciar",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_WHITE,
            activebackground=COLOR_SECONDARY,
            activeforeground=COLOR_WHITE,
            padx=10,
            pady=5,
            command=self._start_login,
            relief="flat",
            cursor="hand2"
        )
        self.btn_start.pack(side="left", padx=3)
        
        self.btn_stop = tk.Button(
            button_frame,
            text="⏹ Detener",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_RED,
            fg=COLOR_WHITE,
            activebackground="#dc2626",
            activeforeground=COLOR_WHITE,
            padx=10,
            pady=5,
            command=self._stop_login,
            relief="flat",
            cursor="hand2",
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=3)
        
        self.btn_back = tk.Button(
            button_frame,
            text="← Atrás",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT,
            fg=COLOR_PRIMARY,
            activebackground=COLOR_LIGHT,
            activeforeground=COLOR_PRIMARY,
            padx=10,
            pady=5,
            command=lambda: self.controller.show_frame("MenuFrame"),
            relief="flat",
            cursor="hand2"
        )
        self.btn_back.pack(side="right", padx=3)
        
        # ── Status bar ──────────────────────────────────────────────────────
        status_frame = tk.Frame(self, bg=COLOR_DARKER, height=30)
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Listo",
            font=("Segoe UI", 9),
            fg=COLOR_LIGHT,
            bg=COLOR_DARKER
        )
        self.status_label.pack(side="left", padx=10, pady=5)
    
    def on_show(self):
        """Se llama cuando el frame es mostrado"""
        pass
    
    def _load_recognition_data(self):
        """Carga los datos de reconocimiento facial"""
        try:
            if USE_ADVANCED:
                auth_service = AuthService(SQLiteRepository())
                auth_service.initialize()
                self.rostros_db, self.nombres_db, self.ids_db = auth_service.load_known_students()
            
            if not self.rostros_db:
                self._load_pkl_database()
            
            if self.rostros_db:
                self.status_label.config(
                    text=f"✓ {len(self.rostros_db)} usuarios cargados",
                    fg=COLOR_SECONDARY
                )
            else:
                self.status_label.config(
                    text="⚠ No hay usuarios registrados",
                    fg=COLOR_ORANGE
                )
        except Exception as e:
            self.status_label.config(
                text=f"✗ Error cargando datos: {str(e)[:40]}",
                fg=COLOR_RED
            )
            print(f"Error cargando datos: {e}")
    
    def _load_pkl_database(self):
        """Carga base de datos desde archivos .pkl"""
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
    
    def _start_login(self):
        """Inicia el login"""
        if not self.rostros_db:
            self.set_state(UIState.ERROR)
            self.message_label.config(text="ERROR: No hay usuarios registrados")
            return
        
        if not self.controller.start_camera():
            return
        
        self.state = UIState.WAITING
        self.user_data = None
        self._reset_user_display()
        
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.status_label.config(text="🔴 Cámara activa", fg=COLOR_RED)
    
    def _stop_login(self):
        """Detiene el login"""
        self.controller.stop_camera()
        
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status_label.config(text="Cámara detenida", fg=COLOR_LIGHT)
        self.set_state(UIState.IDLE)
        self._reset_user_display()
        self.video_canvas.delete("all")
        self.video_canvas.create_text(
            240, 180, text="Cámara detenida", 
            fill=COLOR_ACCENT, font=("Segoe UI", 14)
        )
    
    def process_frame(self, frame):
        """Procesa cada frame de la cámara"""
        try:
            frame = cv2.resize(frame, (480, 360))
            self.last_frame = frame.copy()
            
            # Procesamiento de reconocimiento
            self._process_frame(frame)
            
            # Mostrar en canvas
            self._display_frame(frame)
        except Exception as e:
            print(f"Error procesando frame: {e}")
    
    def _process_frame(self, frame):
        """Procesa el frame para detección y reconocimiento"""
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            if USE_ADVANCED:
                face_locations, encodings = detect_face_encodings_from_frame(frame, scale=0.25)
            else:
                face_locations = []
                encodings = []
            
            if len(encodings) == 0:
                self.set_state(UIState.WAITING)
                return
            
            if len(encodings) == 1:
                self.set_state(UIState.VERIFYING)
                self._verify_face(encodings[0], frame)
            else:
                self.set_state(UIState.POSITIONING)
                self.message_label.config(text="CENTRA TU ROSTRO")
        
        except Exception as e:
            print(f"Error procesando frame: {e}")
            self.set_state(UIState.ERROR)
    
    def _verify_face(self, encoding, frame):
        """Verifica el rostro detectado"""
        try:
            if USE_ADVANCED:
                idx = find_first_match(self.rostros_db, encoding, tolerance=0.5)
            else:
                idx = -1
            
            if idx >= 0 and idx < len(self.nombres_db):
                name = self.nombres_db[idx]
                user_id = self.ids_db[idx] if idx < len(self.ids_db) else 0
                
                self.set_state(UIState.GRANTED)
                self.user_data = {
                    "nombre": name,
                    "id": user_id,
                    "salon": "---",
                    "edad": "---"
                }
                self._update_user_display()
                
                if user_id > 0:
                    ahora = time.monotonic()
                    ultimo = self.ultima_bitacora.get(user_id, 0.0)
                    if ahora - ultimo >= self.cooldown_segundos:
                        try:
                            if USE_ADVANCED:
                                auth = AuthService(SQLiteRepository())
                                auth.log_access(user_id, True)
                        except:
                            pass
                        self.ultima_bitacora[user_id] = ahora
            else:
                self.set_state(UIState.DENIED)
                self.user_data = None
                self._reset_user_display()
        
        except Exception as e:
            print(f"Error verificando rostro: {e}")
            self.set_state(UIState.ERROR)
    
    def _display_frame(self, frame):
        """Muestra el frame en el canvas"""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Dibujar elementos visuales
            self._draw_ui_elements(frame_rgb)
            
            # Convertir a PIL
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(img)
            
            # Actualizar canvas
            self.video_canvas.create_image(0, 0, anchor="nw", image=imgtk)
            self.video_canvas.image = imgtk
        
        except Exception as e:
            print(f"Error mostrando frame: {e}")
    
    def _draw_ui_elements(self, frame_rgb):
        """Dibuja elementos visuales en el frame"""
        h, w = frame_rgb.shape[:2]
        center = (w // 2, h // 2)
        
        color_oval = self._get_state_color()
        oval_x, oval_y = int(w * 0.25), int(h * 0.4)
        cv2.ellipse(frame_rgb, center, (oval_x, oval_y), 0, 0, 360, color_oval, 3)
        
        cv2.rectangle(frame_rgb, (0, 0), (w, 50), (15, 23, 42), -1)
        current_msg = self.message_label.cget("text").split('\n')[0]
        cv2.putText(frame_rgb, current_msg, (15, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_oval, 2)
    
    def set_state(self, new_state):
        """Establece el estado de la UI"""
        self.state = new_state
        
        state_config = {
            UIState.IDLE: ("LISTA", COLOR_PRIMARY),
            UIState.WAITING: ("ESPERANDO ROSTRO...", COLOR_SECONDARY),
            UIState.DETECTING: ("DETECTANDO ROSTRO...", COLOR_ACCENT),
            UIState.VERIFYING: ("VERIFICANDO...", COLOR_ORANGE),
            UIState.POSITIONING: ("CENTRA TU ROSTRO", COLOR_ACCENT),
            UIState.GRANTED: ("✓ ACCESO CONCEDIDO", COLOR_PRIMARY),
            UIState.DENIED: ("✗ ACCESO DENEGADO", COLOR_RED),
            UIState.RESTRICTED: ("⛔ ACCESO RESTRINGIDO", COLOR_RED),
            UIState.ERROR: ("ERROR AL VERIFICAR", COLOR_RED),
        }
        
        msg, color = state_config.get(new_state, ("DESCONOCIDO", COLOR_ACCENT))
        self.message_label.config(text=msg, fg=color)
    
    def _get_state_color(self):
        """Retorna color BGR para el estado actual"""
        color_map = {
            UIState.IDLE: (0, 143, 57),
            UIState.WAITING: (72, 162, 89),
            UIState.DETECTING: (112, 181, 120),
            UIState.VERIFYING: (22, 115, 249),
            UIState.POSITIONING: (149, 199, 153),
            UIState.GRANTED: (57, 143, 0),
            UIState.DENIED: (68, 68, 239),
            UIState.RESTRICTED: (68, 68, 239),
            UIState.ERROR: (68, 68, 239),
        }
        return color_map.get(self.state, (255, 255, 255))
    
    def _reset_user_display(self):
        """Resetea la información del usuario"""
        self.label_nombre.config(text="Nombre: ---")
        self.label_salon.config(text="Salón: ---")
        self.label_edad.config(text="Edad: ---")
        self.label_id.config(text="ID: ---")
    
    def _update_user_display(self):
        """Actualiza la información del usuario"""
        if not self.user_data:
            return
        
        self.label_nombre.config(text=f"Nombre: {self.user_data['nombre'].upper()}")
        self.label_salon.config(text=f"Salón: {self.user_data['salon']}")
        self.label_edad.config(text=f"Edad: {self.user_data['edad']}")
        self.label_id.config(text=f"ID: #{self.user_data['id']}")


# ═══════════════════════════════════════════════════════════════════════════════
# FRAME 3: REGISTRO DE USUARIO
# ═══════════════════════════════════════════════════════════════════════════════
class RegisterFrame(tk.Frame):
    """Frame de registro de usuario"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=BG_DARK)
        self.controller = controller
        
        # Variables de estado
        self.state = "waiting_name"  # waiting_name, capturing
        self.capture_data = None
        self.nombre_usuario = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz de registro"""
        
        # ── Panel Superior ──────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLOR_SECONDARY, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="✏ REGISTRO FACIAL",
            font=("Segoe UI", 14, "bold"),
            fg=COLOR_WHITE,
            bg=COLOR_SECONDARY
        ).pack(pady=8)
        
        # ── Contenedor principal ────────────────────────────────────────────
        content_frame = tk.Frame(self, bg=BG_DARK)
        content_frame.pack(fill="both", expand=True, pady=10, padx=15)
        
        # ── SECCIÓN 1: Datos del usuario ────────────────────────────────────
        data_section = tk.LabelFrame(
            content_frame,
            text="Información del Usuario",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_LIGHTER,
            fg=COLOR_PRIMARY,
            padx=20,
            pady=15
        )
        data_section.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            data_section,
            text="Nombre (o identificador):",
            font=("Segoe UI", 9),
            fg=COLOR_PRIMARY,
            bg=COLOR_LIGHTER
        ).pack(anchor="w")
        
        input_frame = tk.Frame(data_section, bg=COLOR_LIGHTER)
        input_frame.pack(fill="x", pady=(5, 0))
        
        self.entry_nombre = tk.Entry(
            input_frame,
            font=("Segoe UI", 10),
            bg=COLOR_WHITE,
            fg="black",
            insertbackground=COLOR_PRIMARY,
            relief="solid",
            bd=1
        )
        self.entry_nombre.pack(side="left", fill="x", expand=True)
        
        btn_submit = tk.Button(
            input_frame,
            text="Continuar →",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_WHITE,
            activebackground=COLOR_SECONDARY,
            command=self._proceed_to_capture,
            relief="flat",
            cursor="hand2",
            padx=15
        )
        btn_submit.pack(side="left", padx=(10, 0))
        
        self.label_estado = tk.Label(
            data_section,
            text="",
            font=("Segoe UI", 8),
            fg=COLOR_RED,
            bg=COLOR_LIGHTER
        )
        self.label_estado.pack(anchor="w", pady=(8, 0))
        
        # ── Instrucciones ───────────────────────────────────────────────────
        inst_frame = tk.LabelFrame(
            content_frame,
            text="Instrucciones",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_LIGHTER,
            fg=COLOR_PRIMARY,
            padx=15,
            pady=10
        )
        inst_frame.pack(fill="x", pady=(0, 10))
        
        instructions = [
            "✓ Asegúrate de tener buena iluminación",
            "✓ Tu rostro debe estar completamente visible",
            "✓ Mantén una distancia de 30-50 cm",
        ]
        
        for instr in instructions:
            tk.Label(
                inst_frame,
                text=instr,
                font=("Segoe UI", 8),
                fg=COLOR_PRIMARY,
                bg=COLOR_LIGHTER,
                justify="left"
            ).pack(anchor="w", pady=2)
        
        # ── Canvas para Video ───────────────────────────────────────────────
        self.video_canvas = tk.Canvas(
            content_frame,
            width=610,
            height=200,
            bg="black",
            highlightthickness=2,
            highlightbackground=COLOR_PRIMARY
        )
        self.video_canvas.pack(pady=(0, 10))
        
        # ── Controles ───────────────────────────────────────────────────────
        button_frame = tk.Frame(content_frame, bg=BG_DARK)
        button_frame.pack(fill="x")
        
        self.btn_start = tk.Button(
            button_frame,
            text="▶ Iniciar",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_WHITE,
            activebackground=COLOR_SECONDARY,
            padx=15,
            pady=8,
            command=self._start_capture,
            relief="flat",
            cursor="hand2",
            state="disabled"
        )
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_capture = tk.Button(
            button_frame,
            text="📸 Capturar",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ORANGE,
            fg=COLOR_WHITE,
            activebackground="#ea580c",
            padx=15,
            pady=8,
            command=self._save_capture,
            relief="flat",
            cursor="hand2",
            state="disabled"
        )
        self.btn_capture.pack(side="left", padx=5)
        
        self.btn_stop = tk.Button(
            button_frame,
            text="⏹ Detener",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_RED,
            fg=COLOR_WHITE,
            activebackground="#dc2626",
            padx=15,
            pady=8,
            command=self._stop_capture,
            relief="flat",
            cursor="hand2",
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_back = tk.Button(
            button_frame,
            text="← Atrás",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT,
            fg=COLOR_PRIMARY,
            activebackground=COLOR_LIGHT,
            padx=15,
            pady=8,
            command=lambda: self.controller.show_frame("MenuFrame"),
            relief="flat",
            cursor="hand2"
        )
        self.btn_back.pack(side="right", padx=5)
        
        # ── Status bar ──────────────────────────────────────────────────────
        status_frame = tk.Frame(self, bg=COLOR_DARKER, height=30)
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ingresa tu nombre para comenzar",
            font=("Segoe UI", 8),
            fg=COLOR_LIGHT,
            bg=COLOR_DARKER
        )
        self.status_label.pack(side="left", padx=10, pady=5)
    
    def on_show(self):
        """Se llama cuando el frame es mostrado"""
        self.entry_nombre.config(state="normal")
        self.entry_nombre.delete(0, tk.END)
        self.label_estado.config(text="")
        self.nombre_usuario = None
        self.state = "waiting_name"
        self.btn_start.config(state="disabled")
    
    def _proceed_to_capture(self):
        """Procede al paso de captura"""
        nombre = self.entry_nombre.get().strip().lower()
        
        if not nombre:
            self.label_estado.config(text="⚠ Por favor ingresa un nombre")
            return
        
        if not nombre.isalnum():
            self.label_estado.config(text="⚠ Solo letras y números")
            return
        
        if not os.path.exists("data"):
            os.makedirs("data")
        
        if os.path.exists(f"data/{nombre}.pkl"):
            if not messagebox.askyesno("Confirmar", f"¿Reemplazar '{nombre}'?"):
                return
        
        self.nombre_usuario = nombre
        self.entry_nombre.config(state="disabled")
        self.btn_start.config(state="normal")
        self.label_estado.config(text=f"✓ {nombre.upper()}", fg=COLOR_PRIMARY)
        self.status_label.config(text="Haz clic en 'Iniciar'")
    
    def _start_capture(self):
        """Inicia la captura"""
        if not self.controller.start_camera():
            return
        
        self.state = "capturing"
        self.btn_start.config(state="disabled")
        self.btn_capture.config(state="normal")
        self.btn_stop.config(state="normal")
        self.status_label.config(text="Cámara activa - Centra tu rostro")
    
    def _stop_capture(self):
        """Detiene la captura"""
        self.controller.stop_camera()
        
        self.state = "waiting_camera"
        self.btn_start.config(state="normal")
        self.btn_capture.config(state="disabled")
        self.btn_stop.config(state="disabled")
        self.status_label.config(text="Captura detenida")
        self.video_canvas.delete("all")
    
    def _save_capture(self):
        """Guarda el frame capturado"""
        if self.capture_data is None:
            messagebox.showwarning("Aviso", "No hay frame capturado")
            return
        
        try:
            if not USE_FACE_RECOGNITION:
                messagebox.showerror("Error", "Se requiere face_recognition")
                return
            
            rgb = cv2.cvtColor(self.capture_data, cv2.COLOR_BGR2RGB)
            
            boxes = face_recognition.face_locations(rgb)
            
            if len(boxes) != 1:
                messagebox.showwarning(
                    "Aviso",
                    f"Se detectaron {len(boxes)} rostros.\nDebe haber exactamente 1"
                )
                return
            
            encoding = face_recognition.face_encodings(rgb, boxes)[0]
            
            os.makedirs("data", exist_ok=True)
            with open(f"data/{self.nombre_usuario}.pkl", "wb") as f:
                pickle.dump(encoding, f)
            
            messagebox.showinfo(
                "Éxito",
                f"✓ Usuario '{self.nombre_usuario}' registrado"
            )
            
            self._stop_capture()
            self.controller.show_frame("MenuFrame")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando: {e}")
            print(f"Error: {e}")
    
    def process_frame(self, frame):
        """Procesa cada frame de la cámara"""
        try:
            # Redimensionar a 610x200 para el canvas
            frame_resized = cv2.resize(frame, (610, 200))
            self.capture_data = cv2.resize(frame, (640, 480))  # Original para guardar
            
            # Dibujar guía visual
            h, w = frame_resized.shape[:2]
            center = (w // 2, h // 2)
            
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # Óvalo guía
            oval_x, oval_y = int(w * 0.25), int(h * 0.4)
            cv2.ellipse(frame_rgb, center, (oval_x, oval_y), 0, 0, 360, (0, 143, 57), 3)
            
            # Texto
            cv2.rectangle(frame_rgb, (0, 0), (w, 35), (26, 39, 65), -1)
            cv2.putText(frame_rgb, "Centra tu rostro en el óvalo", (15, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 143, 57), 2)
            
            # Mostrar
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(img)
            
            self.video_canvas.create_image(0, 0, anchor="nw", image=imgtk)
            self.video_canvas.image = imgtk
        
        except Exception as e:
            print(f"Error procesando frame: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
