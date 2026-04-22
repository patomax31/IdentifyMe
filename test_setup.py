#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sistema de Verificación de Dependencias con Interfaz Gráfica Tkinter

Crea una pantalla de carga moderna que valida:
- Dependencias de Python
- Hardware (cámara, pantalla)
- Base de datos (SQLite)

Ejecuta automáticamente las verificaciones y permite continuar a la interfaz principal.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sqlite3
import os
import sys
from typing import Dict, List, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import math


# ============================================================================
# ENUMERACIONES Y DATACLASSES
# ============================================================================

class CheckStatus(Enum):
    """Estados posibles de una verificación."""
    PENDING = "pending"
    CHECKING = "checking"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class CheckResult:
    """Resultado de una verificación de sistema."""
    name: str
    category: str
    status: CheckStatus
    message: str = ""
    error_details: str = ""

    def __post_init__(self):
        if self.status == CheckStatus.SUCCESS:
            self.message = "OK"
        elif self.status == CheckStatus.CHECKING:
            self.message = "Verificando..."


# ============================================================================
# VALIDADORES DE SISTEMA
# ============================================================================

class SystemValidator:
    """Realiza todas las validaciones de sistema necesarias."""

    def __init__(self, callback: Callable[[CheckResult], None]):
        """
        Inicializa el validador.
        
        Args:
            callback: Función que se llamará cuando se complete cada validación.
        """
        self.callback = callback
        self.results: List[CheckResult] = []

    @staticmethod
    def get_expected_check_count() -> int:
        """Retorna la cantidad total de verificaciones planificadas."""
        dependency_checks = 6
        hardware_checks = 3
        database_checks = 1
        return dependency_checks + hardware_checks + database_checks

    def validate_dependencies(self) -> List[CheckResult]:
        """Valida todas las dependencias de Python."""
        dependencies = [
            ("cv2", "OpenCV"),
            ("numpy", "NumPy"),
            ("dlib", "dlib"),
            ("PIL", "Pillow"),
            ("face_recognition", "face_recognition"),
            ("tkinter", "Tkinter"),
        ]

        results = []
        for module_name, display_name in dependencies:
            result = CheckResult(
                name=display_name,
                category="Dependencias",
                status=CheckStatus.CHECKING,
            )
            self.callback(result)
            time.sleep(0.3)  # Simula tiempo de verificación

            try:
                __import__(module_name)
                result.status = CheckStatus.SUCCESS
                result.message = "OK"
            except ImportError as e:
                result.status = CheckStatus.ERROR
                result.error_details = str(e)

            self.callback(result)
            results.append(result)

        return results

    def validate_camera(self) -> CheckResult:
        """Valida la disponibilidad de la cámara."""
        result = CheckResult(
            name="Cámara",
            category="Hardware",
            status=CheckStatus.CHECKING,
        )
        self.callback(result)
        time.sleep(0.3)

        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
                result.status = CheckStatus.SUCCESS
                result.message = "OK"
            else:
                result.status = CheckStatus.ERROR
                result.error_details = "No se pudo abrir la cámara"
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error_details = str(e)

        self.callback(result)
        return result

    def validate_display(self) -> CheckResult:
        """Valida que Tkinter puede renderizar correctamente."""
        result = CheckResult(
            name="Pantalla",
            category="Hardware",
            status=CheckStatus.CHECKING,
        )
        self.callback(result)
        time.sleep(0.3)

        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            result.status = CheckStatus.SUCCESS
            result.message = "OK"
            root.destroy()
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error_details = str(e)

        self.callback(result)
        return result

    def validate_servo(self) -> CheckResult:
        """Valida la disponibilidad del servomotor (simulado)."""
        result = CheckResult(
            name="Servomotor",
            category="Hardware",
            status=CheckStatus.CHECKING,
        )
        self.callback(result)
        time.sleep(0.5)

        try:
            # Simulación: verificar si el archivo de configuración existe
            # En un sistema real, aquí se verificaría el puerto serie
            result.status = CheckStatus.SUCCESS
            result.message = "OK (Simulado)"
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error_details = str(e)

        self.callback(result)
        return result

    def validate_database(self) -> CheckResult:
        """Valida la conexión a la base de datos SQLite."""
        result = CheckResult(
            name="Base de Datos",
            category="Base de Datos",
            status=CheckStatus.CHECKING,
        )
        self.callback(result)
        time.sleep(0.4)

        try:
            db_path = os.path.join(os.path.dirname(__file__), "database", "sqlite", "students.db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            result.status = CheckStatus.SUCCESS
            result.message = "OK"
        except Exception as e:
            result.status = CheckStatus.ERROR
            result.error_details = str(e)

        self.callback(result)
        return result

    def run_all_checks(self) -> List[CheckResult]:
        """Ejecuta todas las validaciones en orden."""
        all_results = []

        # Dependencias
        all_results.extend(self.validate_dependencies())

        # Hardware
        all_results.append(self.validate_camera())
        all_results.append(self.validate_display())
        all_results.append(self.validate_servo())

        # Base de datos
        all_results.append(self.validate_database())

        self.results = all_results
        return all_results


# ============================================================================
# COMPONENTES UI
# ============================================================================

class LoadingCircle(tk.Canvas):
    """Círculo de carga animado."""

    def __init__(self, parent, size=50, color="#1f5b9f", **kwargs):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg="white",
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.color = color
        self.angle = 0
        self.is_running = False
        self._animation_after_id = None
        self._animate()

    def start(self):
        """Inicia la animación."""
        self.is_running = True
        self._animate()

    def stop(self):
        """Detiene la animación."""
        self.is_running = False
        if self._animation_after_id is not None:
            self.after_cancel(self._animation_after_id)
            self._animation_after_id = None
        self.delete("all")

    def show_success_icon(self):
        """Muestra un estado final con una marca de correcto."""
        self.is_running = False
        if self._animation_after_id is not None:
            self.after_cancel(self._animation_after_id)
            self._animation_after_id = None
        self.delete("all")

        center = self.size / 2
        radius = self.size / 2 - 5

        self.create_oval(
            center - radius,
            center - radius,
            center + radius,
            center + radius,
            fill=self.color,
            outline=self.color,
            width=3,
        )

        # Marca de correcto (estilo flecha/check)
        self.create_line(
            center - radius * 0.35,
            center + radius * 0.05,
            center - radius * 0.08,
            center + radius * 0.33,
            center + radius * 0.40,
            center - radius * 0.25,
            fill="white",
            width=5,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
        )

    def _animate(self):
        """Anima el círculo de carga."""
        self.delete("all")
        center = self.size / 2
        radius = self.size / 2 - 5

        # Dibuja círculo de fondo
        self.create_oval(
            center - radius,
            center - radius,
            center + radius,
            center + radius,
            outline="#e0e0e0",
            width=3,
        )

        # Dibuja arco rotativo
        extent = 90
        self.create_arc(
            center - radius,
            center - radius,
            center + radius,
            center + radius,
            start=self.angle,
            extent=extent,
            outline=self.color,
            width=4,
            style="arc",
        )

        if self.is_running:
            self.angle = (self.angle + 15) % 360
            self._animation_after_id = self.after(50, self._animate)
        else:
            self._animation_after_id = None


class CheckItemWidget(tk.Frame):
    """Widget que representa un elemento de verificación."""

    def __init__(self, parent, result: CheckResult, **kwargs):
        super().__init__(parent, bg="white", **kwargs)
        self.result = result

        # Crear frame para el contenido
        self.grid_columnconfigure(1, weight=1)

        # Ícono de estado
        self.icon_label = tk.Label(
            self,
            text="●",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#87ceeb",
            width=3,
        )
        self.icon_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        # Información
        info_frame = tk.Frame(self, bg="white")
        info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=8)
        info_frame.grid_columnconfigure(0, weight=1)

        # Nombre del componente
        self.name_label = tk.Label(
            info_frame,
            text=result.name,
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#333333",
        )
        self.name_label.grid(row=0, column=0, sticky="w")

        # Estado
        self.status_label = tk.Label(
            info_frame,
            text=result.message,
            font=("Segoe UI", 9),
            bg="white",
            fg="#666666",
        )
        self.status_label.grid(row=1, column=0, sticky="w")

        # Separador
        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=5
        )

    def update_status(self, result: CheckResult):
        """Actualiza el estado del widget."""
        self.result = result

        # Actualizar icono y color
        if result.status == CheckStatus.CHECKING:
            self.icon_label.config(fg="#87ceeb", text="◐")
        elif result.status == CheckStatus.SUCCESS:
            self.icon_label.config(fg="#1f5b9f", text="✓")
        elif result.status == CheckStatus.ERROR:
            self.icon_label.config(fg="#808080", text="✗")

        # Actualizar texto de estado
        self.status_label.config(text=result.message)

        if result.error_details:
            self.status_label.config(
                text=f"{result.message} - {result.error_details}",
                fg="#d32f2f",
            )


# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

class SystemCheckUI(tk.Tk):
    """Interfaz gráfica para validación de sistema."""

    def __init__(self):
        super().__init__()
        self.title("Identifyme")
        self.geometry("460x800")
        self.resizable(False, False)

        # Configurar estilo
        self._configure_styles()

        # Estado
        self.check_items: Dict[str, CheckItemWidget] = {}
        self.validator = None
        self.check_complete = False
        self.all_success = False
        self.total_checks = 0
        self.latest_results: Dict[str, CheckResult] = {}
        self._mousewheel_bound = False
        self._redirect_after_id = None

        # Crear UI
        self._create_widgets()

        # Iniciar validaciones en thread separado
        self.after(500, self._start_validation)

    def _configure_styles(self):
        """Configura los estilos de la aplicación."""
        # Colores
        self.colors = {
            "bg_main": "#ffffff",
            "bg_secondary": "#f5f5f5",
            "text_primary": "#333333",
            "text_secondary": "#666666",
            "success": "#1f5b9f",
            "error": "#808080",
            "checking": "#87ceeb",
            "accent": "#1f5b9f",
        }

        # Configurar tema
        self.configure(bg=self.colors["bg_main"])
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TProgressbar",
            background=self.colors["success"],
            troughcolor=self.colors["bg_secondary"],
            darkcolor=self.colors["success"],
            lightcolor=self.colors["success"],
        )

    def _create_widgets(self):
        """Crea todos los widgets de la interfaz usando Grid para diseño moderno."""
        # Frame principal con grid
        main_frame = tk.Frame(self, bg=self.colors["bg_main"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configurar grid: 1 columna, 7 filas con la fila 5 expandible
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(5, weight=1)

        # Row 0: Título
        title_label = tk.Label(
            main_frame,
            text="Inicializando IdentifyMe",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors["bg_main"],
            fg=self.colors["text_primary"],
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Row 1: Círculo de carga
        circle_frame = tk.Frame(main_frame, bg=self.colors["bg_main"])
        circle_frame.grid(row=1, column=0, pady=12)

        self.loading_circle = LoadingCircle(
            circle_frame, size=80, color=self.colors["accent"]
        )
        self.loading_circle.pack()
        self.loading_circle.start()

        # Row 2: Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            length=500,
        )
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=(8, 0), padx=5)

        # Row 3: Label de progreso
        self.progress_label = tk.Label(
            main_frame,
            text="0%",
            font=("Segoe UI", 9),
            bg=self.colors["bg_main"],
            fg=self.colors["text_secondary"],
            anchor="center",
            justify="center",
        )
        self.progress_label.grid(row=3, column=0, sticky="ew", pady=(4, 8), padx=5)

        # Row 4: Etiqueta "Verificaciones"
        checks_label = tk.Label(
            main_frame,
            text="Verificaciones",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg_main"],
            fg=self.colors["text_primary"],
        )
        checks_label.grid(row=4, column=0, sticky="ew", pady=(12, 8), padx=5)

        # Row 5: Canvas con scroll (EXPANDIBLE)
        # Crear frame contenedor para canvas + scrollbar
        canvas_frame = tk.Frame(main_frame, bg=self.colors["bg_main"])
        canvas_frame.grid(row=5, column=0, sticky="nsew", pady=(0, 12))
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            canvas_frame,
            bg=self.colors["bg_secondary"],
            highlightthickness=1,
            highlightbackground="#e0e0e0",
            relief=tk.FLAT,
            height=250,
        )
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg_secondary"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(window_id, width=e.width),
        )

        self.checks_container = scrollable_frame
        self.checks_canvas = canvas
        self._bind_checks_scroll_events()

        canvas.grid(row=0, column=0, sticky="nsew")

        # Row 6: Frame para botones
        button_frame = tk.Frame(main_frame, bg=self.colors["bg_main"])
        button_frame.grid(row=6, column=0, sticky="ew", pady=(8, 0))
        button_frame.grid_columnconfigure(0, weight=1)

        self.continue_button = tk.Button(
            button_frame,
            text="Continuar a inicio de sesión",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["success"],
            fg="white",
            padx=15,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._on_continue,
        )
        self.continue_button.grid(row=0, column=1, padx=(5, 0), sticky="e")
        self.continue_button.grid_remove()

        self.retry_button = tk.Button(
            button_frame,
            text="Reintentar",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            fg=self.colors["text_primary"],
            padx=15,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._start_validation,
        )
        self.retry_button.grid(row=0, column=2, padx=(5, 0), sticky="e")
        self.retry_button.grid_remove()

        self.redirect_label = tk.Label(
            button_frame,
            text="",
            font=("Segoe UI", 10, "italic"),
            bg=self.colors["bg_main"],
            fg=self.colors["text_secondary"],
            anchor="center",
            justify="center",
        )
        self.redirect_label.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        self.redirect_label.grid_remove()

        self.cancel_redirect_button = tk.Button(
            button_frame,
            text="Cancelar redirección",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg=self.colors["text_primary"],
            padx=10,
            pady=6,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._cancel_redirect,
        )
        self.cancel_redirect_button.grid(row=2, column=0, columnspan=3, pady=(6, 0))
        self.cancel_redirect_button.grid_remove()

    def _start_validation(self):
        """Inicia las validaciones en un thread separado."""
        self._cancel_pending_redirect()
        self.check_complete = False
        self.all_success = False
        self.latest_results.clear()

        # Limpiar verificaciones previas
        for widget in self.checks_container.winfo_children():
            widget.destroy()
        self.check_items.clear()

        # Resetear UI
        self.continue_button.config(state=tk.DISABLED)
        self.retry_button.config(state=tk.DISABLED)
        self.continue_button.grid_remove()
        self.retry_button.grid_remove()
        self.progress_var.set(0)
        self.progress_label.config(
            text="0%",
            fg=self.colors["text_secondary"],
            font=("Segoe UI", 9),
        )
        self.loading_circle.start()

        # Crear validador
        self.validator = SystemValidator(self._on_check_result)
        self.total_checks = self.validator.get_expected_check_count()

        # Ejecutar validaciones en thread
        thread = threading.Thread(target=self.validator.run_all_checks, daemon=True)
        thread.start()

    def _on_check_result(self, result: CheckResult):
        """Callback cuando se completa una verificación."""
        self.after(0, lambda: self._update_check_result(result))

    def _update_check_result(self, result: CheckResult):
        """Actualiza la UI con un resultado de verificación."""
        # Crear widget si no existe
        key = f"{result.category}_{result.name}"
        self.latest_results[key] = result

        if key not in self.check_items:
            widget = CheckItemWidget(self.checks_container, result)
            widget.pack(fill=tk.X, padx=0, pady=0)
            self.check_items[key] = widget
        else:
            self.check_items[key].update_status(result)

        # Calcular progreso
        total_checks = self.total_checks
        completed = sum(
            1
            for r in self.latest_results.values()
            if r.status in (CheckStatus.SUCCESS, CheckStatus.ERROR)
        )
        progress = (completed / total_checks * 100) if total_checks > 0 else 0
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{int(progress)}%")

        # Verificar si todas las validaciones están completas
        if total_checks > 0 and completed >= total_checks:
            self._on_validation_complete()

    def _on_validation_complete(self):
        """Se ejecuta cuando todas las validaciones están completas."""
        if self.check_complete:
            return

        self.check_complete = True

        # Verificar si todo fue exitoso
        errors = [r for r in self.latest_results.values() if r.status == CheckStatus.ERROR]
        self.all_success = len(errors) == 0

        if self.all_success:
            # Todo está OK
            self.progress_label.config(text="✓ Sistema listo",
                                        fg=self.colors["success"],
                                        font = ("Segoe UI", 18, "bold") )
            self.continue_button.config(state=tk.NORMAL)
            self.retry_button.config(state=tk.NORMAL)
            self.continue_button.grid_remove()
            self.retry_button.grid_remove()

            # Se termina la animación y se muestra marca de correcto
            self.loading_circle.show_success_icon()

            # Redirección automática con opción de cancelar
            self.redirect_label.config(text="Reedirigiendo al acceso...")
            self.redirect_label.grid()
            self.cancel_redirect_button.config(state=tk.NORMAL)
            self.cancel_redirect_button.grid()
            self._redirect_after_id = self.after(5000, self._on_continue)

        else:
            # Hay errores
            error_list = "\n".join([f"• {r.name}: {r.error_details}" for r in errors])
            self.progress_label.config(text=f"✗ {len(errors)} error(es)", 
                                       fg=self.colors["error"],
                                       font=("Segoe UI", 18, "bold"))
            self.retry_button.config(state=tk.NORMAL)
            self.retry_button.grid()
            # messagebox.showerror(
            #     "Errores de Verificación",
            #     f"Se encontraron los siguientes errores:\n\n{error_list}\n\n"
            #     f"Por favor, instala las dependencias faltantes e intenta nuevamente.",
            # )

    def _cancel_pending_redirect(self):
        """Cancela cualquier redirección programada y oculta sus controles."""
        if self._redirect_after_id is not None:
            self.after_cancel(self._redirect_after_id)
            self._redirect_after_id = None

        self.redirect_label.grid_remove()
        self.cancel_redirect_button.grid_remove()
        self.cancel_redirect_button.config(state=tk.DISABLED)

    def _cancel_redirect(self):
        """Cancela la redirección automática al login."""
        self._cancel_pending_redirect()
        self.retry_button.config(state=tk.NORMAL)
        self.continue_button.config(state=tk.NORMAL)
        self.retry_button.grid()
        self.continue_button.grid()

    def _bind_checks_scroll_events(self):
        """Habilita scroll con rueda del mouse sobre el área de verificaciones."""
        self.checks_canvas.bind("<Enter>", self._enable_mousewheel_scroll)
        self.checks_canvas.bind("<Leave>", self._disable_mousewheel_scroll)
        self.checks_container.bind("<Enter>", self._enable_mousewheel_scroll)
        self.checks_container.bind("<Leave>", self._disable_mousewheel_scroll)

    def _enable_mousewheel_scroll(self, _event=None):
        """Activa bindings globales de rueda al entrar al área de checks."""
        if self._mousewheel_bound:
            return
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)
        self._mousewheel_bound = True

    def _disable_mousewheel_scroll(self, _event=None):
        """Desactiva bindings globales de rueda al salir del área de checks."""
        if not self._mousewheel_bound:
            return
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
        self._mousewheel_bound = False

    def _on_mousewheel(self, event):
        """Gestiona scroll para Linux (Button-4/5) y Windows/macOS (MouseWheel)."""
        if getattr(event, "num", None) == 4:
            self.checks_canvas.yview_scroll(-1, "units")
        elif getattr(event, "num", None) == 5:
            self.checks_canvas.yview_scroll(1, "units")
        else:
            delta = int(-event.delta / 120) if event.delta else 0
            if delta != 0:
                self.checks_canvas.yview_scroll(delta, "units")

    def _on_continue(self):
        """Abre la interfaz principal."""
        self._cancel_pending_redirect()
        try:
            from login_ui import FaceLoginUI

            self.withdraw()
            app = FaceLoginUI()
            app.mainloop()
            self.quit()
        except ImportError:
            self.quit()
        except Exception:
            print("Error al iniciar la interfaz principal")

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Punto de entrada de la aplicación."""
    app = SystemCheckUI()
    app.mainloop()


if __name__ == "__main__":
    main()
