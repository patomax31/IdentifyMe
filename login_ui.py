"""
Módulo de interfaz gráfica de login con reconocimiento facial
Contiene solo la presentación (UI) de la aplicación
"""
import cv2
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import threading

import numpy as np

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

COLOR_RED = "#ef4444"          # Rojo
COLOR_ORANGE = "#f97316"       # Naranja

BG_DARK = "#0f172a"
BG_CARD = "#1e293b"


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADOS DE LA INTERFAZ
# ═══════════════════════════════════════════════════════════════════════════════
class UIState:
    """Estados posibles de la interfaz de login"""
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
# INTERFAZ DE LOGIN CON CÁMARA
# ═══════════════════════════════════════════════════════════════════════════════
class FaceLoginUI:
    """
    Interfaz gráfica de login con reconocimiento facial en tiempo real.
    
    Responsabilidades:
    - Renderizar la UI en Tkinter
    - Capturar frames de cámara
    - Mostrar mensajes y estado
    - Delegar lógica de autenticación al servicio
    """
    
    def __init__(self, login_service, parent=None):
        """
        Inicializa la interfaz.
        
        Args:
            login_service: Instancia de FaceLoginService
            parent: Widget padre (opcional)
        """
        self.service = login_service
        
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("Sistema de Acceso Facial")
        self.root.geometry("600x1024")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        
        # Variables de estado de UI
        self.state = UIState.IDLE
        self.camera_active = False
        self.cap = None
        self.user_data = None
        self.last_frame = None
        
        # Build UI
        self._build_ui()
        self._update_status_message()
    
    def _build_ui(self):
        """Construye la interfaz gráfica"""
        # ── Panel Superior ─────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=COLOR_PRIMARY, height=40)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔐 Sistema de Acceso Facial",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_WHITE,
            bg=COLOR_PRIMARY
        ).pack(pady=5)
        
        # ── Canvas para Video ──────────────────────────────────────────────────
        video_frame = tk.Frame(self.root, bg=BG_CARD)
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
        
        # ── Información del Usuario ───────────────────────────────────────────
        info_frame = tk.Frame(self.root, bg=COLOR_ACCENT, height=60)
        info_frame.pack(pady=3, padx=5, fill="x")
        info_frame.pack_propagate(False)
        
        # Foto circular (placeholder)
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
        
        # ── Área de Mensajes ──────────────────────────────────────────────────
        msg_frame = tk.Frame(self.root, bg=BG_DARK, height=40)
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
        
        # ── Panel de Controles ─────────────────────────────────────────────────
        button_frame = tk.Frame(self.root, bg=BG_DARK)
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
            command=self.start_camera,
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
            command=self.stop_camera,
            relief="flat",
            cursor="hand2",
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=3)
        
        self.btn_close = tk.Button(
            button_frame,
            text="✕ Cerrar",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_ACCENT,
            fg=COLOR_PRIMARY,
            activebackground=COLOR_LIGHT,
            activeforeground=COLOR_PRIMARY,
            padx=10,
            pady=5,
            command=self.root.quit,
            relief="flat",
            cursor="hand2"
        )
        self.btn_close.pack(side="right", padx=3)
        
        # ── Status bar ─────────────────────────────────────────────────────────
        status_frame = tk.Frame(self.root, bg=COLOR_DARKER, height=30)
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
    
    def _update_status_message(self):
        """Actualiza el mensaje de estado en la barra inferior"""
        users_count = self.service.get_users_count()
        
        if users_count > 0:
            self.status_label.config(
                text=f"✓ {users_count} usuarios cargados",
                fg=COLOR_SECONDARY
            )
        else:
            self.status_label.config(
                text="⚠ No hay usuarios registrados",
                fg=COLOR_ORANGE
            )
    
    def start_camera(self):
        """Inicia la cámara y comienza el reconocimiento"""
        if self.camera_active:
            return
        
        if not self.service.has_users():
            self.set_state(UIState.ERROR)
            self.message_label.config(text="ERROR: No hay usuarios registrados")
            return
        
        try:
            try:
                from src.infrastructure.camera.opencv_camera import open_camera
                self.cap = open_camera()
            except (ImportError, Exception):
                self.cap = cv2.VideoCapture(0)
            
            if self.cap is None or not self.cap.isOpened():
                self.set_state(UIState.ERROR)
                self.message_label.config(text="ERROR: No se puede acceder a la cámara")
                return
            
            self.camera_active = True
            self.state = UIState.WAITING
            self.user_data = None
            self._reset_user_display()
            
            # Inicia el thread de captura
            threading.Thread(target=self._camera_loop, daemon=True).start()
            
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.status_label.config(text="🔴 Cámara activa", fg=COLOR_RED)
        
        except Exception as e:
            self.set_state(UIState.ERROR)
            self.message_label.config(text=f"ERROR: {str(e)}")
            print(f"Error al iniciar cámara: {e}")
    
    def stop_camera(self):
        """Detiene la cámara"""
        self.camera_active = False
        if self.cap:
            self.cap.release()
        
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status_label.config(text="Cámara detenida", fg=COLOR_LIGHT)
        self.set_state(UIState.IDLE)
        self._reset_user_display()
        self.video_canvas.delete("all")
        self.video_canvas.create_text(320, 240, text="Cámara detenida", 
                                     fill=COLOR_ACCENT, font=("Segoe UI", 14))
    
    def _camera_loop(self):
        """Loop principal de captura de cámara"""
        while self.camera_active:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Redimensionar para procesamiento
                frame = cv2.resize(frame, (640, 480))
                self.last_frame = frame.copy()
                
                # Procesamiento de reconocimiento
                self._process_frame(frame)
                
                # Convertir frame para mostrar en Tkinter
                self._display_frame(frame)
                
                # Pequeño delay para no saturar
                time.sleep(0.03)
                
            except Exception as e:
                print(f"Error en camera loop: {e}")
                break
        
        if self.cap:
            self.cap.release()
    
    def _process_frame(self, frame):
        """Procesa el frame para detección y reconocimiento"""
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Delega detección al servicio
            face_locations, encodings = self.service.detect_face_in_frame(frame)
            
            # Sin rostro detectado
            if len(encodings) == 0:
                self.set_state(UIState.WAITING)
                return
            
            # Un rostro detectado
            if len(encodings) == 1:
                self.set_state(UIState.VERIFYING)
                self._verify_face(encodings[0], frame)
            else:
                # Múltiples rostros
                self.set_state(UIState.POSITIONING)
                self.message_label.config(text="CENTRA TU ROSTRO")
        
        except Exception as e:
            print(f"Error procesando frame: {e}")
            self.set_state(UIState.ERROR)
    
    def _verify_face(self, encoding, frame):
        """Verifica el rostro detectado contra la base de datos"""
        try:
            # Delega verificación al servicio
            encontrado, user_data = self.service.verify_face(encoding)
            
            if encontrado:
                self.set_state(UIState.GRANTED)
                self.user_data = user_data
                self._update_user_display()
                
                # Log de acceso
                if user_data["id"] > 0:
                    self.service.log_access(user_data["id"], True)
            else:
                self.set_state(UIState.DENIED)
                self.user_data = None
                self._reset_user_display()
        
        except Exception as e:
            print(f"Error verificando rostro: {e}")
            self.set_state(UIState.ERROR)
    
    def _display_frame(self, frame):
        """Muestra el frame en el canvas de Tkinter"""
        try:
            # Convertir BGR a RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Dibujar elementos visuales
            self._draw_ui_elements(frame_rgb)
            
            # Convertir a PIL Image
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(img)
            
            # Actualizar canvas
            self.video_canvas.create_image(0, 0, anchor="nw", image=imgtk)
            self.video_canvas.image = imgtk
        
        except Exception as e:
            print(f"Error mostrando frame: {e}")
    
    def _draw_ui_elements(self, frame_rgb):
        """Dibuja elementos de UI en el frame (guía visual)"""
        h, w = frame_rgb.shape[:2]
        center = (w // 2, h // 2)
        
        # Oval guía
        color_oval = self._get_state_color()
        oval_x, oval_y = int(w * 0.25), int(h * 0.4)
        cv2.ellipse(frame_rgb, center, (oval_x, oval_y), 0, 0, 360, color_oval, 3)
        
        # Barra superior con mensaje
        cv2.rectangle(frame_rgb, (0, 0), (w, 50), (15, 23, 42), -1)
        current_msg = self.message_label.cget("text").split('\n')[0]
        cv2.putText(frame_rgb, current_msg, (15, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, color_oval, 2)
    
    def set_state(self, new_state):
        """Establece el estado y actualiza el mensaje"""
        self.state = new_state
        
        # Mapeo de estados a mensajes y colores
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
        """Retorna el color BGR para el estado actual"""
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
        """Resetea la pantalla de información del usuario"""
        self.label_nombre.config(text="Nombre: ---")
        self.label_salon.config(text="Salón: ---")
        self.label_edad.config(text="Edad: ---")
        self.label_id.config(text="ID: ---")
    
    def _update_user_display(self):
        """Actualiza la pantalla con datos del usuario"""
        if not self.user_data:
            return
        
        self.label_nombre.config(text=f"Nombre: {self.user_data['nombre'].upper()}")
        self.label_salon.config(text=f"Salón: {self.user_data['salon']}")
        self.label_edad.config(text=f"Edad: {self.user_data['edad']}")
        self.label_id.config(text=f"ID: #{self.user_data['id']}")
    
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()
<<<<<<< HEAD
=======

>>>>>>> 2e2d95e (UI de la cargainicial de dependencias test_setup.py)
