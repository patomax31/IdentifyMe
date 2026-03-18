# Face Recognition Biometric Login

Sistema biométrico facial embebido para la identificación y verificación de usuarios a partir de imágenes faciales capturadas por una cámara digital.

## 📌 Estructura del proyecto

- `login.py` – Módulo de ejecución para iniciar el sistema de login por reconocimiento facial.
- `registrar.py` – Script para registrar un nuevo usuario (extrae y guarda su encoding facial).
- `data/` – Carpeta donde se almacenan los archivos `.pkl` con los encodings de cada usuario.
- `database/script.sql` – Esquema SQLite del sistema.
- `database/face_recognition.db` – Base de datos SQLite generada automaticamente al ejecutar el sistema.
- `test.py` – Verifica que las librerías necesarias (OpenCV, dlib, numpy) estén instaladas.

## ✅ Requisitos (dependencias)

Este proyecto funciona mejor dentro de un entorno virtual de Python para evitar conflictos con otras librerías del sistema.

### 1) Crear y activar un entorno virtual (recomendado)

#### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Windows (CMD)
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

> 💡 Si no activas un venv, los paquetes pueden instalarse globalmente y podrías tener problemas al ejecutar los scripts.

### 2) Instalar dependencias

```bash
pip install opencv-python face_recognition dlib numpy
```

> 🔍 `face_recognition` depende de `dlib`, que a su vez requiere compilación en algunos sistemas. Si tienes problemas en Windows, busca instalación de `dlib` con ruedas precompiladas.

## 🗄️ Base de datos SQLite

- El sistema inicializa automaticamente la base de datos desde `database/script.sql`.
- El registro guarda biometria en SQLite (tabla `datos_biometricos`) y conserva un respaldo en `data/*.pkl`.
- Al iniciar login, los `.pkl` existentes se migran automaticamente a SQLite.

## 🚀 Uso

### 1) Registrar un usuario

Ejecuta el script de registro y sigue las instrucciones en pantalla:

```bash
python registrar.py
```

- Se abrirá la cámara y verás un óvalo guía.
- Coloca tu rostro dentro del óvalo.
- Presiona `S` para capturar y guardar el encoding.
- El encoding se guardará como `data/<nombre>.pkl`.

### 2) Iniciar la sesión (login)

Ejecuta el script de login:

```bash
python login.py
```

- El sistema buscará tu rostro en la base de datos (los archivos `.pkl` en `data/`).
- Si encuentra una coincidencia, mostrará `ACCESO CONCEDIDO` con el nombre.
- Si no, mostrará `ACCESO DENEGADO`.
- Presiona `q` para cerrar la ventana.

## 🧪 Verificar la instalación

Puedes verificar que las librerías estén correctamente instaladas ejecutando:

```bash
python test.py
```

## 📌 Notas

- Usa buena iluminación para mejorar la detección facial.
- Asegúrate de que solo haya un rostro en el cuadro al capturar el encoding.
- Si tienes problemas con la cámara, prueba con otro dispositivo o controla que no esté siendo utilizada por otra aplicación.
