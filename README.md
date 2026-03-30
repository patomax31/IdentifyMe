# Face Recognition Biometric Login

Sistema biométrico facial embebido para la identificación y verificación de usuarios a partir de imágenes faciales capturadas por una cámara digital.

## 📌 Estructura del proyecto

- `login.py` – Módulo de ejecución para iniciar el sistema de login por reconocimiento facial.
- `registrar.py` – Script para registrar un nuevo estudiante (grupo + biometria facial).
- `data/` – Carpeta de respaldo con archivos `.pkl` (formato `est_<id>.pkl`).
- `database/script.sql` – Esquema SQLite del sistema.
- `database/face_recognition.db` – Base de datos SQLite generada automaticamente al ejecutar el sistema.
- `database/sqlite_manager.py` – Gestor de operaciones BD (creación de estudiantes, guardado de biometria, registros de acceso).
- `test.py` – Verifica que las librerías necesarias (OpenCV, dlib, numpy) estén instaladas.
- `venv/` – Entorno virtual de Python (se crea automáticamente con los siguientes pasos).

---

## 🚀 Instalación Rápida desde GitHub

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/face-recognition.git
cd face-recognition
```

### Paso 2: Crear el entorno virtual

El entorno virtual **debe crearse con acceso a librerías del sistema** para que funcione correctamente en Raspberry Pi:

#### En Raspberry Pi / Linux:
```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

#### En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### En Windows (CMD):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### En macOS:
```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

> ⚠️ **Importante:** El flag `--system-site-packages` es CRÍTICO en Raspberry Pi porque permite acceso a librerías del sistema operativo (libcamera, libpicamera2) que no están disponibles en PyPI.

### Paso 3: Instalar dependencias

```bash
pip install --upgrade pip
pip install opencv-python face-recognition dlib numpy
```

> 📌 `face-recognition` depende de `dlib`, que requiere compilación. En Raspberry Pi esto puede tomar 10-20 minutos. Sea paciente.

**Si la compilación de dlib falla en Raspberry Pi**, intente usar piwheels:
```bash
pip install --upgrade pip
pip install --index-url https://www.piwheels.org/simple opencv-python face-recognition numpy
```

### Paso 4: Instalar dependencias del sistema (Raspberry Pi)

Si está en Raspberry Pi, instale también las librerías de cámara:

```bash
sudo apt-get update
sudo apt-get install -y python3-libcamera python3-picamera2
```

### Paso 5: Verificar la instalación

```bash
python test.py
```

Si todo está correcto verá un mensaje indicando que todas las librerías se importan sin errores.

---

## ✅ Requisitos previos

- **Python 3.10 o superior**
- **pip** actualizado
- **en Raspberry Pi**: acceso sudo (para instalar libcamera)
- **Cámara conectada y funcional**

---

## 🧪 Probar el proyecto

### 1) Verificar que todo está listo

```bash
# Asegúrate de que el venv está activado
source venv/bin/activate  # Linux/Mac
# ó
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Verifica que importan todas las librerías
python -c "import cv2, face_recognition, numpy; print('✓ Listo para usar')"
```

### 2) Registrar un estudiante (primera vez)

```bash
python registrar.py
```

**Instrucciones en pantalla:**
- Ingresa grado (1-3), letra del grupo (A-Z) y turno (MATUTINO/VESPERTINO)
- Se abrirá la cámara con un óvalo guía
- Coloca tu rostro dentro del óvalo (bien iluminado)
- Presiona `S` para capturar
- Presiona `Q` para salir sin guardar

El sistema guardará automáticamente:
- La biometria en SQLite (`database/face_recognition.db`)
- Un respaldo en formato `.pkl` en la carpeta `data/`

### 3) Probar el login

```bash
python login.py
```

**Lo que verás:**
- La cámara se abre con un óvalo guía
- Si detecta un rostro registrado: `ACCESO CONCEDIDO` (verde)
- Si no reconoce el rostro: `ACCESO DENEGADO` (rojo)
- Presiona `Q` para salir

---

## 🔧 Activar y Desactivar el Entorno Virtual

### Activar el venv

#### Linux / macOS:
```bash
source venv/bin/activate
```

#### Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

#### Windows (CMD):
```cmd
venv\Scripts\activate.bat
```

**Verifica que está activado:** debería aparecer `(venv)` al inicio de tu línea de comandos.

### Desactivar el venv

En **cualquier sistema operativo**:
```bash
deactivate
```

---

## 🗄️ Base de datos SQLite

- **Ubicación:** `database/face_recognition.db`
- **Esquema:** `database/script.sql`
- **Inicialización:** Se crea automáticamente al ejecutar `registrar.py` o `login.py`

### Tablas principales:
- `estudiantes` – Información del estudiante (grado, letra, turno)
- `datos_biometricos` – Encoding facial almacenado (BLOB)
- `bitacora_accesos` – Registro de intentos de login (fecha, hora, usuario, resultado)

---

## 🐛 Troubleshooting: Solucionar problemas comunes

### ❌ Error: `ModuleNotFoundError: No module named 'libcamera'`

**Causa:** El venv no está accediendo a las librerías del sistema (Raspberry Pi).

**Solución:**

1. Elimina el venv actual:
```bash
deactivate  # Primero desactiva el venv
rm -rf venv
```

2. Recrea el venv **CON** `--system-site-packages`:
```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

