import tkinter as tk
import threading
from login import login
from registrar import registrar_usuario

# =========================
# PALETA ALTA VISIBILIDAD
# (optimizada para luz solar directa)
# =========================
BG_MAIN      = "#F0F4FF"   # Fondo casi blanco con tinte frío
BG_CARD      = "#FFFFFF"   # Card blanca pura
BORDER       = "#C7D2FE"   # Borde azul suave visible
ACCENT       = "#4F46E5"   # Indigo intenso — excelente contraste sobre blanco
ACCENT_DARK  = "#3730A3"   # Hover del botón primario
BTN2_BG      = "#EEF2FF"   # Fondo botón secundario
BTN2_HOVER   = "#E0E7FF"
TEXT_TITLE   = "#1E1B4B"   # Casi negro violáceo — máximo contraste
TEXT_SUB     = "#4338CA"   # Azul fuerte — legible al sol
TEXT_FOOTER  = "#6366F1"
SEP_COLOR    = "#C7D2FE"
SHADOW       = "#A5B4FC"

# =========================
# FUNCIONES
# =========================


def ejecutar_login():
    login()

def ejecutar_registro():
    registrar_usuario()
# =========================
# VENTANA PRINCIPAL
# =========================
ventana = tk.Tk()
ventana.title("Sistema Facial")
ventana.geometry("460x800")
ventana.resizable(False, False)
ventana.configure(bg=BG_MAIN)

# ── Fondo con patrón de puntos (profundidad visual) ──────────────────────────
bg_canvas = tk.Canvas(ventana, width=460, height=800,
                      bg=BG_MAIN, highlightthickness=0)
bg_canvas.place(x=0, y=0)
for row in range(0, 800, 28):
    for col in range(0, 460, 28):
        bg_canvas.create_oval(col, row, col+3, row+3, fill=BORDER, outline="")

# ── Sombra del card (efecto de elevación) ────────────────────────────────────
shadow = tk.Frame(ventana, bg=SHADOW)
shadow.place(relx=0.5, rely=0.5, anchor="center",
             width=386, height=396)

# ── Card principal ────────────────────────────────────────────────────────────
card = tk.Frame(ventana, bg=BG_CARD,
                highlightbackground=BORDER, highlightthickness=2)
card.place(relx=0.5, rely=0.5, anchor="center", width=382, height=392)

# ── Banda superior de color (acento visual) ───────────────────────────────────
band = tk.Frame(card, bg=ACCENT, height=8)
band.pack(fill="x")

# ── Ícono / logo central ──────────────────────────────────────────────────────
icon_canvas = tk.Canvas(card, width=80, height=80,
                        bg=BG_CARD, highlightthickness=0)
icon_canvas.pack(pady=(22, 0))

# Círculo fondo icono
icon_canvas.create_oval(4, 4, 76, 76, fill=BTN2_BG, outline=ACCENT, width=2)
# Cara
icon_canvas.create_oval(18, 16, 62, 64, outline=ACCENT, width=2, fill="")
# Ojos
icon_canvas.create_oval(26, 30, 36, 40, fill=ACCENT, outline="")
icon_canvas.create_oval(44, 30, 54, 40, fill=ACCENT, outline="")
# Boca
icon_canvas.create_arc(26, 46, 54, 62, start=200, extent=140,
                       outline=ACCENT, width=2, style="arc")
# Marcadores de escaneo (esquinas)
scan_color = ACCENT_DARK
for x1, y1, x2, y2 in [(14, 12, 26, 12), (14, 12, 14, 24),
                         (54, 12, 66, 12), (66, 12, 66, 24),
                         (14, 56, 14, 68), (14, 68, 26, 68),
                         (54, 68, 66, 68), (66, 56, 66, 68)]:
    icon_canvas.create_line(x1, y1, x2, y2, fill=scan_color, width=2)

# ── Título ────────────────────────────────────────────────────────────────────
tk.Label(card,
         text="Sistema de Acceso",
         font=("Segoe UI", 19, "bold"),
         fg=TEXT_TITLE, bg=BG_CARD).pack(pady=(14, 0))

tk.Label(card,
         text="Reconocimiento Facial",
         font=("Segoe UI", 10, "bold"),
         fg=TEXT_SUB, bg=BG_CARD).pack()

# ── Separador ─────────────────────────────────────────────────────────────────
tk.Frame(card, bg=SEP_COLOR, height=2).pack(fill="x", padx=30, pady=20)

# ── Botón INICIAR SESIÓN ──────────────────────────────────────────────────────
btn_login = tk.Button(
    card,
    text="▶   Iniciar Sesión",
    font=("Segoe UI", 13, "bold"),
    width=22,
    height=2,
    bg=ACCENT,
    fg="white",
    activebackground=ACCENT_DARK,
    activeforeground="white",
    bd=0,
    cursor="hand2",
    command=ejecutar_login
)
btn_login.pack(pady=(0, 12), padx=30, fill="x")
btn_login.bind("<Enter>", lambda e: btn_login.config(bg=ACCENT_DARK))
btn_login.bind("<Leave>", lambda e: btn_login.config(bg=ACCENT))

# ── Botón REGISTRAR USUARIO ───────────────────────────────────────────────────
btn_registro = tk.Button(
    card,
    text="＋   Registrar Usuario",
    font=("Segoe UI", 13, "bold"),
    width=22,
    height=2,
    bg=BTN2_BG,
    fg=ACCENT,
    activebackground=BTN2_HOVER,
    activeforeground=ACCENT_DARK,
    bd=2,
    relief="solid",
    highlightbackground=ACCENT,
    highlightthickness=2,
    cursor="hand2",
    command=ejecutar_registro
)
btn_registro.pack(padx=30, fill="x")
btn_registro.bind("<Enter>", lambda e: btn_registro.config(bg=BTN2_HOVER))
btn_registro.bind("<Leave>", lambda e: btn_registro.config(bg=BTN2_BG))

# ── Banda inferior ────────────────────────────────────────────────────────────
tk.Frame(card, bg=BORDER, height=2).pack(fill="x", side="bottom")

# ── Footer ────────────────────────────────────────────────────────────────────
tk.Label(
    ventana,
    text="Sistema de Reconocimiento Facial  •  v1.0",
    font=("Segoe UI", 9, "bold"),
    fg=TEXT_FOOTER,
    bg=BG_MAIN
).pack(side="bottom", pady=14)

ventana.mainloop()