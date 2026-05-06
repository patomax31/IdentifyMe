# 🚀 GUÍA RÁPIDA DE INICIO

## Instalación Rápida

### Opción 1: Ejecutar directamente (Recomendado)

```bash
cd /home/carlos/Documentos/UNI/Identifyme/face-recognition
bash run.sh
```

### Opción 2: Manual

```bash
cd /home/carlos/Documentos/UNI/Identifyme/face-recognition
source venv/bin/activate
python main.py
```

---

## 📱 Usando la Aplicación

### Pantalla Principal

Verás dos opciones:

1. **🔓 INICIAR SESIÓN**
   - Haz clic para acceder con reconocimiento facial
   - Se abrirá una nueva ventana con:
     - Cámara en tiempo real (640x480)
     - Mensajes dinámicos
     - Información del usuario

2. **✏ REGISTRAR NUEVO USUARIO**
   - Haz clic para registrar un nuevo usuario
   - Sigue estos pasos:
     - Ingresa tu nombre
     - Haz clic en "Iniciar Captura"
     - Centra tu rostro en el óvalo
     - Haz clic en "Capturar"

---

## 🎥 Pantalla de Login

### Elementos Principales:

```
┌─────────────────────────────────────┐
│   🔐 SISTEMA DE ACCESO FACIAL      │ <- Encabezado verde
├─────────────────────────────────────┤
│                                     │
│         [CÁMARA 640x480]           │ <- Video en vivo
│      Óvalo verde guía              │
│                                     │
├─────────────────────────────────────┤
│ Nombre: ---                        │ <- Cuando se detecta
│ Salón: ---                         │    usuario
│ Edad: ---                          │
│ ID: ---                            │
├─────────────────────────────────────┤
│ ESPERANDO ROSTRO...                │ <- Mensaje dinámico
├─────────────────────────────────────┤
│ [▶ Iniciar] [⏹ Detener] [✕ Cerrar]│ <- Botones
└─────────────────────────────────────┘
```

### Estados y Mensajes:

| Estado | Mensaje | Color |
|--------|---------|-------|
| Esperando | "ESPERANDO ROSTRO..." | Verde |
| Detectando | "DETECTANDO ROSTRO..." | Verde claro |
| Verificando | "VERIFICANDO..." | Naranja |
| Posicionamiento | "CENTRA TU ROSTRO" | Verde |
| Acceso Permitido | "✓ ACCESO CONCEDIDO" | Verde brillante |
| Acceso Denegado | "✗ ACCESO DENEGADO" | Rojo |
| Error | "ERROR AL VERIFICAR" | Rojo |

---

## 🎨 Pantalla de Registro

### Paso 1: Ingres ar Nombre
```
┌─────────────────────────────────────┐
│ ✏ REGISTRO FACIAL                  │
├─────────────────────────────────────┤
│ Información del Usuario             │
│ Nombre: [____________] [Continuar]  │
├─────────────────────────────────────┤
│ Instrucciones                       │
│ ✓ Buena iluminación                │
│ ✓ Rostro visible                   │
│ ✓ 30-50cm de distancia             │
└─────────────────────────────────────┘
```

### Paso 2: Captura de Rostro
```
┌─────────────────────────────────────┐
│ ✏ REGISTRO FACIAL                  │
├─────────────────────────────────────┤
│                                     │
│     [CÁMARA 640x480]               │
│    Óvalo verde guía                │
│                                     │
├─────────────────────────────────────┤
│ [▶ Iniciar] [📸 Capturar] [⏹ Detener]
└─────────────────────────────────────┘
```

---

## 🔒 Características de Seguridad

✅ **Reconocimiento Facial**: Utiliza face_recognition con dlib
✅ **Detección de un rostro**: Solo se permite 1 rostro por sesión
✅ **Cooldown de acceso**: 3 segundos entre intentos
✅ **Validación de nombre**: Solo letras y números
✅ **Confirmación**: Pregunta antes de reemplazar usuario

---

## 📁 Estructura de Archivos

```
face-recognition/
├── main.py              ← Punto de entrada principal
├── login.py             ← Interfaz de login (FaceLoginUI)
├── registrar.py         ← Interfaz de registro (FaceRegisterUI)
├── test_setup.py        ← Verifica dependencias
├── test_integration.py  ← Tests de las clases
├── run.sh               ← Script de ejecución
├── data/                ← Carpeta de usuarios registrados
│   ├── usuario1.pkl
│   ├── usuario2.pkl
│   └── ...
├── venv/                ← Virtual environment
└── MEJORAS.md           ← Documentación técnica
```

---

## 🐛 Solución de Problemas

### Error: "No se puede acceder a la cámara"
- Verifica que ninguna otra aplicación esté usando la cámara
- Reinicia la aplicación
- Intenta: `sudo modprobe -r uvcvideo && sudo modprobe uvcvideo`

### Error: "No hay usuarios registrados"
- Registra al menos un usuario primero
- Verifica que los archivos `.pkl` estén en `data/`

### Cámara lenta o con lag
- Cierra otras aplicaciones
- Reduce la iluminación de fondo
- Intenta acercarte más a la cámara

### La interfaz se ve pequeña o grande
- La aplicación asume una resolución de pantalla estándar
- Puedes ajustar el `geometry()` en `main.py`, `login.py` y `registrar.py`

---

## 📊 Colores de la Interfaz

```python
Verde oscuro     → #008f39    (Primario)
Verde medio      → #48a259    (Secundario)
Verde claro      → #70b578    (Terciario)
Verde muy claro  → #95c799    (Acento)
Rojo            → #ef4444     (Error/Denegado)
Naranja         → #f97316     (Verificando)
Blanco          → #ffffff     (Texto)
```

---

## 🧪 Ejecutar Tests

### Verificar Dependencias:
```bash
source venv/bin/activate
python test_setup.py
```

### Tests de Integración:
```bash
source venv/bin/activate
python test_integration.py
```

---

## 📝 Notas Importantes

1. **Primer uso**: Registra al menos un usuario antes de intentar login
2. **Iluminación**: Buena iluminación mejora la precisión
3. **Formato**: Los nombres se guardan en minúsculas (ej: "juan" → data/juan.pkl)
4. **Seguridad**: Los encodings faciales están protegidos en archivos .pkl

---

## ✅ Checklist Antes de Usar

- [ ] Python 3.11+ instalado
- [ ] Virtual environment creado (`venv/`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Cámara conectada y funcionando
- [ ] Buena iluminación disponible

---

## 🎓 Para Desarrolladores

### Modificar colores:
Edita las constantes en `login.py`, `registrar.py` y `main.py`:
```python
COLOR_PRIMARY = "#008f39"      # Cambia aquí
```

### Agregar campos a usuario:
En `login.py`, línea ~150:
```python
self.user_data = {
    "nombre": name,
    "id": user_id,
    "salon": "---",
    "edad": "---",
    "tu_campo": "valor"  # Añade aquí
}
```

### Cambiar resolución de video:
Busca todas las instancias de `640, 480` y cambia:
```python
frame = cv2.resize(frame, (NEW_WIDTH, NEW_HEIGHT))
```

---

## 📞 Soporte

Para problemas específicos:
1. Revisa `MEJORAS.md` para documentación técnica
2. Ejecuta `test_integration.py` para verificar integridad
3. Verifica que `face_recognition_models` tenga los archivos .dat

---

**Versión**: 2.0  
**Última actualización**: 15 de Abril de 2026  
**Estado**: ✅ Producción

