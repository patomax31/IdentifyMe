import tkinter as tk
from login import login

# =========================
# COLORES
# =========================
BG_MAIN      = "#F0F4FF"
BG_CARD      = "#FFFFFF"
BORDER       = "#C7D2FE"
ACCENT       = "#4F46E5"
ACCENT_DARK  = "#3730A3"
BTN2_BG      = "#EEF2FF"
BTN2_HOVER   = "#E0E7FF"
TEXT_TITLE   = "#1E1B4B"
TEXT_SUB     = "#4338CA"
TEXT_FOOTER  = "#6366F1"
SEP_COLOR    = "#C7D2FE"
SHADOW       = "#A5B4FC"

# =========================
# FUNCIONES
# =========================

def ejecutar_login():
    login()

def ejecutar_registro():
    print("Aquí puedes conectar tu módulo de registro")

# =========================
# VENTANA PRINCIPAL
# =========================
ventana = tk.Tk()
ventana.title("Sistema Facial")
ventana.geometry("460x800")
ventana.resizable(False, False)
ventana.configure(bg=BG_MAIN)

bg_canvas = tk.Canvas(ventana, width=460, height=800,
                      bg=BG_MAIN, highlightthickness=0)
bg_canvas.place(x=0, y=0)

for row in range(0, 800, 28):
    for col in range(0, 460, 28):
        bg_canvas.create_oval(col, row, col+3, row+3, fill=BORDER, outline="")

shadow = tk.Frame(ventana, bg=SHADOW)
shadow.place(relx=0.5, rely=0.5, anchor="center",
             width=386, height=396)

card = tk.Frame(ventana, bg=BG_CARD,
                highlightbackground=BORDER, highlightthickness=2)
card.place(relx=0.5, rely=0.5, anchor="center", width=382, height=392)

band = tk.Frame(card, bg=ACCENT, height=8)
band.pack(fill="x")

tk.Label(card,
         text="Sistema de Acceso",
         font=("Segoe UI", 19, "bold"),
         fg=TEXT_TITLE, bg=BG_CARD).pack(pady=(30, 0))

tk.Label(card,
         text="Reconocimiento Facial",
         font=("Segoe UI", 10, "bold"),
         fg=TEXT_SUB, bg=BG_CARD).pack()

tk.Frame(card, bg=SEP_COLOR, height=2).pack(fill="x", padx=30, pady=20)

btn_login = tk.Button(
    card,
    text="▶   Iniciar Sesión",
    font=("Segoe UI", 13, "bold"),
    height=2,
    bg=ACCENT,
    fg="white",
    activebackground=ACCENT_DARK,
    bd=0,
    cursor="hand2",
    command=ejecutar_login
)
btn_login.pack(pady=(0, 12), padx=30, fill="x")

btn_registro = tk.Button(
    card,
    text="＋   Registrar Usuario",
    font=("Segoe UI", 13, "bold"),
    height=2,
    bg=BTN2_BG,
    fg=ACCENT,
    activebackground=BTN2_HOVER,
    bd=2,
    relief="solid",
    cursor="hand2",
    command=ejecutar_registro
)
btn_registro.pack(padx=30, fill="x")

tk.Label(
    ventana,
    text="Sistema de Reconocimiento Facial • v1.0",
    font=("Segoe UI", 9, "bold"),
    fg=TEXT_FOOTER,
    bg=BG_MAIN
).pack(side="bottom", pady=14)

ventana.mainloop()