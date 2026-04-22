# Guía - Sistema de Verificación con Interfaz Gráfica

## Descripción General

El nuevo `test_setup.py` es una interfaz gráfica moderna (splash screen) que valida el estado del sistema antes de iniciar la aplicación de reconocimiento facial.

## Características

### 1. **Interfaz Moderna**
- Diseño limpio con Tkinter
- Colores profesionales (azul marino, gris, azul claro)
- Tipografía Segoe UI
- Círculo de carga animado
- Barra de progreso dinámica

### 2. **Validaciones Automáticas**

#### Dependencias Python
- ✓ cv2 (OpenCV)
- ✓ numpy
- ✓ dlib
- ✓ PIL (Pillow)
- ✓ face_recognition
- ✓ tkinter

#### Hardware
- ✓ Cámara (OpenCV)
- ✓ Pantalla (Tkinter render)
- ✓ Servomotor (simulado)

#### Base de Datos
- ✓ Conexión SQLite
- ✓ Ubicación: `database/sqlite/students.db`

### 3. **Interfaz de Usuario**

```
┌─────────────────────────────────────────────┐
│ Inicializando sistema de acceso facial      │
│                                             │
│            ╔════════════════╗               │
│            ║      ◐         ║  (animado)    │
│            ╚════════════════╝               │
│                                             │
│          ████████████ 42%                   │
│                                             │
│ Verificaciones                              │
│ ─────────────────────────────────────────  │
│ ✓ cv2 (OpenCV)               OK             │
│ ✓ NumPy                      OK             │
│ ✓ dlib                       OK             │
│ ✓ Pillow                     OK             │
│ ◐ face_recognition      Verificando...     │
│                                             │
│ [Reintentar]  [Continuar a Interfaz ▶]    │
└─────────────────────────────────────────────┘
```

## Instalación

### Requisitos Previos

```bash
# Asegurar que estás en el entorno virtual
source activate_venv.sh  # En Linux/Mac
# o
activate_venv.bat  # En Windows
```

### Ejecutar la Verificación

```bash
# Desde la raíz del proyecto
python test_setup.py
```

## Estados de Verificación

| Estado | Icono | Color | Significado |
|--------|-------|-------|-------------|
| Verificando | ◐ | Azul Claro | En proceso |
| Éxito | ✓ | Azul Marino | Todo OK |
| Error | ✗ | Gris | Falló |

## Flujo de Uso

1. **Ejecutar el script**
   ```bash
   python test_setup.py
   ```

2. **Se inicia la interfaz gráfica**
   - Muestra un círculo de carga animado
   - Comienza a validar cada componente

3. **Si todo está OK**
   - Mensaje de confirmación
   - Botón "Continuar a Interfaz Principal"
   - Abre automáticamente `FaceLoginUI`

4. **Si hay errores**
   - Muestra lista de fallos
   - Botón "Reintentar" disponible
   - Instrucciones para instalar dependencias

## Integración con FaceLoginUI

El script intenta importar y ejecutar `FaceLoginUI` automáticamente:

```python
from login_ui import FaceLoginUI

app = FaceLoginUI()
app.mainloop()
```

### Archivo `login_ui.py`

Debe tener una clase `FaceLoginUI` que herede de `tk.Tk`:

```python
import tkinter as tk

class FaceLoginUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Acceso Facial")
        # ... resto de la interfaz
```

## Estructura del Código

### Clases Principales

#### `CheckStatus` (Enum)
Estados posibles de una verificación:
- `PENDING`: Pendiente
- `CHECKING`: En verificación
- `SUCCESS`: Exitosa
- `ERROR`: Error

#### `CheckResult` (Dataclass)
Resultado de una verificación con atributos:
- `name`: Nombre del componente
- `category`: Categoría (Dependencias, Hardware, Base de Datos)
- `status`: Estado actual
- `message`: Mensaje de estado
- `error_details`: Detalles del error

