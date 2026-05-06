# Sistema de Verificación de Dependencias - Interfaz Gráfica Moderna

## 🎯 Objetivo

Sistema automatizado de verificación de dependencias con interfaz gráfica moderna (splash screen) usando Tkinter. Valida que todos los componentes necesarios para el sistema de reconocimiento facial estén disponibles antes de iniciar la aplicación principal.

## ✨ Características Principales

### 1. Interfaz Moderna y Responsiva
- Diseño limpio con Tkinter
- Colores profesionales (azul marino, gris, azul claro)
- Tipografía moderna (Segoe UI)
- **No bloquea la interfaz** durante las validaciones (threading)

### 2. Validaciones Exhaustivas

#### Dependencias Python (6 módulos)
```
✓ cv2 (OpenCV)
✓ NumPy
✓ dlib
✓ PIL (Pillow)
✓ face_recognition
✓ Tkinter
```

#### Hardware
```
✓ Cámara (verificada con OpenCV)
✓ Pantalla (verificada con Tkinter)
✓ Servomotor (simulado/mockeable)
```

#### Base de Datos
```
✓ Conexión SQLite
✓ Ubicación automática: database/sqlite/students.db
```

### 3. Elementos Visuales

- **Círculo de carga animado** con rotación suave
- **Barra de progreso** que se actualiza en tiempo real
- **Indicador de porcentaje** de verificaciones completadas
- **Iconos dinámicos**: 
  - `◐` (verificando - azul claro)
  - `✓` (éxito - azul marino)
  - `✗` (error - gris)
- **Lista scrolleable** de verificaciones

### 4. Manejo de Errores

- Mensaje detallado si hay fallos
- Botón "Reintentar" para reiniciar verificaciones
- Información del error para cada componente fallido
- Integración con cuadros de diálogo (messagebox)

### 5. Integración Automática

- Abre automáticamente `FaceLoginUI` si la verificación es exitosa
- Permite ejecutar con/sin verificación (`--skip-check`)

## 📁 Archivos Incluidos

```
test_setup.py
├── SystemCheckUI (tk.Tk)         # Interfaz principal
├── SystemValidator               # Validaciones
├── LoadingCircle (tk.Canvas)      # Círculo animado
└── CheckItemWidget (tk.Frame)     # Item de verificación

GUIA_SYSTEM_CHECK.md              # Documentación detallada
system_check_integration_example.py # Ejemplo de integración
```

## 🚀 Inicio Rápido

### 1. Asegurar el Entorno Virtual

```bash
# Linux/Mac
source activate_venv.sh

# Windows
activate_venv.bat
```

### 2. Ejecutar la Verificación

```bash
python test_setup.py
```

### 3. Flujo Típico

```
Ejecutar test_setup.py
        ↓
[Interfaz gráfica inicia]
        ↓
[Círculo animado + validaciones]
        ↓
¿Todo OK?
├─→ SÍ: "Sistema listo" → [Botón: Continuar]
└─→ NO: "Errores encontrados" → [Botón: Reintentar]
        ↓
[Si continúa] Abre FaceLoginUI
```

## 💻 Uso Programático

### Ejecutar con verificación
```bash
python test_setup.py
```

### Ejecutar saltando verificación
```bash
python system_check_integration_example.py --skip-check
```

### Desde otro script
```python
import subprocess
import sys

# Opción 1: Con verificación
subprocess.run([sys.executable, "test_setup.py"])

# Opción 2: Importar directamente
from test_setup import SystemCheckUI
app = SystemCheckUI()
app.mainloop()
```

## 🎨 Personalización

### Cambiar Colores

En `test_setup.py`, método `_configure_styles()`:

```python
self.colors = {
    "bg_main": "#ffffff",           # Fondo principal
    "bg_secondary": "#f5f5f5",      # Fondo secundario
    "success": "#1f5b9f",           # Azul Marino (éxito)
    "error": "#808080",             # Gris (error)
    "checking": "#87ceeb",          # Azul Claro (verificando)
}
```

### Agregar Nueva Validación

1. Crear método en `SystemValidator`:

```python
def validate_nuevo_componente(self) -> CheckResult:
    result = CheckResult(
        name="Mi Componente",
        category="Categoría",
        status=CheckStatus.CHECKING
    )
    self.callback(result)  # Notificar UI
    
    # Tu lógica de validación
    try:
        # ...validar...
        result.status = CheckStatus.SUCCESS
    except Exception as e:
        result.status = CheckStatus.ERROR
        result.error_details = str(e)
    
    self.callback(result)
    return result
```

2. Llamar en `run_all_checks()`:

```python
all_results.append(self.validate_nuevo_componente())
```

## 🔍 Estructura del Código

### Enumeración: CheckStatus
Estados posibles de cada verificación:
- `PENDING`: Pendiente de verificar
- `CHECKING`: En proceso
- `SUCCESS`: Completado exitosamente
- `ERROR`: Error

### Dataclass: CheckResult
Representa el resultado de una verificación:
- `name`: str - Nombre del componente
- `category`: str - Categoría (Dependencias, Hardware, etc)
- `status`: CheckStatus - Estado actual
- `message`: str - Mensaje descriptivo
- `error_details`: str - Detalles del error

