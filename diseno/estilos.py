from tkinter import ttk
from .colores import *

def aplicar_estilos():
    style = ttk.Style()
    style.configure("Custom.TCombobox",
        fieldbackground=CARD,
        background=CARD,
        foreground=TXT
    )