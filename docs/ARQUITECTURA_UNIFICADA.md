# Arquitectura Unificada - Una Sola Ventana

## 📋 Resumen

Se ha refactorizado la aplicación para tener **una única ventana** en lugar de múltiples ventanas independientes. Todos los componentes (menú, login, registro) funcionan dentro de la misma ventana, navegando entre vistas diferentes.

## 🏗️ Estructura

### Archivo Principal: `app.py`

La aplicación está organizada en clases de control:

```
MainApplication (clase controllers)
├── MenuFrame (vista: menú principal)
├── LoginFrame (vista: reconocimiento facial de login)
└── RegisterFrame (vista: captura de usuario para registro)
```

### Punto de Entrada: `main.py`

Simplificado a 3 líneas que crean la ventana Tk e inicializa `MainApplication`.

## 🔄 Flujo de Navegación

```
Inicio
   ↓
[MenuFrame] ← Menú principal
   ├─→ "Iniciar Sesión" → [LoginFrame]
   │                            └─→ "Atrás" → [MenuFrame]
   │
   └─→ "Registrar Usuario" → [RegisterFrame]
                                  └─→ "Atrás" → [MenuFrame]
```

## 🎥 Gestión de Cámara

- **Centralizada**: `MainApplication.start_camera()` y `stop_camera()`
- **Compartida**: Una sola instancia de `cv2.VideoCapture`
- **Callback**: Cada frame procesa mediante `process_frame()` del frame actual
- **Segura**: Se detiene automáticamente al cambiar de vista

## 🧩 Componentes

### MenuFrame
- Botones para Login y Registro
- Interfaz de inicio
- Sin cámara

### LoginFrame
- Reconocimiento facial en tiempo real
- Canvas 480x360 para video
- Información del usuario detectado
- Estados: IDLE, WAITING, VERIFYING, GRANTED, DENIED, etc.

### RegisterFrame
- Captura de rostro para nuevo usuario
- Solicita nombre del usuario
- Canvas para vista previa
- Guarda encoding facial en `data/nombre.pkl`

## 📊 Tamaños

- **Ventana principal**: 640x480 (fija)
- **Canvas login**: 480x360
- **Canvas registro**: 610x200

## 🚀 Uso

```bash
python3 main.py
```

## ✅ Ventajas

1. **Una sola ventana**: Sin popup ni ventanas flotantes
2. **API simplificada**: `show_frame()` para navegar
3. **Gestión centralizada**: Cámara compartida
4. **Mejor UX**: Navegación fluida dentro de la ventana
5. **Mantenimiento**: Código más organizado y modular

## 📁 Archivos Actualizados

- ✅ `app.py` - NUEVO: Arquitectura completa unificada
- ✅ `main.py` - ACTUALIZADO: Punto de entrada simplificado
- ⚠️ `login.py` - Mantener para compatibilidad (si es necesario)
- ⚠️ `registrar.py` - Mantener para compatibilidad (si es necesario)

## 🔧 Extensión Futura

Para agregar nuevas vistas:

```python
class NuevaFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=BG_DARK)
        self.controller = controller
        # ... construir UI ...
    
    def on_show(self, **kwargs):
        # Se ejecuta cuando esta vista es mostrada
        pass
    
    def process_frame(self, frame):
        # Se ejecuta para cada frame de cámara (si está activa)
        pass

# En MainApplication._create_frames():
for F in (MenuFrame, LoginFrame, RegisterFrame, NuevaFrame):
    frame = F(container, self)
    # ...
```

Luego: `self.controller.show_frame("NuevaFrame")`
