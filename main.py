import tkinter as tk
import threading
from login import login
from registrar import registrar_usuario

# =========================
# FUNCIONES
# =========================
def ejecutar_login():
    threading.Thread(target=login, daemon=True).start()

def ejecutar_registro():
    threading.Thread(target=registrar_usuario, daemon=True).start()

# =========================
# INTERFAZ
# =========================
ventana = tk.Tk()
ventana.title("Sistema Facial")
ventana.geometry("460x800")
ventana.resizable(False, False)
ventana.configure(bg="#0f172a")

# CONTENEDOR
frame = tk.Frame(ventana, bg="#1e293b",
                 highlightbackground="#334155",
                 highlightthickness=1)
frame.place(relx=0.5, rely=0.5, anchor="center", width=380, height=310)

# TÍTULO
tk.Label(
    frame,
    text="Sistema de Acceso Facial",
    font=("Segoe UI", 17, "bold"),
    fg="white",
    bg="#1e293b"
).pack(pady=(28, 4))

# SUBTÍTULO
tk.Label(
    frame,
    text="Reconocimiento facial",
    font=("Segoe UI", 9),
    fg="#64748b",
    bg="#1e293b"
).pack()

# SEPARADOR
sep = tk.Frame(frame, bg="#334155", height=1)
sep.pack(fill="x", padx=30, pady=18)

# BOTÓN LOGIN
btn_login = tk.Button(
    frame,
    text="Iniciar Sesión",
    font=("Segoe UI", 11, "bold"),
    width=22,
    height=2,
    bg="#7C3AED",
    fg="white",
    activebackground="#5B21B6",
    activeforeground="white",
    bd=0,
    cursor="hand2",
    command=ejecutar_login
)
btn_login.pack(pady=(0, 10))
btn_login.bind("<Enter>", lambda e: btn_login.config(bg="#5B21B6"))
btn_login.bind("<Leave>", lambda e: btn_login.config(bg="#7C3AED"))

# BOTÓN REGISTRO
btn_registro = tk.Button(
    frame,
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
    command=ejecutar_registro
)
btn_registro.pack()
btn_registro.bind("<Enter>", lambda e: btn_registro.config(bg="#0f172a"))
btn_registro.bind("<Leave>", lambda e: btn_registro.config(bg="#1e293b"))

# FOOTER
tk.Label(
    ventana,
    text="Sistema de Reconocimiento Facial",
    font=("Segoe UI", 9),
    fg="#334155",
    bg="#0f172a"
).pack(side="bottom", pady=12)

ventana.mainloop()