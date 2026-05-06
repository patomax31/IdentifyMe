#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejemplos Avanzados - Personalización del Sistema de Verificación

Este archivo muestra patrones y ejemplos para:
1. Agregar nuevas validaciones
2. Personalizar colores
3. Cambiar el comportamiento
4. Extender funcionalidades
"""

# ============================================================================
# EJEMPLO 1: Agregar una Validación Personalizada
# ============================================================================

"""
Escenario: Necesitas validar que un servicio externo (ej: API) está disponible

Paso 1: Agregar método al SystemValidator
"""

# Código a agregar en la clase SystemValidator:
"""
def validate_api_service(self) -> CheckResult:
    '''Valida disponibilidad del servicio API.'''
    result = CheckResult(
        name="Servicio API",
        category="Servicios",
        status=CheckStatus.CHECKING,
    )
    self.callback(result)
    time.sleep(0.5)
    
    try:
        import requests
        # Intenta conectarse a tu API
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            result.status = CheckStatus.SUCCESS
            result.message = "OK"
        else:
            result.status = CheckStatus.ERROR
            result.error_details = f"HTTP {response.status_code}"
    except Exception as e:
        result.status = CheckStatus.ERROR
        result.error_details = str(e)
    
    self.callback(result)
    return result
"""

# Paso 2: Agregar a run_all_checks()
"""
def run_all_checks(self) -> List[CheckResult]:
    all_results = []
    
    # ... validaciones existentes ...
    
    # Nueva sección: Servicios
    all_results.append(self.validate_api_service())
    
    return all_results
"""


# ============================================================================
# EJEMPLO 2: Cambiar Colores del Tema
# ============================================================================

"""
Escenario: Quieres usar un tema rojo/verde en lugar de azul

En SystemCheckUI._configure_styles():
"""

# Tema Rojo/Verde
THEME_RED_GREEN = {
    "bg_main": "#ffffff",
    "bg_secondary": "#f5f5f5",
    "text_primary": "#1a1a1a",
    "text_secondary": "#555555",
    "success": "#22c55e",        # Verde brillante
    "error": "#ef4444",          # Rojo brillante
    "checking": "#f59e0b",       # Ámbar
    "accent": "#22c55e",
}

# Tema Morado/Cian
THEME_PURPLE_CYAN = {
    "bg_main": "#0f172a",        # Fondo oscuro
    "bg_secondary": "#1e293b",
    "text_primary": "#f1f5f9",
    "text_secondary": "#cbd5e1",
    "success": "#06b6d4",        # Cian
    "error": "#a855f7",          # Morado
    "checking": "#60a5fa",       # Azul claro
    "accent": "#06b6d4",
}

# Tema Naranja/Gris (Profesional)
THEME_ORANGE_GRAY = {
    "bg_main": "#fafbfc",
    "bg_secondary": "#f0f1f3",
    "text_primary": "#24292e",
    "text_secondary": "#576069",
    "success": "#f76707",        # Naranja
    "error": "#6e7781",          # Gris
    "checking": "#ffa657",       # Naranja claro
    "accent": "#f76707",
}

# Código para usarlo:
"""
class SystemCheckUI(tk.Tk):
    def __init__(self, theme=None):
        super().__init__()
        self.theme = theme or THEME_BLUE_DEFAULT
        # ...resto del código...
    
    def _configure_styles(self):
        self.colors = self.theme
        # ...resto del código...
"""

# Uso:
"""
# Con tema por defecto
app = SystemCheckUI()

# Con tema personalizado
app = SystemCheckUI(theme=THEME_PURPLE_CYAN)
"""


# ============================================================================
# EJEMPLO 3: Agregar Validación de Puerto Serie (Servomotor Real)
# ============================================================================

"""
Escenario: Validar conexión real a servomotor por puerto serie
"""

VALIDATE_SERVO_REAL = """
def validate_servo_real(self) -> CheckResult:
    '''Valida conexión real al servomotor por puerto serie.'''
    result = CheckResult(
        name="Servomotor",
        category="Hardware",
        status=CheckStatus.CHECKING,
    )
    self.callback(result)
    time.sleep(0.3)
    
    try:
        import serial
        
        # Intenta abrir puerto serie (personalizar según tu configuración)
        port = "/dev/ttyUSB0"  # Linux
        # port = "COM3"  # Windows
        
        ser = serial.Serial(port, 9600, timeout=1)
        
        # Envía comando de prueba
        ser.write(b"TEST\\n")
        response = ser.readline().decode().strip()
        
        ser.close()
        
        if response == "OK":
            result.status = CheckStatus.SUCCESS
            result.message = "OK"
        else:
            result.status = CheckStatus.ERROR
            result.error_details = f"Respuesta inesperada: {response}"
            
    except ImportError:
        result.status = CheckStatus.ERROR
        result.error_details = "pyserial no instalado"
    except Exception as e:
        result.status = CheckStatus.ERROR
        result.error_details = f"Puerto no disponible: {str(e)}"
    
    self.callback(result)
    return result
