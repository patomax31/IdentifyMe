# -*- coding: utf-8 -*-
"""
configBase.py - Configuración centralizada del sistema de reconocimiento facial
Permite ajustar parámetros de login y registro de forma interactiva
"""

import os
import json

CONFIG_FILE = "config_settings.json"

# Configuración por defecto
DEFAULT_CONFIG = {
    # REGISTRO
    "registro": {
        "oval_width_ratio": 0.25,      # Proporción del ancho de óvalo respecto a pantalla (0.1 - 0.5)
        "oval_height_ratio": 0.4,      # Proporción del alto de óvalo respecto a pantalla (0.2 - 0.6)
        "line_thickness": 2,           # Grosor de línea del óvalo (1 - 5)
    },
    
    # LOGIN
    "login": {
        "tolerance": 0.5,              # Precisión reconocimiento (0.3 - 0.7, menor = más estricto)
        "process_every_n_frames": 3,   # Procesar cada N frames (1 - 10, mayor = más rápido pero menos preciso)
        "frames_to_confirm": 2,        # Frames seguidos para confirmar (1 - 5)
        "cooldown_seconds": 8.0,       # Segundos entre mismo usuario (1 - 30)
        "scanning_time_seconds": 3.0,  # Tiempo de escaneo sin moverse (1 - 8)
        "state_display_seconds": 2.0,  # Tiempo mostrando estado (1 - 5)
    },
    
    # CÁMARA
    "camera": {
        "width": 640,                  # Ancho (320 - 1280)
        "height": 480,                 # Alto (240 - 1024)
    },
    
    # INTERFAZ
    "ui": {
        "line_thickness": 3,           # Grosor de líneas en login (1 - 5)
        "font_scale": 1.1,             # Tamaño de fuente (0.5 - 2.0)
    }
}

def load_config():
    """Carga la configuración desde archivo o retorna default"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[AVISO] Error al cargar config: {e}. Usando valores por defecto.")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    """Guarda la configuración en archivo JSON"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print("[OK] Configuracion guardada correctamente.")
    except Exception as e:
        print(f"[ERROR] Error al guardar configuracion: {e}")

def solicitar_valor(prompt, tipo=str, minimo=None, maximo=None, default=None):
    """Solicita un valor al usuario con validación"""
    while True:
        try:
            valor_str = input(prompt).strip()
            
            if not valor_str and default is not None:
                return default
            
            if tipo == int:
                valor = int(valor_str)
                if minimo is not None and valor < minimo:
                    print(f"  ❌ Valor muy bajo. Mínimo: {minimo}")
                    continue
                if maximo is not None and valor > maximo:
                    print(f"  ❌ Valor muy alto. Máximo: {maximo}")
                    continue
                return valor
            
            elif tipo == float:
                valor = float(valor_str)
                if minimo is not None and valor < minimo:
                    print(f"  [ERROR] Valor muy bajo. Minimo: {minimo}")
                    continue
                if maximo is not None and valor > maximo:
                    print(f"  [ERROR] Valor muy alto. Maximo: {maximo}")
                    continue
                return valor
            
            elif tipo == str:
                return valor_str
                
        except ValueError:
            print(f"  [ERROR] Entrada invalida. Esperado: {tipo.__name__}")

