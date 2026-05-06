<<<<<<< HEAD
import tkinter as tk
from tkinter import ttk, messagebox
import threading, cv2, os, pickle
from PIL import Image, ImageTk
import winsound
=======
import cv2
from typing import Callable, Optional
>>>>>>> 7b8e1a289254b37d3144b741d98017de8259c97a

from src.application.registration_service import RegistrationService
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import encode_single_face_from_frame

# ══════════════════════════════════════════════════════════════
#  PALETA — Alta visibilidad (pantalla al sol, 480×800)
# ══════════════════════════════════════════════════════════════
BG          = "#F0F4FF"
CARD        = "#FFFFFF"
ACC         = "#3730A3"   # Indigo oscuro — contraste máximo
ACC2        = "#6D28D9"   # Violeta acento
ACC_LITE    = "#E0E7FF"
ACC_HOV     = "#312E81"
BORDER      = "#818CF8"
SEP         = "#C7D2FE"
SUCCESS     = "#065F46";  SUCCESS_BG = "#D1FAE5"
WARN        = "#92400E";  WARN_BG    = "#FEF3C7"
ERROR       = "#991B1B";  ERROR_BG   = "#FEE2E2"
INFO        = "#1E40AF";  INFO_BG    = "#DBEAFE"
TXT         = "#1E1B4B"
TXT_LBL     = "#312E81"
TXT_MUTE    = "#4338CA"

FONT_TITLE  = ("Trebuchet MS", 13, "bold")
FONT_LBL    = ("Trebuchet MS", 9,  "bold")
FONT_ENTRY  = ("Consolas",    11)
FONT_BTN    = ("Trebuchet MS", 11, "bold")
FONT_HINT   = ("Trebuchet MS",  8)
FONT_BADGE  = ("Consolas",     8,  "bold")