"""


# ============================================================================
# EJEMPLO 4: Agregar Validación de Versión Mínima de Paquete
# ============================================================================

"""
Escenario: Verificar que OpenCV sea versión 4.5+
"""

VALIDATE_VERSION = """
def validate_opencv_version(self) -> CheckResult:
    '''Valida que OpenCV sea versión 4.5 o superior.'''
    result = CheckResult(
        name="OpenCV (v4.5+)",
        category="Dependencias",
        status=CheckStatus.CHECKING,
    )
    self.callback(result)
    time.sleep(0.3)
    
    try:
        import cv2
        version = tuple(map(int, cv2.__version__.split(".")[:2]))
        
        if version >= (4, 5):
            result.status = CheckStatus.SUCCESS
            result.message = f"OK (v{cv2.__version__})"
        else:
            result.status = CheckStatus.ERROR
            result.error_details = f"Versión {cv2.__version__} (se requiere 4.5+)"
            
    except ImportError:
        result.status = CheckStatus.ERROR
        result.error_details = "No instalado"
    
    self.callback(result)
    return result
"""


# ============================================================================
# EJEMPLO 5: Agregar Validación de Espacio en Disco
# ============================================================================

"""
Escenario: Verificar que hay al menos 500MB disponibles
"""

VALIDATE_DISK_SPACE = """
def validate_disk_space(self) -> CheckResult:
    '''Valida espacio disponible en disco (mínimo 500MB).'''
    result = CheckResult(
        name="Espacio en Disco",
        category="Sistema",
        status=CheckStatus.CHECKING,
    )
    self.callback(result)
    time.sleep(0.3)
    
    try:
        import shutil
        import os
        
        db_path = os.path.join(os.path.dirname(__file__), "database")
        stat = shutil.disk_usage(db_path)
        free_gb = stat.free / (1024 ** 3)
        
        if stat.free > 500 * 1024 * 1024:  # 500MB
            result.status = CheckStatus.SUCCESS
            result.message = f"OK ({free_gb:.1f}GB disponible)"
        else:
            result.status = CheckStatus.ERROR
            result.error_details = f"Solo {free_gb:.1f}GB disponible (se necesitan 0.5GB)"
            
    except Exception as e:
        result.status = CheckStatus.ERROR
        result.error_details = str(e)
    
    self.callback(result)
    return result
"""


# ============================================================================
# EJEMPLO 6: Agregar Validación de Permisos de Archivo
# ============================================================================

"""
Escenario: Verificar permisos de lectura/escritura en carpeta de datos
"""

VALIDATE_FILE_PERMISSIONS = """
def validate_permissions(self) -> CheckResult:
    '''Valida permisos de lectura/escritura en carpeta de datos.'''
    result = CheckResult(
        name="Permisos de Archivo",
        category="Sistema",
        status=CheckStatus.CHECKING,
    )
    self.callback(result)
    time.sleep(0.3)
    
    try:
        import os
        import tempfile
        
        db_path = os.path.join(os.path.dirname(__file__), "database")
        
        # Crear archivo temporal para probar escritura
        test_file = os.path.join(db_path, ".write_test")
        
        with open(test_file, "w") as f:
            f.write("test")
        
        os.remove(test_file)
        
        result.status = CheckStatus.SUCCESS
        result.message = "OK"
        
    except PermissionError:
        result.status = CheckStatus.ERROR
        result.error_details = f"Permisos insuficientes en {db_path}"
    except Exception as e:
        result.status = CheckStatus.ERROR
        result.error_details = str(e)
    
    self.callback(result)
    return result
"""


# ============================================================================
# EJEMPLO 7: Personalizar Mensaje de Inicio
# ============================================================================

"""
Escenario: Cambiar el título de la ventana y mensajes iniciales
"""

CUSTOM_MESSAGES = """
class SystemCheckUI(tk.Tk):
    def __init__(self, title=None, subtitle=None):
        super().__init__()
        
        # Títulos personalizables
        self.window_title = title or "Sistema de Acceso Facial"
        self.check_title = subtitle or "Inicializando sistema de acceso facial"
        
        self.title(self.window_title)
        self._create_widgets()
    
    def _create_widgets(self):
        # En el método que crea el título:
        title_label = tk.Label(
            main_frame,
            text=self.check_title,
            font=("Segoe UI", 16, "bold"),
            # ...resto...
        )