def configurar_interactivo():
    """Modo interactivo para configurar parámetros"""
    config = load_config()
    
    print("\n" + "="*70)
    print(" === CONFIGURACION DEL SISTEMA DE RECONOCIMIENTO FACIAL ===")
    print("="*70)
    print("Presiona ENTER para mantener el valor actual entre parentesis\n")
    
    # CONFIGURACIÓN DE REGISTRO
    print("\n<> CONFIGURACION DE REGISTRO")
    print("-" * 70)
    print("Oval guia - Define el marco donde debe aparecer el rostro")
    
    config["registro"]["oval_width_ratio"] = solicitar_valor(
        f"  Proporción ancho del óvalo (0.1-0.5) [{config['registro']['oval_width_ratio']}]: ",
        float, 0.1, 0.5, config["registro"]["oval_width_ratio"]
    )
    
    config["registro"]["oval_height_ratio"] = solicitar_valor(
        f"  Proporción alto del óvalo (0.2-0.6) [{config['registro']['oval_height_ratio']}]: ",
        float, 0.2, 0.6, config["registro"]["oval_height_ratio"]
    )
    
    config["registro"]["line_thickness"] = solicitar_valor(
        f"  Grosor línea óvalo (1-5) [{config['registro']['line_thickness']}]: ",
        int, 1, 5, config["registro"]["line_thickness"]
    )
    
    # CONFIGURACIÓN DE LOGIN
    print("\n[*] CONFIGURACION DE LOGIN")
    print("-" * 70)
    print("Reconocimiento facial - Ajusta precision y velocidad")
    
    config["login"]["tolerance"] = solicitar_valor(
        f"  Precisión (tolerance) (0.3-0.7, menor=más estricto) [{config['login']['tolerance']}]: ",
        float, 0.3, 0.7, config["login"]["tolerance"]
    )
    
    config["login"]["process_every_n_frames"] = solicitar_valor(
        f"  Procesar cada N frames (1-10) [{config['login']['process_every_n_frames']}]: ",
        int, 1, 10, config["login"]["process_every_n_frames"]
    )
    
    config["login"]["frames_to_confirm"] = solicitar_valor(
        f"  Frames seguidos para confirmar (1-5) [{config['login']['frames_to_confirm']}]: ",
        int, 1, 5, config["login"]["frames_to_confirm"]
    )
    
    config["login"]["cooldown_seconds"] = solicitar_valor(
        f"  Cooldown entre accesos (seg) (1-30) [{config['login']['cooldown_seconds']}]: ",
        float, 1, 30, config["login"]["cooldown_seconds"]
    )
    
    config["login"]["scanning_time_seconds"] = solicitar_valor(
        f"  TIEMPO DE ESCANEO (seg) - No moverse (1-8) [{config['login']['scanning_time_seconds']}]: ",
        float, 1, 8, config["login"]["scanning_time_seconds"]
    )
    
    config["login"]["state_display_seconds"] = solicitar_valor(
        f"  Tiempo mostrar estado (seg) (1-5) [{config['login']['state_display_seconds']}]: ",
        float, 1, 5, config["login"]["state_display_seconds"]
    )
    
    # CONFIGURACIÓN DE CÁMARA
    print("\n[CAM] CONFIGURACION DE CAMARA")
    print("-" * 70)
    
    config["camera"]["width"] = solicitar_valor(
        f"  Ancho (320-1280) [{config['camera']['width']}]: ",
        int, 320, 1280, config["camera"]["width"]
    )
    
    config["camera"]["height"] = solicitar_valor(
        f"  Alto (240-1024) [{config['camera']['height']}]: ",
        int, 240, 1024, config["camera"]["height"]
    )
    
    # CONFIGURACIÓN DE INTERFAZ
    print("\n[UI] CONFIGURACION DE INTERFAZ")
    print("-" * 70)
    
    config["ui"]["line_thickness"] = solicitar_valor(
        f"  Grosor líneas login (1-5) [{config['ui']['line_thickness']}]: ",
        int, 1, 5, config["ui"]["line_thickness"]
    )
    
    config["ui"]["font_scale"] = solicitar_valor(
        f"  Tamaño fuente (0.5-2.0) [{config['ui']['font_scale']}]: ",
        float, 0.5, 2.0, config["ui"]["font_scale"]
    )
    
    # GUARDAR CONFIGURACIÓN
    print("\n" + "="*70)
    save_config(config)
    print("="*70)
    
    return config

def mostrar_config_actual():
    """Muestra la configuración actual"""
    config = load_config()
    
    print("\n" + "="*70)
    print(" === CONFIGURACION ACTUAL DEL SISTEMA ===")
    print("="*70)
    
    print("\n<> REGISTRO:")
    for key, value in config["registro"].items():
        print(f"  * {key}: {value}")
    
    print("\n[*] LOGIN:")
    for key, value in config["login"].items():
        print(f"  * {key}: {value}")
    
    print("\n[CAM] CAMARA:")
    for key, value in config["camera"].items():
        print(f"  * {key}: {value}")
    
    print("\n[UI] INTERFAZ:")
    for key, value in config["ui"].items():
        print(f"  * {key}: {value}")
    
    print("="*70 + "\n")

def main():
    """Menú principal"""
    while True:
        print("\n" + "="*70)
        print(" === GESTOR DE CONFIGURACION - RECONOCIMIENTO FACIAL ===")
        print("="*70)
        print("1 - Configurar parametros (interactivo)")
        print("2 - Ver configuracion actual")
        print("3 - Restaurar valores por defecto")
        print("4 - Salir")
        print("="*70)
        
        opcion = input("Selecciona una opcion (1-4): ").strip()
        
        if opcion == "1":
            configurar_interactivo()
        elif opcion == "2":
            mostrar_config_actual()
        elif opcion == "3":
            confirmar = input("Restaurar valores por defecto? (s/n): ").strip().lower()
            if confirmar == "s":
                save_config(DEFAULT_CONFIG)
                print("[OK] Valores por defecto restaurados.")
        elif opcion == "4":
            print("[SALIDA] Hasta luego!")
            break
        else:
            print("[ERROR] Opcion no valida.")

if __name__ == "__main__":
    main()
