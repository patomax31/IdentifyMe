# IdentifyMe Desktop Hybrid (Flask + PyWebview)

Aplicacion de escritorio hibrida con ventana nativa (sin navegador visible):

- Backend local Flask
- UI servida por templates Jinja2
- Contenedor de escritorio con PyWebview

## Estructura

- main.py: orquestador de app de escritorio
- flask_server.py: app Flask con rutas / y /status
- templates/index.html: vista principal
- static/: CSS y JS de interfaz

## Dependencias (Windows / Python 3.14)

`pywebview` declara `pythonnet` solo por la plataforma Windows; `pythonnet` suele **no tener wheel** en Python muy nuevo (p. ej. 3.14) y **falla al compilar**. Esta app arranca con **backend Qt** (`gui="qt"` en `main.py`) y **no usa** `pythonnet` en runtime.

Desde esta carpeta, con el venv del repo activado (o sin activar si existe `..\.venv`):

```powershell
.\install_deps.ps1
```

Equivalente manual:

```powershell
pip install -r requirements.txt
pip install --no-deps "pywebview>=5.0,<6.0"
```

## Ejecutar en desarrollo

### Windows (PowerShell), raiz del repo en `...\biometrico`

```powershell
cd desktop_hybrid
..\.venv\Scripts\Activate.ps1
python main.py
```

Si tu venv esta en la raiz del repo como `.venv`, puedes usar `..\.venv\Scripts\python.exe main.py` sin activar.

### Linux (ejemplo con venv en la raiz del proyecto)

```bash
cd desktop_hybrid
../.venv/bin/python -m pip install -r requirements.txt
../.venv/bin/python -m pip install --no-deps "pywebview>=5.0,<6.0"
../.venv/bin/python main.py
```

## Empaquetar a .exe con PyInstaller

Desde Windows, dentro de la carpeta desktop_hybrid:

```bash
pyinstaller --onefile --noconsole --name IdentifyMe --add-data "templates;templates" --add-data "static;static" main.py
```

Salida esperada:

- dist/IdentifyMe.exe

## Notas de produccion

- Flask corre en un hilo separado para no bloquear la UI.
- Se valida que el puerto 5000 este libre antes de iniciar.
- Debug de PyWebview se mantiene desactivado.
- Al cerrar la ventana, el servidor Flask se apaga correctamente.