"""

# Uso:
"""
app = SystemCheckUI(
    title="Mi Aplicación de Acceso",
    subtitle="Verificando componentes necesarios..."
)
"""


# ============================================================================
# EJEMPLO 8: Agregar Logo o Imagen
# ============================================================================

"""
Escenario: Mostrar un logo durante el proceso de verificación
"""

ADD_LOGO = """
def _create_widgets(self):
    # ...código anterior...
    
    # Cargar imagen de logo
    try:
        from PIL import Image, ImageTk
        
        logo = Image.open("logo.png")
        logo.thumbnail((100, 100), Image.Resampling.LANCZOS)
        self.logo_image = ImageTk.PhotoImage(logo)
        
        logo_label = tk.Label(
            main_frame,
            image=self.logo_image,
            bg=self.colors["bg_main"]
        )
        logo_label.pack(pady=10)
    except Exception:
        pass  # Si no hay logo, continuar sin él
    
    # ...resto del código...
"""


# ============================================================================
# EJEMPLO 9: Guardar Logs de Verificación
# ============================================================================

"""
Escenario: Guardar resultado de verificaciones en archivo
"""

SAVE_LOGS = """
import json
from datetime import datetime

class SystemValidator:
    def __init__(self, callback, log_file="verification.log"):
        self.callback = callback
        self.log_file = log_file
    
    def save_log(self):
        '''Guarda los resultados en un archivo JSON.'''
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "checks": [
                {
                    "name": r.name,
                    "category": r.category,
                    "status": r.status.value,
                    "message": r.message,
                    "error": r.error_details,
                }
                for r in self.results
            ]
        }
        
        with open(self.log_file, "w") as f:
            json.dump(log_data, f, indent=2)
"""

# Uso:
"""
validator = SystemValidator(callback, log_file="verification.log")
validator.run_all_checks()
validator.save_log()  # Guardar después de completar
"""


# ============================================================================
# EJEMPLO 10: Agregar Reintentos Automáticos
# ============================================================================

"""
Escenario: Reintentar automáticamente si falla (máximo 3 intentos)
"""

AUTO_RETRY = """
class SystemCheckUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.max_retries = 3
        self.current_retry = 0
    
    def _start_validation(self):
        '''Inicia validaciones con reintentos automáticos.'''
        # ... código existente ...
        
        if self.current_retry < self.max_retries:
            self.after(5000, self._check_retry_needed)
    
    def _check_retry_needed(self):
        '''Verifica si necesita reintentar.'''
        errors = [r for r in self.validator.results if r.status == CheckStatus.ERROR]
        
        if errors and self.current_retry < self.max_retries:
            self.current_retry += 1
            print(f"Reintentando... ({self.current_retry}/{self.max_retries})")
            self._start_validation()
"""


# ============================================================================
# RESUMEN DE EXTENSIONES COMUNES
# ============================================================================

"""
Checklist de personalizaciones comunes:

□ Cambiar colores del tema
  → Editar dictionary en _configure_styles()

□ Agregar nueva validación
  → Crear método en SystemValidator
  → Llamar en run_all_checks()

□ Cambiar títulos/mensajes
  → Pasar parámetros al __init__()
  → O editar strings directamente

□ Validar Puerto Serie (Servo)
  → Instalar: pip install pyserial
  → Ver VALIDATE_SERVO_REAL arriba

□ Validar Versión de Paquete
  → Ver VALIDATE_VERSION arriba

□ Guardar Logs
  → Ver SAVE_LOGS arriba

□ Agregar Logo
  → Ver ADD_LOGO arriba

□ Reintentos Automáticos
  → Ver AUTO_RETRY arriba

□ Validar Espacio Disco
  → Ver VALIDATE_DISK_SPACE arriba

□ Validar Permisos
  → Ver VALIDATE_FILE_PERMISSIONS arriba
"""

# ============================================================================
# TEMPLATES ÚTILES
# ============================================================================

"""
Template para nueva validación genérica:

def validate_NOMBRE(self) -> CheckResult:
    '''Descripción de lo que valida.'''
    result = CheckResult(
        name="NOMBRE",
        category="CATEGORÍA",
        status=CheckStatus.CHECKING,
    )
    self.callback(result)
    time.sleep(0.3)
    
    try:
        # TU LÓGICA AQUÍ
        # Si todo bien:
        result.status = CheckStatus.SUCCESS
        result.message = "OK"
        # Si hay error:
        # result.status = CheckStatus.ERROR
        # result.error_details = "Descripción del error"
    except Exception as e:
        result.status = CheckStatus.ERROR
        result.error_details = str(e)
    
    self.callback(result)
    return result
"""

if __name__ == "__main__":
    print("""
    Este archivo contiene ejemplos de código para personalizar
    el Sistema de Verificación.
    
    Copiar el código de los ejemplos que necesites e integrar
    en test_setup.py según tus requisitos.
    
    Ejemplos disponibles:
    1. Agregar validación personalizada
    2. Cambiar colores del tema
    3. Validación de servomotor real
    4. Validación de versión de paquete
    5. Validación de espacio en disco
    6. Validación de permisos
    7. Personalizar mensajes
    8. Agregar logo
    9. Guardar logs
    10. Reintentos automáticos
    """)
