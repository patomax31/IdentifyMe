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

## Ejecutar en desarrollo

```bash
cd face-recognition/desktop_hybrid
/home/carlos/Documentos/UNI/Identifyme/.venv/bin/python -m pip install -r requirements.txt
/home/carlos/Documentos/UNI/Identifyme/.venv/bin/python main.py
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
