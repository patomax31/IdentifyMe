import cv2
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
from src.application.auth_service import AuthService
from src.application.login_use_case import LoginUseCase
from src.core.config import get_recognition_settings
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame
from src.infrastructure.recognition.matcher_adapter import FaceMatcherAdapter

BG='#EEF2FF'; CARD='#FFFFFF'; SIDE='#F8FAFF'; ACC='#4338CA'; ACC2='#7C3AED'; BORDER='#A5B4FC'; TXT='#1E1B4B'
OK='#065F46'; OKBG='#D1FAE5'; ERR='#991B1B'; ERRBG='#FEE2E2'; INFO='#1D4ED8'; INFOBG='#DBEAFE'

def login():
    settings = get_recognition_settings()
    use_case = LoginUseCase(
        auth_service=AuthService(SQLiteRepository()),
        matcher=FaceMatcherAdapter(),
        pkl_repository=PklRepository(),
        tolerance=settings.tolerance,
        cooldown_seconds=settings.access_cooldown_seconds,
    )
    use_case.initialize()
    rostros_db, nombres_db, ids_db = use_case.load_known_students()
    if not rostros_db:
        print('No hay biometria registrada. Ejecuta primero registrar.py'); return
    cap = open_camera()
    if cap is None:
        print('No se pudo acceder a la camara.'); return

    win=tk.Tk(); win.title('Login Biometrico'); win.geometry('800x560'); win.resizable(False,False); win.configure(bg=BG)
    left=tk.Frame(win,bg=CARD,highlightbackground=BORDER,highlightthickness=2); left.place(x=10,y=10,width=490,height=540)
    right=tk.Frame(win,bg=SIDE,highlightbackground=BORDER,highlightthickness=2); right.place(x=514,y=10,width=276,height=540)

    h1=tk.Frame(left,bg=ACC,height=44); h1.pack(fill='x'); h1.pack_propagate(False)
    tk.Label(h1,text='📷  Acceso en Tiempo Real',font=('Segoe UI',11,'bold'),fg='white',bg=ACC).place(relx=.5,rely=.5,anchor='center')
    tk.Frame(left,bg=ACC2,height=3).pack(fill='x')
    cam_box=tk.Frame(left,bg='#1E1B4B',padx=4,pady=4); cam_box.pack(fill='both',expand=True,padx=14,pady=14)
    cam=tk.Label(cam_box,bg='#1E1B4B'); cam.pack(fill='both',expand=True)

    foot=tk.Frame(left,bg='#E0E7FF',height=36); foot.pack(fill='x',padx=14,pady=(0,14)); foot.pack_propagate(False)
    tk.Label(foot,text='● LIVE',fg=ERR,bg='#E0E7FF',font=('Segoe UI',8,'bold')).place(x=10,rely=.5,anchor='w')
    tk.Label(foot,text='Coloca tu rostro frente a la cámara',fg=ACC,bg='#E0E7FF',font=('Segoe UI',8)).place(relx=.5,rely=.5,anchor='center')

    h2=tk.Frame(right,bg=ACC,height=44); h2.pack(fill='x'); h2.pack_propagate(False)
    tk.Label(h2,text='🔐  Control de Acceso',font=('Segoe UI',11,'bold'),fg='white',bg=ACC).place(relx=.5,rely=.5,anchor='center')
    tk.Frame(right,bg=ACC2,height=3).pack(fill='x')
    body=tk.Frame(right,bg=SIDE); body.pack(fill='both',expand=True,padx=14,pady=10)

    reloj=tk.Label(body,text='',font=('Consolas',20,'bold'),fg='#F59E0B',bg=SIDE)
    reloj.pack(fill='x',pady=(0,8))
    estado_fr=tk.Frame(body,bg=INFOBG,highlightbackground=INFO,highlightthickness=1)
    estado_fr.pack(fill='x')
    estado=tk.Label(estado_fr,text='◌ Esperando rostro...',font=('Segoe UI',9,'bold'),fg=INFO,bg=INFOBG,wraplength=220)
    estado.pack(pady=6)
    tk.Label(body,text='Historial',font=('Segoe UI',9,'bold'),fg=ACC,bg=SIDE).pack(anchor='w',pady=(10,4))
    historial=tk.Text(body,height=18,bg='white',fg=TXT,bd=1,relief='solid')
    historial.pack(fill='both',expand=True)

    def add_log(msg):
        historial.insert('end', f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        historial.see('end')

    def set_estado(msg,mode='info'):
        mp={'ok':(OKBG,OK,'●'),'error':(ERRBG,ERR,'✖'),'info':(INFOBG,INFO,'◌')}
        bg,fg,d=mp[mode]
        estado_fr.config(bg=bg,highlightbackground=fg)
        estado.config(text=f'{d} {msg}',bg=bg,fg=fg)

    def tick():
        reloj.config(text=datetime.now().strftime('%H:%M:%S'))
        win.after(1000,tick)
    tick()

    last=''
    running={'ok':True}
    def loop():
        nonlocal last
        if not running['ok']: return
        ret, frame = cap.read()
        if ret:
            alto, ancho, _ = frame.shape
            centro=(ancho//2,alto//2); ejes=(int(ancho*.25),int(alto*.4))
            _, encodings = detect_face_encodings_from_frame(frame, scale=settings.scale)
            result = use_case.process_frame(encodings, rostros_db, nombres_db, ids_db)
            cv2.ellipse(frame, centro, ejes, 0,0,360, result.color, 2)
            cv2.rectangle(frame,(0,0),(ancho,40),(0,0,0),-1)
            cv2.putText(frame,result.message,(20,28),cv2.FONT_HERSHEY_DUPLEX,.75,result.color,2)
            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            img=Image.fromarray(rgb).resize((462,430))
            imgtk=ImageTk.PhotoImage(img)
            cam.imgtk=imgtk; cam.configure(image=imgtk)
            txt=result.message
            if txt!=last:
                low=txt.lower()
                if 'permit' in low or 'bienvenido' in low or 'acceso' in low:
                    set_estado(txt,'ok')
                elif 'no' in low or 'deneg' in low or 'desconoc' in low:
                    set_estado(txt,'error')
                else:
                    set_estado(txt,'info')
                add_log(txt)
                last=txt
        win.after(15,loop)

    def cerrar():
        running['ok']=False
        cap.release()
        win.destroy()

    tk.Button(body,text='Salir',command=cerrar,bg='#EF4444',fg='white',bd=0,pady=8,cursor='hand2').pack(fill='x',pady=10)
    tk.Frame(right,bg=ACC2,height=3).pack(fill='x',side='bottom')
    f=tk.Frame(right,bg=ACC,height=24); f.pack(fill='x',side='bottom'); f.pack_propagate(False)
    tk.Label(f,text='Face-ID System v1.0',font=('Segoe UI',7,'bold'),fg='white',bg=ACC).place(relx=.5,rely=.5,anchor='center')
    win.protocol('WM_DELETE_WINDOW', cerrar)
    loop(); win.mainloop()

if __name__ == '__main__':
    login()