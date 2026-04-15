import tkinter as tk
import threading
import cv2
import pickle
import os


# ─── Paleta del dashboard ────────────────────────────────────────────────────
BG_DARK      = "#0f172a"
BG_CARD      = "#1e293b"
BG_INPUT     = "#0f172a"
BORDER       = "#334155"
ACCENT       = "#7C3AED"
ACCENT_LIGHT = "#EDE9FE"
SUCCESS      = "#10B981"
ERROR        = "#ef4444"
TEXT_PRIMARY = "#f1f5f9"
TEXT_MUTED   = "#64748b"


def registrar_usuario():

    def iniciar_captura():
        nombre = entry_nombre.get().strip().lower()

        if not nombre:
            label_estado.config(text="⚠  Ingresa un nombre", fg=ERROR)
            return

        ventana_registro.destroy()

        if not os.path.exists("data"):
            os.makedirs("data")

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            alto, ancho, _ = frame.shape
            centro = (ancho // 2, alto // 2)
            ejes   = (int(ancho * 0.25), int(alto * 0.4))

            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (ancho, alto), (0, 0, 0), -1)
            cv2.ellipse(overlay, centro, ejes, 0, 0, 360, (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

            cv2.ellipse(frame, centro, ejes, 0, 0, 360, (124, 58, 237), 2)
            for angle in [0, 90, 180, 270]:
                cv2.ellipse(frame, centro, ejes, 0, angle - 10, angle + 10, (16, 185, 129), 3)

            cv2.rectangle(frame, (0, alto - 50), (ancho, alto), (15, 23, 42), -1)
            cv2.putText(frame, f"ID: {nombre.upper()}",
                        (12, alto - 28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (124, 58, 237), 1)
            cv2.putText(frame, "[S] CAPTURAR   [Q] CANCELAR",
                        (12, alto - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 116, 139), 1)

            cv2.rectangle(frame, (0, 0), (ancho, 32), (15, 23, 42), -1)
            cv2.putText(frame, "REGISTRO FACIAL",
                        (12, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (124, 58, 237), 1)

            cv2.imshow("Registro Facial", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb)

                if len(boxes) == 1:
                    encoding = face_recognition.face_encodings(rgb, boxes)[0]
                    with open(f"data/{nombre}.pkl", "wb") as f:
                        pickle.dump(encoding, f)
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                else:
                    cv2.rectangle(frame, (0, 0), (ancho, alto), (239, 68, 68), 3)
                    cv2.putText(frame, "UN SOLO ROSTRO REQUERIDO",
                                (ancho // 2 - 160, alto // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (239, 68, 68), 2)
                    cv2.imshow("Registro Facial", frame)
                    cv2.waitKey(1200)

            if key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    # ─────────────────────────────────────────────────────────────────────────
    # VENTANA REGISTRO
    # ─────────────────────────────────────────────────────────────────────────
    ventana_registro = tk.Toplevel()
    ventana_registro.title("Registro Facial")
    ventana_registro.geometry("420x520")
    ventana_registro.resizable(False, False)
    ventana_registro.configure(bg=BG_DARK)

    # ── Card principal ───────────────────────────────────────────────────────
    card = tk.Frame(ventana_registro, bg=BG_CARD,
                    highlightbackground=BORDER, highlightthickness=1)
    card.place(relx=0.5, rely=0.5, anchor="center", width=364, height=464)

    # ── Header morado ────────────────────────────────────────────────────────
    header = tk.Frame(card, bg=ACCENT, height=56)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="Registro de Usuario",
             font=("Segoe UI", 13, "bold"),
             fg="white", bg=ACCENT).place(relx=0.5, rely=0.5, anchor="center")

    # ── Ícono facial ─────────────────────────────────────────────────────────
    icon_canvas = tk.Canvas(card, width=100, height=100,
                            bg=BG_CARD, highlightthickness=0)
    icon_canvas.pack(pady=(24, 0))

    # Halo
    icon_canvas.create_oval(2, 2, 98, 98, outline=ACCENT_LIGHT, width=8)
    # Círculo escaneo
    icon_canvas.create_oval(14, 14, 86, 86, outline=ACCENT, width=2, dash=(5, 4))
    # Cara
    icon_canvas.create_oval(22, 20, 78, 80, outline=ACCENT, width=2)
    # Marcadores
    for x1,y1,x2,y2 in [(22,20,34,20),(22,20,22,32),
                          (66,20,78,20),(78,20,78,32),
                          (22,68,22,80),(22,80,34,80),
                          (66,80,78,80),(78,68,78,80)]:
        icon_canvas.create_line(x1,y1,x2,y2, fill=SUCCESS, width=2)
    # Ojos
    icon_canvas.create_oval(34, 38, 44, 48, fill=ACCENT, outline="")
    icon_canvas.create_oval(56, 38, 66, 48, fill=ACCENT, outline="")
    # Nariz
    icon_canvas.create_line(50, 50, 46, 60, fill=TEXT_MUTED, width=1)
    icon_canvas.create_line(50, 50, 54, 60, fill=TEXT_MUTED, width=1)
    # Boca
    icon_canvas.create_arc(36, 56, 64, 74, start=200, extent=140,
                            outline=ACCENT, width=2, style="arc")

    # ── Separador ────────────────────────────────────────────────────────────
    sep = tk.Frame(card, bg=BORDER, height=1)
    sep.pack(fill="x", padx=28, pady=(18, 0))

    # ── Label ────────────────────────────────────────────────────────────────
    tk.Label(card, text="Ingresa tu nombre",
             font=("Segoe UI", 9),
             fg=TEXT_MUTED, bg=BG_CARD).pack(pady=(14, 6))

    # ── Input ────────────────────────────────────────────────────────────────
    input_frame = tk.Frame(card, bg=ACCENT, padx=1, pady=1)
    input_frame.pack(padx=32, fill="x")

    input_inner = tk.Frame(input_frame, bg=BG_INPUT)
    input_inner.pack(fill="x")

    tk.Label(input_inner, text=" › ", font=("Segoe UI", 12, "bold"),
             fg=ACCENT, bg=BG_INPUT).pack(side="left", padx=(8, 0), pady=10)

    entry_nombre = tk.Entry(
        input_inner,
        font=("Segoe UI", 11),
        fg=TEXT_PRIMARY,
        bg=BG_INPUT,
        insertbackground=ACCENT,
        bd=0,
        width=16
    )
    entry_nombre.pack(side="left", pady=10, padx=(0, 10))
    entry_nombre.focus()

    # ── Estado ───────────────────────────────────────────────────────────────
    label_estado = tk.Label(card, text="",
                            font=("Segoe UI", 8),
                            fg=ERROR, bg=BG_CARD)
    label_estado.pack(pady=(8, 0))

 # ── Info ─────────────────────────────────────────────────────────────────
    info_frame = tk.Frame(card, bg="#1a1f35", highlightbackground=BORDER, highlightthickness=1)
    info_frame.pack(padx=32, pady=(6, 0), fill="x")

    tk.Label(info_frame,
             text="📋  INSTRUCCIONES",
             font=("Segoe UI", 8, "bold"),
             fg=ACCENT, bg="#1a1f35").pack(anchor="w", padx=12, pady=(10, 4))

    pasos = [
        ("1", "Posiciona tu rostro frente a la cámara"),
        ("2", "Mantén buena iluminación"),
        ("3", "Presiona  S  para capturar"),
    ]

    for num, texto in pasos:
        fila = tk.Frame(info_frame, bg="#1a1f35")
        fila.pack(fill="x", padx=12, pady=2)

        tk.Label(fila, text=num,
                 font=("Segoe UI", 7, "bold"),
                 fg="white", bg=ACCENT,
                 width=2).pack(side="left", padx=(0, 8))

        tk.Label(fila, text=texto,
                 font=("Segoe UI", 8),
                 fg=TEXT_MUTED, bg="#1a1f35").pack(side="left", anchor="w")

    tk.Frame(info_frame, bg="#1a1f35", height=8).pack()
    # ── Botón ────────────────────────────────────────────────────────────────
    btn_frame = tk.Frame(card, bg=BG_CARD)
    btn_frame.pack(pady=20, padx=32, fill="x")

    btn = tk.Button(
        btn_frame,
        text="Iniciar Captura",
        font=("Segoe UI", 11, "bold"),
        fg="white",
        bg=ACCENT,
        activebackground="#5B21B6",
        activeforeground="white",
        bd=0,
        pady=12,
        cursor="hand2",
        command=lambda: threading.Thread(target=iniciar_captura, daemon=True).start()
    )
    btn.pack(fill="x")
    btn.bind("<Enter>", lambda e: btn.config(bg="#5B21B6"))
    btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT))

    # ── Footer ───────────────────────────────────────────────────────────────
    footer = tk.Frame(card, bg=BG_DARK, height=32)
    footer.pack(fill="x", side="bottom")
    footer.pack_propagate(False)
    tk.Label(footer, text="Face-ID System  v1.0",
             font=("Segoe UI", 7),
             fg=TEXT_MUTED, bg=BG_DARK).place(relx=0.5, rely=0.5, anchor="center")