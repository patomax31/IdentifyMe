# Guia de Instalacion (Windows)

Esta guia instala todo lo necesario para ejecutar el proyecto de reconocimiento facial en Windows usando PowerShell.

## 1. Ir a la carpeta del proyecto

```powershell
cd C:\Users\valdo\OneDrive\Escritorio\FIE\face-recognition
```

## 2. Crear entorno virtual

Si no existe `venv`:

```powershell
python -m venv venv
```

## 3. Activar entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloquea scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4. Actualizar herramientas base de Python

```powershell
python -m pip install --upgrade pip setuptools wheel
```

## 5. Instalar librerias principales

```powershell
pip install numpy opencv-python pillow click
```

## 6. Instalar CMake

Verifica primero:

```powershell
cmake --version
```

Si no existe, instala con winget:

```powershell
winget install -e --id Kitware.CMake --accept-source-agreements --accept-package-agreements
```

## 7. Instalar dlib (recomendado: binario precompilado)

```powershell
pip install dlib-bin
```

## 8. Instalar face_recognition y modelos

```powershell
pip install face-recognition-models
pip install face_recognition --no-deps
```

## 9. Verificar instalacion

```powershell
python test.py
```

Debes ver versiones de OpenCV, Dlib y Numpy, con mensaje de exito.

## 10. Ejecutar el sistema

Registro de usuario:

```powershell
python registrar.py
```

Login biometrico:

```powershell
python login.py
```

---

## Ruta alternativa: compilar dlib desde fuente

Solo usa esta opcion si no puedes usar `dlib-bin`.

### A) Instalar Visual Studio Build Tools (C++)

1. Instala "Build Tools for Visual Studio".
2. Marca el workload: **Desktop development with C++**.
3. Reinicia PowerShell.

### B) Confirmar CMake

```powershell
cmake --version
```

### C) Instalar dlib y face_recognition

```powershell
pip install dlib
pip install face_recognition
```

---

## Solucion de problemas

### 1) `venv` creado en Linux/Raspberry y roto en Windows

Si aparece algo como rutas `/usr/bin`, recrea el entorno:

```powershell
Remove-Item -Recurse -Force .\venv
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2) Quiero repetir instalacion en otro equipo

Genera archivo de dependencias:

```powershell
pip freeze > requirements.txt
```

Instala dependencias desde archivo:

```powershell
pip install -r requirements.txt
```

### 3) Git muestra miles de archivos de `venv`

Asegura estas entradas en `.gitignore`:

```gitignore
venv/
.venv/
ENV/
env/
```

Si ya estaban rastreados, sacalos del indice (sin borrar archivos locales):

```powershell
git rm -r --cached --ignore-unmatch venv .venv ENV env
git add .gitignore
git commit -m "Stop tracking virtual environments"
```