3. Reinstala las dependencias Python:
```bash
pip install --upgrade pip
pip install opencv-python face-recognition dlib numpy
```

4. Verifica que funciona:
```bash
python login.py
```

### ❌ Error: `ModuleNotFoundError: No module named 'face_recognition'`

**Causa:** Las dependencias no están instaladas en el venv.

**Solución:**

```bash
# Asegúrate de que el venv está activado
source venv/bin/activate

# Reinstala las dependencias
pip install --upgrade pip setuptools wheel
pip install opencv-python face-recognition dlib numpy
```

**Si la compilación de dlib toma mucho tiempo (>30 min):**
- Deténlo con `Ctrl+C`
- Usa piwheels en Raspberry Pi:
```bash
pip install --index-url https://www.piwheels.org/simple face-recognition
```

### ❌ Error: `Camera initialization failed` / Problemas con la cámara

**Causa:** La cámara no está conectada, no tiene permisos, u otra aplicación la usa.

**Soluciones:**

```bash
# Verifica que la cámara está disponible (Linux)
ls -la /dev/video* 

# Cierra otras aplicaciones que usen la cámara
# Intenta dar permisos (si es necesario)
sudo chmod 666 /dev/video0

# Reinicia el script
python login.py
```

### ❌ Error: `dlib compilation failed` (Raspberry Pi)

**Causa:** El compilador o dependencias de desarrollo faltan.

**Solución:**

```bash
# Instala dependencias de compilación
sudo apt-get install -y build-essential python3-dev

# Luego intenta reinstalar
pip install dlib --no-cache-dir
```

### ❌ El venv sigue apuntando a la ruta incorrecta (después de clonar)

**Síntoma:** Errores de libcamera incluso después de crear el venv.

**Causa:** Python sigue cachés o puntos de montaje del venv anterior.

**Solución nuclear (garantizada):**

```bash
# Desactiva el venv actual
deactivate 2>/dev/null

# Elimina completamente el venv
rm -rf venv

# Limpia caché de Python
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Crea el venv completamente nuevo
python3 -m venv --system-site-packages venv

# Activa
source venv/bin/activate

# Reinstala todo desde cero
pip install --upgrade pip setuptools wheel
pip install opencv-python face-recognition dlib numpy

# Verifica que funciona
python -c "import cv2, face_recognition; print('✓ Correcto')"
```

---

## 🔄 Cambiar entre ramas de Git

Si estás trabajando con varias ramas (como `kevin` y `VictorRama`), **el venv funciona para todas**:

```bash
# Ver rama actual
git branch

# Cambiar de rama (el venv se mantiene)
git checkout VictorRama
git checkout kevin

# Activar venv (igual para todas las ramas)
source venv/bin/activate

# Ejecutar
python login.py
```

---

## 📌 Notas generales de uso

- **Iluminación:** Usa buena iluminación frontal para mejorar la detección facial.
- **Rostros:** Asegúrate de que solo haya UN rostro en el cuadro al capturar el encoding.
- **Tolerancia:** El reconocimiento funciona en ángulos 0-45°. Enfrenta la cámara directamente.
- **Cámara múltiple:** Si tienes más de una cámara conectada, el sistema usa la primera disponible.
- **Base de datos:** Los datos se guardan automáticamente en SQLite. No necesitas hacer configuración adicional.
- Variables opcionales de rendimiento: `CAMERA_WIDTH`, `CAMERA_HEIGHT`, `CAMERA_FPS`.
