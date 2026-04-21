# Face Recognition Biometric Login

Sistema biométrico facial embebido para la identificación y verificación de usuarios a partir de imágenes faciales capturadas por una cámara digital.

## 📌 Estructura del proyecto

- `login.py` – Módulo de ejecución para iniciar el sistema de login por reconocimiento facial.
- `registrar.py` – Script para registrar un nuevo estudiante (grupo + biometria facial).
- `src/` – Nueva arquitectura modular (en adopcion progresiva):
	- `src/core/` – Configuracion compartida.
	- `src/domain/` – Puertos (interfaces) del dominio para desacoplar servicios de la infraestructura.
	- `src/application/` – Servicios/casos de uso de alto nivel.
	- `src/infrastructure/camera/` – Adaptadores de camara OpenCV.
	- `src/infrastructure/recognition/` – Motor de reconocimiento facial.
	- `src/infrastructure/persistence/` – Repositorio de persistencia (SQLite adapter).
- `data/` – Carpeta de respaldo con archivos `.pkl` (formato `est_<id>.pkl`).
- `database/script.sql` – Esquema SQLite del sistema.
- `database/face_recognition.db` – Base de datos SQLite generada automaticamente al ejecutar el sistema.
- `test.py` – Verifica que las librerías necesarias (OpenCV, dlib, numpy) estén instaladas.

### Estado actual de modularizacion

- `login.py` y `registrar.py` ya delegan en modulos de `src/` para camara, reconocimiento y servicios de aplicacion.
- `database/sqlite_manager.py` funciona como fachada de compatibilidad.
- La implementacion SQLite se separo por responsabilidad en `database/sqlite/`:
	- `connection.py` (conexion),
	- `migrations.py` (inicializacion/migracion),
	- `students.py` (consultas de estudiantes y biometria),
	- `access.py` (bitacora de accesos),
	- `encoding.py` (serializacion de vectores faciales),
	- `paths.py` (rutas del motor local).
- `src/infrastructure/persistence/sqlite_repository.py` permanece como adaptador usado por servicios de aplicacion.

## ✅ Requisitos (dependencias)

Este proyecto funciona mejor dentro de un entorno virtual de Python para evitar conflictos con otras librerías del sistema.

### Configuración automática en Windows (recomendada)

Puedes configurar todo el entorno en un solo paso (crea `.venv`, instala dependencias y valida imports):

```powershell
.\setup_windows.ps1
```

También puedes usar el lanzador para CMD o doble clic:

```cmd
setup_windows.bat
```

Opcionalmente, para recrear el entorno desde cero:

```powershell
.\setup_windows.ps1 -ForceRecreate
```

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
- El registro guarda biometria en SQLite (tabla `datos_biometricos`) para `ESTUDIANTE` y conserva un respaldo en `data/*.pkl`.
- En la version local, el login usa SQLite como fuente principal y solo usa `.pkl` como compatibilidad si aun no hay biometria en BD.

## 🚀 Uso

### 1) Registrar un estudiante

Ejecuta el script de registro y sigue las instrucciones en pantalla:

```bash
python registrar.py
```

- Se abrirá la cámara y verás un óvalo guía.
- Captura primero los datos del grupo: grado, letra y turno.
- Coloca tu rostro dentro del óvalo.
- Presiona `S` para capturar y guardar el encoding.
- El encoding se guardará en SQLite y en `data/est_<id>.pkl` como respaldo.

### 2) Iniciar la sesión (login)

Ejecuta el script de login:

```bash
python login.py
```

- El sistema buscará el rostro en SQLite (estudiantes activos).
- Si encuentra una coincidencia, mostrará `ACCESO CONCEDIDO` con grupo e identificador interno.
- Si no, mostrará `ACCESO DENEGADO`.
- Presiona `q` para cerrar la ventana.

## 🧪 Verificar la instalación

Puedes verificar que las librerías estén correctamente instaladas ejecutando:

```bash
python test.py
```

## ✅ Pruebas unitarias (arquitectura modular)

Se incluyeron pruebas unitarias para los servicios de aplicacion en `tests/`.

Ejecuta:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Cobertura actual de pruebas:

- Delegacion de inicializacion de servicios hacia el repositorio.
- Carga de estudiantes conocidos en autenticacion.
- Registro de bitacora de acceso en autenticacion.
- Flujo de registro de estudiante + persistencia de biometria.
- Integracion SQLite para `students.py` (crear/cargar biometria).
- Integracion SQLite para `access.py` (persistencia y validacion de tipo de usuario).

## 📌 Notas

- Usa buena iluminación para mejorar la detección facial.
- Asegúrate de que solo haya un rostro en el cuadro al capturar el encoding.
- Si tienes problemas con la cámara, prueba con otro dispositivo o controla que no esté siendo utilizada por otra aplicación.

### Troubleshooting rápido (Windows)

- Si aparece `Please install face_recognition_models...`, instala siempre con el Python del entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install face_recognition_models
```

- Si luego aparece error de `pkg_resources`, fija `setuptools` a una versión compatible:

```powershell
.\.venv\Scripts\python.exe -m pip install "setuptools<81"
```
