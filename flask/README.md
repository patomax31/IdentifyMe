# Flask UI moderna para Identifyme

Esta carpeta contiene una replica web (Flask) de las interfaces del sistema:

- Inicio
- Login facial
- Registro biometrico

La logica de negocio reutiliza los mismos casos de uso del proyecto:

- src/application/login_use_case.py
- src/application/registration_use_case.py

## Ejecutar

Desde la raiz face-recognition:

```bash
source ../.venv/bin/activate
pip install flask opencv-python numpy face-recognition
python flask/app.py
```

Luego abre:

- http://127.0.0.1:5000

## Flujo

- Login: toma frames de la webcam del navegador y consulta /api/login/verify.
- Registro: captura una imagen y consulta /api/registro con nombre, grado, letra y turno.

## Notas

- Debes dar permiso de camara al navegador.
- Si no hay usuarios registrados, el login devolvera error hasta que registres al menos uno.
