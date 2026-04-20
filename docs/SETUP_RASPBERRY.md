# SETUP para Raspberry Pi / Debian 13

## Resumen de lo que se hizo para hacer funcionar el proyecto

Este documento describe cómo se configuró correctamente el proyecto de reconocimiento facial en una Raspberry Pi con Debian 13.

### 1. Dependencias del Sistema

Se instalaron las siguientes dependencias del sistema:
```bash
sudo apt-get update
sudo apt-get install -y git build-essential libopenblas-dev libblas-dev m4 cmake cython3 python3-dev
```

### 2. Entorno Virtual Python

El proyecto usa un entorno virtual Python 3.13 en `/home/pi/Desktop/identifyme/face-recognition/venv/`

### 3. Librerías Python Instaladas

- **numpy** - Computación numérica
- **opencv-python** - Visión por computadora (v4.13.0)
- **dlib** - Algoritmos de ML (v20.0.0)
- **face_recognition** - Reconocimiento facial (v1.3.0)
- **face_recognition_models** - Modelos preentrenados (v0.3.0)
- **Pillow** - Procesamiento de imágenes

### 4. Problema Resuelto: pkg_resources

**Problema:** `face_recognition_models` importaba `pkg_resources` que no estaba disponible, causando el error:
```
Please install `face_recognition_models` with this command before using `face_recognition`:
pip install git+https://github.com/ageitgey/face_recognition_models
```

**Solución:** Se reemplazó el archivo `face_recognition_models/__init__.py` con una versión que usa `importlib.resources` (enfoque moderno de Python 3.9+) en lugar de `pkg_resources` (anticuado).

### 5. Cómo Usar el Proyecto

**Activar el entorno virtual:**
```bash
source /home/pi/Desktop/identifyme/face-recognition/venv/bin/activate
```

**Registrar un nuevo usuario:**
```bash
python registrar.py
```
- Se abrirá la cámara
- Coloca tu rostro dentro del óvalo guía
- Presiona `S` para guardar
- Se creará un archivo `data/<nombre>.pkl`

**Iniciar sesión:**
```bash
python login.py
```
- El sistema buscará tu rostro en la base de datos
- Presiona `q` para cerrar

**Verificar instalación:**
```bash
python test.py
```

### 6. Notas Importantes

- El proyecto está completamente funcional en Raspberry Pi con Debian 13
- Usa buena iluminación para mejores resultados
- Os archivos `.pkl` se guardan en la carpeta `data/`
- La cámara debe estar disponible como `/dev/video0`
- El proyecto requiere Python 3.7+

### 7. Composición Final del Entorno

```
venv/
├── bin/
│   ├── python
│   └── pip
├── lib/python3.13/site-packages/
│   ├── cv2/                          # OpenCV
│   ├── face_recognition/             # Face Recognition
│   ├── face_recognition_models/      # Models (CORREGIDO)
│   ├── dlib/                         # Dlib
│   ├── numpy/                        # NumPy
│   ├── PIL/                          # Pillow
│   └── ...
```

---
**Fecha de Setup:** 11 de Marzo de 2026
**Sistema:** Raspberry Pi / Debian 13
**Python:** 3.13.5