<<<<<<< HEAD
def registrar_usuario():
    service = RegistrationService(SQLiteRepository())
    service.initialize()
    os.makedirs('data', exist_ok=True)

    cap     = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    latest  = {'frame': None}
    running = {'ok': True}
    face_data = {'frames': 0, 'encoding': None, 'captured': False, 'countdown': 0}

    # ══════════════════════════════════════════════════════════
    #  VENTANA ÚNICA — 480 × 800
    # ══════════════════════════════════════════════════════════
    win = tk.Toplevel()
    win.title("Registro Facial")
    win.geometry("480x800")
    win.resizable(False, False)
    win.configure(bg=BG)

    # ── Fondo decorativo ──────────────────────────────────────
    bg_c = tk.Canvas(win, width=480, height=800, bg=BG, highlightthickness=0)
    bg_c.place(x=0, y=0)
    for r in range(0, 800, 26):
        for c in range(0, 480, 26):
            bg_c.create_oval(c, r, c+3, r+3, fill=SEP, outline="")

    # ══════════════════════════════════════════════════════════
    #  HEADER
    # ══════════════════════════════════════════════════════════
    hdr = tk.Frame(win, bg=ACC, height=56)
    hdr.place(x=0, y=0, width=480, height=56)

    tk.Label(hdr, text="👤  REGISTRO FACIAL",
             font=FONT_TITLE, fg="white", bg=ACC
             ).place(relx=0.5, rely=0.45, anchor="center")

    # Franja inferior del header
    tk.Frame(win, bg=ACC2, height=4).place(x=0, y=56, width=480, height=4)

    # ══════════════════════════════════════════════════════════
    #  VISOR DE CÁMARA  (card elevada)
    # ══════════════════════════════════════════════════════════
    # Sombra
    tk.Frame(win, bg=BORDER).place(x=14, y=68, width=454, height=306)
    # Card
    cam_card = tk.Frame(win, bg=CARD, highlightbackground=BORDER, highlightthickness=2)
    cam_card.place(x=12, y=66, width=454, height=304)

    # Mini-header del visor
    cam_top = tk.Frame(cam_card, bg=ACC, height=28)
    cam_top.pack(fill="x")
    cam_top.pack_propagate(False)
    tk.Label(cam_top, text="● LIVE",
             font=FONT_BADGE, fg="#FCA5A5", bg=ACC).place(x=10, rely=0.5, anchor="w")
    cam_title = tk.Label(cam_top, text="Cámara encuadra tu rostro",
                         font=FONT_HINT, fg=SEP, bg=ACC)
    cam_title.place(relx=0.5, rely=0.5, anchor="center")

    # Canvas de la cámara — fondo oscuro para contrastar el feed
    cam_lbl = tk.Label(cam_card, bg="#0F172A")
    cam_lbl.pack(fill="both", expand=True, padx=6, pady=(4, 0))

    # Barra de estado del visor
    cam_bar = tk.Frame(cam_card, bg=INFO_BG, height=26)
    cam_bar.pack(fill="x")
    cam_bar.pack_propagate(False)
    cam_hint_lbl = tk.Label(cam_bar,
                             text="Coloca tu rostro dentro del óvalo",
                             font=FONT_HINT, fg=INFO, bg=INFO_BG)
    cam_hint_lbl.place(relx=0.5, rely=0.5, anchor="center")

    # ══════════════════════════════════════════════════════════
    #  PASTILLA DE PROGRESO (3 pasos visuales)
    # ══════════════════════════════════════════════════════════
    steps_frame = tk.Frame(win, bg=BG)
    steps_frame.place(x=12, y=376, width=454, height=40)

    step_labels  = []
    step_circles = []
    step_texts   = ["Escanear", "Completar", "Registrar"]

    for i, txt in enumerate(step_texts):
        col = tk.Frame(steps_frame, bg=BG)
        col.place(relx=(i * 0.33) + 0.165, rely=0.5, anchor="center")

        circ = tk.Canvas(col, width=28, height=28, bg=BG, highlightthickness=0)
        circ.pack()
        circ.create_oval(2, 2, 26, 26, fill=SEP, outline=BORDER, width=2)
        circ.create_text(14, 14, text=str(i+1),
                         font=("Consolas", 9, "bold"), fill=TXT_LBL)
        step_circles.append(circ)

        lbl = tk.Label(col, text=txt, font=("Trebuchet MS", 7, "bold"),
                       fg=TXT_MUTE, bg=BG)
        lbl.pack()
        step_labels.append(lbl)

        # Línea conectora
        if i < 2:
            tk.Frame(steps_frame, bg=SEP, height=2).place(
                relx=(i * 0.33) + 0.33, rely=0.35, anchor="center",
                width=60, height=2
            )

    def set_step(n):
        """Resalta el paso activo (0-based)."""
        for i, circ in enumerate(step_circles):
            circ.delete("all")
            if i < n:
                circ.create_oval(2, 2, 26, 26, fill=SUCCESS, outline=SUCCESS, width=2)
                circ.create_text(14, 14, text="✓", font=("Consolas", 9, "bold"), fill="white")
                step_labels[i].config(fg=SUCCESS)
            elif i == n:
                circ.create_oval(2, 2, 26, 26, fill=ACC, outline=ACC, width=2)
                circ.create_text(14, 14, text=str(i+1),
                                 font=("Consolas", 9, "bold"), fill="white")
                step_labels[i].config(fg=ACC)
            else:
                circ.create_oval(2, 2, 26, 26, fill=SEP, outline=BORDER, width=2)
                circ.create_text(14, 14, text=str(i+1),
                                 font=("Consolas", 9, "bold"), fill=TXT_LBL)
                step_labels[i].config(fg=TXT_MUTE)

    set_step(0)

    # ══════════════════════════════════════════════════════════
    #  FORMULARIO  (card debajo del visor)
    # ══════════════════════════════════════════════════════════
    # Sombra
    tk.Frame(win, bg=BORDER).place(x=14, y=424, width=454, height=316)
    # Card
    form_card = tk.Frame(win, bg=CARD, highlightbackground=BORDER, highlightthickness=2)
    form_card.place(x=12, y=422, width=454, height=314)

    # Mini-header formulario
    form_top = tk.Frame(form_card, bg=ACC2, height=28)
    form_top.pack(fill="x")
    form_top.pack_propagate(False)
    tk.Label(form_top, text="📋  Datos del Estudiante",
             font=FONT_HINT, fg="white", bg=ACC2
             ).place(relx=0.5, rely=0.5, anchor="center")

    form_body = tk.Frame(form_card, bg=CARD)
    form_body.pack(fill="both", expand=True, padx=16, pady=8)

    nombre = tk.StringVar()
    grado  = tk.StringVar()
    letra  = tk.StringVar()
    turno  = tk.StringVar(value="MATUTINO")

    # ── Helper campo ──────────────────────────────────────────
    def make_field(parent, label, var, w=30):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=(0, 6))
        tk.Label(row, text=label, font=FONT_LBL,
                 fg=TXT_LBL, bg=CARD, anchor="w").pack(fill="x")
        border = tk.Frame(row, bg=ACC, padx=2, pady=2)
        border.pack(fill="x")
        inner = tk.Frame(border, bg=ACC_LITE)
        inner.pack(fill="x")
        tk.Label(inner, text="›", font=("Consolas", 13, "bold"),
                 fg=ACC, bg=ACC_LITE, width=2).pack(side="left")
        e = tk.Entry(inner, textvariable=var, font=FONT_ENTRY,
                     fg=TXT, bg=ACC_LITE, insertbackground=ACC,
                     bd=0, width=w, state="disabled",
                     disabledbackground="#E2E8F0",
                     disabledforeground="#94A3B8")
        e.pack(side="left", pady=6, padx=(2, 8), fill="x", expand=True)
        e.bind("<FocusIn>",  lambda _: border.config(bg=ACC2))
        e.bind("<FocusOut>", lambda _: border.config(bg=ACC))
        return e, border

    # Campos en 2 columnas para aprovechar el ancho
    cols_frame = tk.Frame(form_body, bg=CARD)
    cols_frame.pack(fill="x")

    col_l = tk.Frame(cols_frame, bg=CARD)
    col_l.pack(side="left", fill="x", expand=True, padx=(0, 6))
    col_r = tk.Frame(cols_frame, bg=CARD)
    col_r.pack(side="left", fill="x", expand=True)

    e_nombre, b_nombre = make_field(form_body, "Nombre completo", nombre, w=34)
    e_grado,  b_grado  = make_field(col_l,     "Grado  (1–3)",    grado,  w=10)
    e_letra,  b_letra  = make_field(col_r,     "Grupo  (A–Z)",    letra,  w=10)

    # Turno
    tk.Label(form_body, text="Turno", font=FONT_LBL,
             fg=TXT_LBL, bg=CARD, anchor="w").pack(fill="x")
    turno_frame = tk.Frame(form_body, bg=ACC, padx=2, pady=2)
    turno_frame.pack(fill="x", pady=(0, 6))
    turno_inner = tk.Frame(turno_frame, bg=ACC_LITE)
    turno_inner.pack(fill="x")

    style = ttk.Style()
    style.configure("Sol.TCombobox",
                    fieldbackground=ACC_LITE, background=ACC_LITE,
                    foreground=TXT, selectbackground=SEP,
                    font=("Consolas", 11))
    cb = ttk.Combobox(turno_inner, textvariable=turno,
                      values=["MATUTINO", "VESPERTINO"],
                      state="disabled", font=FONT_ENTRY,
                      style="Sol.TCombobox")
    cb.pack(fill="x", padx=6, pady=5)

    all_fields = [e_nombre, e_grado, e_letra]

    def toggle_form(state):
        for e in all_fields:
            e.config(state=state)
        cb.config(state="readonly" if state == "normal" else "disabled")
        if state == "normal":
            e_nombre.focus()

    # ── Pastilla de estado del formulario ─────────────────────
    status_frame = tk.Frame(form_body, bg=INFO_BG,
                            highlightbackground=INFO, highlightthickness=1)
    status_frame.pack(fill="x", pady=(2, 0))
    status_lbl = tk.Label(status_frame,
                           text="  ◌  Escanea tu rostro primero",
                           font=("Trebuchet MS", 9, "bold"),
                           fg=INFO, bg=INFO_BG)
    status_lbl.pack(pady=5)

    def set_status(msg, mode="info"):
        mp = {"ok":(SUCCESS_BG,SUCCESS,"●"),
              "error":(ERROR_BG,ERROR,"✖"),
              "info":(INFO_BG,INFO,"◌"),
              "warn":(WARN_BG,WARN,"⚠")}
        bg, fg, dot = mp.get(mode, mp["info"])
        status_frame.config(bg=bg, highlightbackground=fg)
        status_lbl.config(text=f"  {dot}  {msg}", fg=fg, bg=bg)

    # ── Progressbar ───────────────────────────────────────────
    prog = ttk.Progressbar(form_body, mode="indeterminate")
    prog.pack(fill="x", pady=(4, 0))

    # ══════════════════════════════════════════════════════════
    #  BOTÓN REGISTRAR (sticky al fondo)
    # ══════════════════════════════════════════════════════════
    btn_outer = tk.Frame(win, bg=ACC_HOV, padx=2, pady=2)
    btn_outer.place(x=12, y=742, width=454, height=50)

    btn_reg = tk.Button(
        btn_outer,
        text="✓   Registrar Estudiante",
        font=FONT_BTN,
        fg="white", bg=ACC,
        activebackground=ACC_HOV, activeforeground="white",
        bd=0, cursor="hand2", state="disabled",
        disabledforeground="#A5B4FC",
        command=None
=======
def _notify(state_callback: Optional[Callable[[str], None]], message: str) -> None:
    if state_callback is not None:
        state_callback(message)


def registrar_usuario(state_callback: Optional[Callable[[str], None]] = None):
    _notify(state_callback, "Inicializando registro biometrico...")
    recognition_settings = get_recognition_settings()
    use_case = RegistrationUseCase(
        registration_service=RegistrationService(SQLiteRepository()),
        pkl_repository=PklRepository(),
>>>>>>> 7b8e1a289254b37d3144b741d98017de8259c97a
    )
    btn_reg.pack(fill="both", expand=True)
    btn_reg.bind("<Enter>", lambda e: btn_reg.config(bg=ACC_HOV)
                 if btn_reg["state"] == "normal" else None)
    btn_reg.bind("<Leave>", lambda e: btn_reg.config(bg=ACC)
                 if btn_reg["state"] == "normal" else None)

    # Footer
    tk.Label(win, text="Face-ID System  v1.0",
             font=("Trebuchet MS", 7, "bold"),
             fg=TXT_MUTE, bg=BG).place(x=0, y=796, width=480)

<<<<<<< HEAD
    # ══════════════════════════════════════════════════════════
    #  LOOP DE CÁMARA
    # ══════════════════════════════════════════════════════════
    def update_cam():
        if not running['ok']:
            return

=======
    if cap is None:
        message = "No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo."
        print(message)
        _notify(state_callback, message)
        return

    start_message = f"Registrando a {nombre} en {grado}{letra}-{turno}. Presiona 'S' para capturar o 'Q' para salir."
    print(start_message)
    _notify(state_callback, start_message)

    while True:
>>>>>>> 7b8e1a289254b37d3144b741d98017de8259c97a
        ret, frame = cap.read()
        if ret:
            latest['frame'] = frame.copy()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = rgb.shape[:2]
            cx, cy = w // 2, h // 2
            ex, ey = int(w * 0.28), int(h * 0.40)

            enc = encode_single_face_from_frame(frame)

            # ─ Color del óvalo según detección ─
            if enc is None:
                face_data['frames']    = 0
                face_data['countdown'] = 0
                oval_color = (153, 27, 27)    # rojo oscuro
                hint_txt   = "Coloca tu rostro dentro del óvalo"
                hint_bg    = ERROR_BG;  hint_fg = ERROR
            else:
                face_data['frames'] += 1
                f = face_data['frames']
                if f < 10:
                    oval_color = (29, 78, 216)   # azul
                    hint_txt   = "Acércate un poco más…"
                    hint_bg    = INFO_BG;  hint_fg = INFO
                elif f < 20:
                    oval_color = (146, 64, 14)   # ámbar
                    hint_txt   = "Mantente quieto…"
                    hint_bg    = WARN_BG;  hint_fg = WARN
                else:
                    oval_color = (6, 95, 70)     # verde oscuro
                    hint_txt   = "Perfecto  ✔  Capturando…"
                    hint_bg    = SUCCESS_BG;  hint_fg = SUCCESS

                    if not face_data['captured']:
                        face_data['countdown'] += 1

<<<<<<< HEAD
            # ─ Cuenta regresiva y captura automática ─
            if face_data['countdown'] > 0 and not face_data['captured']:
                count = 3 - (face_data['countdown'] // 10)
                if count > 0:
                    cv2.putText(rgb, str(count),
                                (cx - 24, cy + 16),
                                cv2.FONT_HERSHEY_SIMPLEX, 2.4,
                                (6, 95, 70), 5)
                else:
                    face_data['encoding'] = enc
                    face_data['captured'] = True
                    toggle_form("normal")
                    set_step(1)
                    btn_reg.config(state="normal",
                                   command=lambda: threading.Thread(
                                       target=guardar, daemon=True).start())
                    set_status("Rostro capturado ✔  Completa los datos", "ok")
                    cam_title.config(text="Rostro registrado  ✔")
                    try:
                        winsound.Beep(1200, 300)
                    except Exception:
                        pass

            # ─ Overlay con hueco elíptico ─
            overlay = rgb.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (240, 244, 255), -1)
            cv2.ellipse(overlay, (cx, cy), (ex, ey), 0, 0, 360, (240, 244, 255), -1)
            cv2.addWeighted(overlay, 0.28, rgb, 0.72, 0, rgb)
=======
            if result.success:
                print(result.message)
                _notify(state_callback, result.message)
                break

            print(result.message)
            _notify(state_callback, result.message)
>>>>>>> 7b8e1a289254b37d3144b741d98017de8259c97a

            # Óvalo principal
            cv2.ellipse(rgb, (cx, cy), (ex, ey), 0, 0, 360, oval_color, 3)
            # Esquinas decorativas del óvalo
            for a in [0, 90, 180, 270]:
                cv2.ellipse(rgb, (cx, cy), (ex, ey), 0, a-15, a+15, oval_color, 5)

<<<<<<< HEAD
            # Actualizar hint de cámara
            cam_hint_lbl.config(text=hint_txt, fg=hint_fg, bg=hint_bg)
            cam_bar.config(bg=hint_bg)
=======
    cap.release()
    cv2.destroyAllWindows()
    _notify(state_callback, "Registro biometrico finalizado.")
>>>>>>> 7b8e1a289254b37d3144b741d98017de8259c97a

            img   = Image.fromarray(rgb).resize((438, 230))
            imgtk = ImageTk.PhotoImage(img)
            cam_lbl.imgtk = imgtk
            cam_lbl.configure(image=imgtk)

        win.after(15, update_cam)

    update_cam()

    # ══════════════════════════════════════════════════════════
    #  GUARDAR
    # ══════════════════════════════════════════════════════════
    def guardar():
        # Validación
        if not nombre.get().strip():
            set_status("Nombre requerido", "error"); return
        if grado.get() not in ["1", "2", "3"]:
            set_status("Grado inválido (1–3)", "error"); return
        if len(letra.get()) != 1 or not letra.get().isalpha():
            set_status("Grupo inválido (A–Z)", "error"); return

        enc = face_data['encoding']
        if enc is None:
            set_status("Primero escanea tu rostro", "error"); return

        prog.start()
        set_status("Guardando…", "info")
        btn_reg.config(state="disabled")

        try:
            g   = int(grado.get())
            l   = letra.get().upper()
            t   = turno.get()
            sid = service.register_student_with_encoding(g, l, t, enc)

            try:
                service.repository.conn.execute(
                    "UPDATE students SET name=? WHERE id=?",
                    (nombre.get().strip(), sid)
                )
                service.repository.conn.commit()
            except Exception:
                pass

            with open(f"data/est_{sid}.pkl", "wb") as f:
                pickle.dump(enc, f)

            prog.stop()
            set_step(2)
            set_status(f"¡Registrado!  #{sid}  —  {nombre.get().strip()}", "ok")
            try:
                winsound.Beep(900, 200)
                winsound.Beep(1100, 200)
            except Exception:
                pass
            messagebox.showinfo("Éxito",
                f"{nombre.get().strip()} registrado como estudiante #{sid}")

            # Reset para nuevo registro
            nombre.set(""); grado.set(""); letra.set(""); turno.set("MATUTINO")
            face_data.update({'frames': 0, 'encoding': None,
                              'captured': False, 'countdown': 0})
            toggle_form("disabled")
            set_step(0)
            set_status("Escanea tu rostro primero", "info")
            btn_reg.config(state="disabled")

        except Exception as ex:
            prog.stop()
            set_status(f"Error: {ex}", "error")
            btn_reg.config(state="normal")

    # ══════════════════════════════════════════════════════════
    #  CIERRE LIMPIO
    # ══════════════════════════════════════════════════════════
    def cerrar():
        running['ok'] = False
        cap.release()
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", cerrar)