#### `SystemValidator`
Realiza todas las validaciones. Métodos principales:
- `validate_dependencies()`: Valida módulos Python
- `validate_camera()`: Verifica disponibilidad de cámara
- `validate_display()`: Valida renderizado de Tkinter
- `validate_servo()`: Simula verificación de servomotor
- `validate_database()`: Valida conexión SQLite
- `run_all_checks()`: Ejecuta todas las validaciones

#### `LoadingCircle` (Canvas)
Widget personalizado que dibuja un círculo animado.
- `start()`: Inicia la animación
- `stop()`: Detiene la animación

#### `CheckItemWidget` (Frame)
Widget que muestra el estado de una verificación.
- Icono con color según estado
- Nombre del componente
- Mensaje de estado

#### `SystemCheckUI` (tk.Tk)
Interfaz principal de la aplicación.
- Gestiona el flujo de validaciones
- Actualiza UI dinámicamente
- Maneja threading

## Características Técnicas

### Threading
Las validaciones se ejecutan en un thread separado para no bloquear la interfaz:
```python
thread = threading.Thread(target=self.validator.run_all_checks, daemon=True)
thread.start()
```

### Callbacks
Se usa un sistema de callbacks para actualizar la UI:
```python
self.validator = SystemValidator(self._on_check_result)
```

### Colores Definidos
```python
"bg_main": "#ffffff"        # Blanco
"bg_secondary": "#f5f5f5"   # Gris muy claro
"text_primary": "#333333"   # Texto oscuro
"text_secondary": "#666666" # Texto gris
"success": "#1f5b9f"        # Azul Marino (éxito)
"error": "#808080"          # Gris (error)
"checking": "#87ceeb"       # Azul Claro (verificando)
"accent": "#1f5b9f"         # Azul Marino (acento)
```

## Personalización

### Cambiar Colores
Editar en `_configure_styles()`:
```python
self.colors = {
    "success": "#1f5b9f",  # Cambiar a otro color
    # ...
}
```

### Agregar Nuevas Validaciones
1. Crear método en `SystemValidator`:
   ```python
   def validate_new_component(self) -> CheckResult:
       result = CheckResult(name="Nuevo", category="Hardware", status=CheckStatus.CHECKING)
       self.callback(result)
       # ... tu lógica ...
       self.callback(result)
       return result
   ```

2. Llamar en `run_all_checks()`:
   ```python
   all_results.append(self.validate_new_component())
   ```

## Solución de Problemas

### La interfaz no aparece (no hay display)
En sistemas sin entorno gráfico (servidor), Tkinter no puede mostrar ventanas.

### Dependencias no encontradas
Ejecutar: `pip install -r requirements.txt`

### Error de cámara
- Verificar que la cámara está conectada
- Probar: `cv2.VideoCapture(0)` en Python

### Error de base de datos
- Verificar permisos en `database/` folder
- Crear manualmente si es necesario

## Ejemplos de Uso

### Ejecutar desde línea de comandos
```bash
/home/carlos/Documentos/UNI/Identifyme/.venv/bin/python test_setup.py
```

### Ejecutar desde otro script
```python
import subprocess
subprocess.run([
    "/home/carlos/Documentos/UNI/Identifyme/.venv/bin/python",
    "test_setup.py"
])
```

## Notas Importantes

1. **Sin prints en consola**: Todos los mensajes aparecen en la UI
2. **Threading seguro**: Se usa `.after()` para actualizar UI desde threads
3. **Manejo de errores**: Información detallada en diálogos
4. **Integración automática**: Si `FaceLoginUI` existe, se abre automáticamente
5. **Modular y extensible**: Fácil agregar nuevas validaciones

## Próximos Pasos

1. Integrar completamente con `login_ui.py`
2. Agregar validaciones adicionales según sea necesario
3. Personalizar colores según branding
4. Traducir mensajes al español completo
5. Agregar logs a archivo
