import tkinter as tk
from enum import Enum
from tkinter import ttk
from typing import Optional

import cv2
from PIL import Image, ImageTk

from src.application.auth_service import AuthService
from src.application.login_use_case import LoginUseCase
from src.application.registration_service import RegistrationService
from src.application.registration_use_case import RegistrationUseCase
from src.core.config import get_recognition_settings
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame
from src.infrastructure.recognition.matcher_adapter import FaceMatcherAdapter


class AppState(Enum):
    HOME = "home"
    LOGIN = "login"
    REGISTRATION = "registration"


class StateManager:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.current_state = AppState.HOME

        self.recognition_settings = get_recognition_settings()

        self.cap: Optional[cv2.VideoCapture] = None
        self.camera_job: Optional[str] = None
        self.camera_label: Optional[tk.Label] = None
        self.camera_photo: Optional[ImageTk.PhotoImage] = None
        self.last_frame = None

        self.login_use_case: Optional[LoginUseCase] = None
        self.known_encodings = []
        self.known_labels = []
        self.known_ids = []

        self.registration_use_case: Optional[RegistrationUseCase] = None

        self.status_var = tk.StringVar(value="Listo para iniciar.")
        self.name_var = tk.StringVar()
        self.grade_var = tk.StringVar(value="1")
        self.group_var = tk.StringVar()
        self.shift_var = tk.StringVar(value="MATUTINO")

        self._build_shell()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_shell(self) -> None:
        self.root.title("Sistema Facial")
        self.root.geometry("760x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.outer_frame = tk.Frame(
            self.root,
            bg="#1e293b",
            highlightbackground="#334155",
            highlightthickness=1,
        )
        self.outer_frame.pack(fill="both", expand=True, padx=24, pady=20)

        self.title_label = tk.Label(
            self.outer_frame,
            text="Sistema de Acceso Facial",
            font=("Segoe UI", 17, "bold"),
            fg="white",
            bg="#1e293b",
        )
        self.title_label.pack(pady=(16, 4))

        self.subtitle_label = tk.Label(
            self.outer_frame,
            text="Reconocimiento facial en una sola ventana",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1e293b",
        )
        self.subtitle_label.pack(pady=(0, 10))

        separator = tk.Frame(self.outer_frame, bg="#334155", height=1)
        separator.pack(fill="x", padx=20, pady=(0, 10))

        self.content_frame = tk.Frame(self.outer_frame, bg="#1e293b")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.status_label = tk.Label(
            self.outer_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            fg="#93c5fd",
            bg="#1e293b",
            anchor="w",
        )
        self.status_label.pack(fill="x", padx=20, pady=(0, 14))

    def start(self) -> None:
        self.transition_to(AppState.HOME)

    def transition_to(self, state: AppState) -> None:
        self._stop_camera()
        self.current_state = state
        self._clear_content()

        if state == AppState.HOME:
            self._render_home()
        elif state == AppState.LOGIN:
            self._render_login()
        elif state == AppState.REGISTRATION:
            self._render_registration()

    def _clear_content(self) -> None:
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.camera_label = None
        self.camera_photo = None
        self.last_frame = None

    def _render_home(self) -> None:
        self.status_var.set("Selecciona una accion.")

        actions = tk.Frame(self.content_frame, bg="#1e293b")
        actions.pack(expand=True)

        btn_login = tk.Button(
            actions,
            text="Iniciar Sesion",
            font=("Segoe UI", 11, "bold"),
            width=22,
            height=2,
            bg="#7C3AED",
            fg="white",
            activebackground="#5B21B6",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            command=lambda: self.transition_to(AppState.LOGIN),
        )
        btn_login.pack(pady=(0, 12))

        btn_registro = tk.Button(
            actions,
            text="Registrar Usuario",
            font=("Segoe UI", 11, "bold"),
            width=22,
            height=2,
            bg="#1e293b",
            fg="#7C3AED",
            activebackground="#0f172a",
            activeforeground="#7C3AED",
            bd=1,
            relief="solid",
            cursor="hand2",
            command=lambda: self.transition_to(AppState.REGISTRATION),
        )
        btn_registro.pack()

    def _render_login(self) -> None:
        self.status_var.set("Inicializando login biometrico...")

        top_bar = tk.Frame(self.content_frame, bg="#1e293b")
        top_bar.pack(fill="x", pady=(0, 8))

        tk.Button(
            top_bar,
            text="Volver",
            font=("Segoe UI", 9, "bold"),
            bg="#0f172a",
            fg="#93c5fd",
            activebackground="#172554",
            activeforeground="#dbeafe",
            bd=0,
            cursor="hand2",
            command=lambda: self.transition_to(AppState.HOME),
        ).pack(side="left")

        self.camera_label = tk.Label(
            self.content_frame,
            bg="#020617",
            width=640,
            height=480,
            relief="solid",
            bd=1,
            highlightbackground="#334155",
            highlightthickness=1,
        )
        self.camera_label.pack(pady=8)

        self._start_login_flow()

    def _start_login_flow(self) -> None:
        self.login_use_case = LoginUseCase(
            auth_service=AuthService(SQLiteRepository()),
            matcher=FaceMatcherAdapter(),
            pkl_repository=PklRepository(),
            tolerance=self.recognition_settings.tolerance,
            cooldown_seconds=self.recognition_settings.access_cooldown_seconds,
        )
        self.login_use_case.initialize()
        self.known_encodings, self.known_labels, self.known_ids = self.login_use_case.load_known_students()

        if not self.known_encodings:
            self.status_var.set("No hay biometria registrada. Ve a Registro para comenzar.")
            return

        self.cap = open_camera()
        if self.cap is None:
            self.status_var.set("No se pudo acceder a la camara. Cierra otras apps e intenta de nuevo.")
            return

        self.status_var.set("Login activo. Presiona Volver para cerrar la camara.")
        self._update_login_frame()

    def _update_login_frame(self) -> None:
        if self.current_state != AppState.LOGIN or self.cap is None or self.login_use_case is None:
            return

        ok, frame = self.cap.read()
        if not ok:
            self.status_var.set("No se pudo leer el frame de camara.")
            self._stop_camera()
            return

        self.last_frame = frame.copy()

        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4))

        _, encodings = detect_face_encodings_from_frame(frame, scale=self.recognition_settings.scale)
        result = self.login_use_case.process_frame(
            encodings,
            self.known_encodings,
            self.known_labels,
            self.known_ids,
        )

        cv2.ellipse(frame, centro, ejes, 0, 0, 360, result.color, 2)
        cv2.rectangle(frame, (0, 0), (ancho, 40), (0, 0, 0), -1)
        cv2.putText(frame, result.message, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, result.color, 2)

        self._render_camera_frame(frame)
        self.status_var.set(result.message)
        self.camera_job = self.root.after(30, self._update_login_frame)

    def _render_registration(self) -> None:
        self.status_var.set("Completa los datos y captura tu rostro.")

        form = tk.Frame(self.content_frame, bg="#1e293b")
        form.pack(fill="x", pady=(0, 8))

        tk.Button(
            form,
            text="Volver",
            font=("Segoe UI", 9, "bold"),
            bg="#0f172a",
            fg="#93c5fd",
            activebackground="#172554",
            activeforeground="#dbeafe",
            bd=0,
            cursor="hand2",
            command=lambda: self.transition_to(AppState.HOME),
        ).grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="w")

        tk.Label(form, text="Nombre", bg="#1e293b", fg="white", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w")
        tk.Entry(form, textvariable=self.name_var, width=24).grid(row=1, column=1, padx=(8, 20), sticky="w")

        tk.Label(form, text="Grado", bg="#1e293b", fg="white", font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w")
        ttk.Combobox(form, textvariable=self.grade_var, values=["1", "2", "3"], width=5, state="readonly").grid(
            row=1, column=3, padx=(8, 20), sticky="w"
        )

        tk.Label(form, text="Grupo", bg="#1e293b", fg="white", font=("Segoe UI", 9)).grid(row=1, column=4, sticky="w")
        tk.Entry(form, textvariable=self.group_var, width=5).grid(row=1, column=5, padx=(8, 20), sticky="w")

        tk.Label(form, text="Turno", bg="#1e293b", fg="white", font=("Segoe UI", 9)).grid(row=1, column=6, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.shift_var,
            values=["MATUTINO", "VESPERTINO"],
            width=12,
            state="readonly",
        ).grid(row=1, column=7, padx=(8, 0), sticky="w")

        controls = tk.Frame(self.content_frame, bg="#1e293b")
        controls.pack(fill="x", pady=(0, 8))

        tk.Button(
            controls,
            text="Capturar y Guardar",
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="white",
            activebackground="#15803d",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            command=self.capture_registration,
        ).pack(side="left")

        self.camera_label = tk.Label(
            self.content_frame,
            bg="#020617",
            width=640,
            height=480,
            relief="solid",
            bd=1,
            highlightbackground="#334155",
            highlightthickness=1,
        )
        self.camera_label.pack(pady=8)

        self._start_registration_flow()

    def _start_registration_flow(self) -> None:
        self.registration_use_case = RegistrationUseCase(
            registration_service=RegistrationService(SQLiteRepository()),
            pkl_repository=PklRepository(),
        )
        self.registration_use_case.initialize()

        self.cap = open_camera()
        if self.cap is None:
            self.status_var.set("No se pudo acceder a la camara. Cierra otras apps e intenta de nuevo.")
            return

        self.status_var.set("Camara de registro activa. Presiona 'Capturar y Guardar'.")
        self._update_registration_frame()

    def _update_registration_frame(self) -> None:
        if self.current_state != AppState.REGISTRATION or self.cap is None:
            return

        ok, frame = self.cap.read()
        if not ok:
            self.status_var.set("No se pudo leer el frame de camara.")
            self._stop_camera()
            return

        self.last_frame = frame.copy()

        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4))

        cv2.ellipse(frame, centro, ejes, 0, 0, 360, (255, 255, 0), 2)
        cv2.putText(
            frame,
            "Encuadra tu rostro aqui",
            (centro[0] - 120, centro[1] - ejes[1] - 20),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            (255, 255, 0),
            1,
        )

        self._render_camera_frame(frame)
        self.camera_job = self.root.after(30, self._update_registration_frame)

    def capture_registration(self) -> None:
        if self.current_state != AppState.REGISTRATION or self.registration_use_case is None:
            return

        nombre = self.name_var.get().strip()
        grado_raw = self.grade_var.get().strip()
        letra = self.group_var.get().strip().upper()
        turno = self.shift_var.get().strip().upper()

        if not nombre:
            self.status_var.set("Dato invalido: el nombre es obligatorio.")
            return

        if grado_raw not in {"1", "2", "3"}:
            self.status_var.set("Dato invalido: el grado debe ser 1, 2 o 3.")
            return

        if len(letra) != 1 or not letra.isalpha():
            self.status_var.set("Dato invalido: el grupo debe ser una sola letra (A-Z).")
            return

        if turno not in {"MATUTINO", "VESPERTINO"}:
            self.status_var.set("Dato invalido: usa MATUTINO o VESPERTINO.")
            return

        if self.last_frame is None:
            self.status_var.set("Aun no hay imagen de camara para capturar.")
            return

        _, encodings = detect_face_encodings_from_frame(self.last_frame, scale=self.recognition_settings.scale)
        result = self.registration_use_case.register_from_detected_faces(
            nombre=nombre,
            grado=int(grado_raw),
            letra=letra,
            turno=turno,
            encodings=encodings,
        )
        self.status_var.set(result.message)

    def _render_camera_frame(self, frame_bgr) -> None:
        if self.camera_label is None:
            return

        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame_rgb)
        self.camera_photo = ImageTk.PhotoImage(image=image)
        self.camera_label.configure(image=self.camera_photo)

    def _stop_camera(self) -> None:
        if self.camera_job is not None:
            self.root.after_cancel(self.camera_job)
            self.camera_job = None

        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def on_close(self) -> None:
        self._stop_camera()
        self.root.destroy()