### Clase: SystemValidator
Realiza todas las validaciones:
- `validate_dependencies()` - Módulos Python
- `validate_camera()` - Disponibilidad de cámara
- `validate_display()` - Renderizado de Tkinter
- `validate_servo()` - Servomotor
- `validate_database()` - Conexión SQLite
- `run_all_checks()` - Todas las validaciones

### Clase: LoadingCircle
Widget Canvas personalizado:
- `start()` - Inicia animación
- `stop()` - Detiene animación
- Dibuja círculo rotativo suavemente

### Clase: CheckItemWidget
Frame que muestra estado de verificación:
- Icono con color dinámico
- Nombre del componente
- Estado y mensaje de error
- Separador visual

### Clase: SystemCheckUI (tk.Tk)
Interfaz principal:
- `_create_widgets()` - Construye UI
- `_start_validation()` - Inicia verificaciones en thread
- `_update_check_result()` - Actualiza UI seguramente
- `_on_validation_complete()` - Maneja fin de validaciones
- `_on_continue()` - Abre FaceLoginUI

## 🔧 Características Técnicas

### Threading Seguro
Las validaciones se ejecutan en thread separado:
```python
thread = threading.Thread(
    target=self.validator.run_all_checks,
    daemon=True
)
thread.start()
```

Actualizaciones de UI se hacen con `.after()`:
```python
self.after(0, lambda: self._update_check_result(result))
```

### Callbacks
Sistema de callbacks para comunicación:
```python
validator = SystemValidator(callback=self._on_check_result)
```

### Sin Bloqueo
- Interfaz receptiva en todo momento
- Animación suave del círculo
- Barra de progreso actualizada
- Cancelable en cualquier momento

## ⚙️ Requisitos

### Dependencias Base
- Python 3.7+
- tkinter (incluido en Python)

### Dependencias a Validar
Que serán validadas por el sistema:
- opencv-python (cv2)
- numpy
- dlib
- pillow
- face_recognition

### Sistema Operativo
- ✓ Linux
- ✓ Windows
- ✓ macOS

## 🐛 Solución de Problemas

### "No display" en servidor sin GUI
Normal en entornos sin X11. El script validará correctamente pero no mostrará la ventana.

### Dependencias no encontradas
```bash
pip install opencv-python numpy dlib pillow face_recognition
```

### Cámara no detectada
- Verificar conexión física
- Probar: `python -c "import cv2; cv2.VideoCapture(0).isOpened()"`

### Error de permisos base de datos
```bash
chmod 755 database/
chmod 755 database/sqlite/
```

## 📊 Ejemplo de Salida

### Caso Exitoso
```
┌─────────────────────────────────────────┐
│ Inicializando sistema de acceso facial  │
│                                         │
│        Círculo de carga animado         │
│                                         │
│     ████████████████ 100%               │
│                                         │
│ Verificaciones                          │
│ ✓ cv2 (OpenCV)             OK           │
│ ✓ NumPy                    OK           │
│ ✓ dlib                     OK           │
│ ✓ Pillow                   OK           │
│ ✓ face_recognition         OK           │
│ ✓ Tkinter                  OK           │
│ ✓ Cámara                   OK           │
│ ✓ Pantalla                 OK           │
│ ✓ Servomotor              OK (Simulado) │
│ ✓ Base de Datos            OK           │
│                                         │
│ ✓ Sistema listo                         │
│                                         │
│ [Continuar a Interfaz Principal]        │
└─────────────────────────────────────────┘
```

### Caso con Errores
```
✗ dlib                     Error
✗ Base de Datos            Error - Permission denied

[Reintentar]
```

## 📝 Notas Importantes

1. **Sin prints en consola** - Todo se muestra en la interfaz gráfica
2. **Threading seguro** - No hay race conditions
3. **Modular y extensible** - Fácil agregar nuevas validaciones
4. **Integración automática** - Abre FaceLoginUI si existe
5. **Manejo completo de errores** - Información detallada del fallo
6. **Performance** - Validaciones rápidas (~5 segundos total)

## 🔗 Integración con Proyecto

### Con `login_ui.py`
```python
# En test_setup.py, cerca de línea 560:
from login_ui import FaceLoginUI

# Se ejecuta automáticamente si todo está OK
app = FaceLoginUI()
app.mainloop()
```

### Con `main.py`
```python
# En main.py:
from test_setup import SystemCheckUI

def main():
    app = SystemCheckUI()
    app.mainloop()

if __name__ == "__main__":
    main()
```

## 🚀 Próximos Pasos

- [ ] Integrar completamente con `login_ui.py`
- [ ] Agregar logs a archivo
- [ ] Traducir completamente al español
- [ ] Agregar configuración en archivo `.env`
- [ ] Incluir tests unitarios
- [ ] Documentación de API

## 📞 Soporte

Para problemas o sugerencias, consulta:
- `GUIA_SYSTEM_CHECK.md` - Documentación detallada
- `system_check_integration_example.py` - Ejemplo de integración
- Código comentado en `test_setup.py`

---

**Versión**: 1.0.0  
**Última actualización**: Abril 2026  
**Estado**: ✓ Producción
