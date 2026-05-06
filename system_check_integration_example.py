#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejemplo de Integración - System Check + FaceLoginUI

Este archivo muestra cómo integrar el nuevo SystemCheckUI con la interfaz
de login facial existente.
"""

import tkinter as tk
from test_setup import SystemCheckUI


class FaceLoginUI(tk.Tk):
    """
    Interfaz de login con reconocimiento facial.
    
    Esta es una clase de ejemplo que debería reemplazar o complementar
    la clase login_ui.py existente.
    """
    
    def __init__(self):
        super().__init__()
        self.title("Sistema de Acceso Facial - Login")
        self.geometry("600x500")
        self.configure(bg="#f5f5f5")
        
        # Crear la interfaz principal
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de la interfaz de login."""
        # Frame principal
        main_frame = tk.Frame(self, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = tk.Label(
            main_frame,
            text="Sistema de Acceso Facial",
            font=("Segoe UI", 18, "bold"),
            bg="#f5f5f5",
            fg="#333333"
        )
        title.pack(pady=20)
        
        # Mensaje de bienvenida
        msg = tk.Label(
            main_frame,
            text="El sistema está verificado y listo para usar.",
            font=("Segoe UI", 12),
            bg="#f5f5f5",
            fg="#666666"
        )
        msg.pack(pady=10)
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg="#f5f5f5")
        btn_frame.pack(pady=30)
        
        start_btn = tk.Button(
            btn_frame,
            text="Iniciar Cámara",
            font=("Segoe UI", 11, "bold"),
            bg="#1f5b9f",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._start_camera
        )
        start_btn.pack(pady=5)
        
        exit_btn = tk.Button(
            btn_frame,
            text="Salir",
            font=("Segoe UI", 11),
            bg="#e0e0e0",
            fg="#333333",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.quit
        )
        exit_btn.pack(pady=5)
    
    def _start_camera(self):
        """Inicia la interfaz de captura de cámara."""
        # TODO: Implementar la interfaz de cámara
        import tkinter.messagebox as messagebox
        messagebox.showinfo(
            "Cámara",
            "Función de cámara a implementar.\n"
            "Aquí iría la interfaz de captura y reconocimiento facial."
        )


def main():
    """
    Punto de entrada alternativo que ejecuta la verificación primero.
    
    Opciones:
    1. Ejecutar verificación y luego UI principal
    2. Ejecutar directamente FaceLoginUI
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--skip-check":
        # Saltar verificación
        print("Saltando verificación de sistema...")
        app = FaceLoginUI()
        app.mainloop()
    else:
        # Ejecutar verificación primero
        print("Iniciando verificación del sistema...")
        app = SystemCheckUI()
        app.mainloop()


if __name__ == "__main__":
    main()
