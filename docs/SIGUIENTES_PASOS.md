# Siguientes Pasos del Proyecto

Este documento define la siguiente fase para terminar la adopcion de arquitectura modular sin romper el comportamiento actual.

## 1. Extraer casos de uso (application)

Objetivo: mover reglas de flujo que aun viven en scripts de entrada.

1. Crear `src/application/login_use_case.py`.
2. Mover logica de autenticacion por frame:
- resolver match de rostro,
- decidir mensaje de salida,
- aplicar cooldown de bitacora.
3. Crear `src/application/registration_use_case.py`.
4. Mover logica de registro:
- validar resultado de deteccion,
- registrar estudiante,
- guardar biometria.

Criterio de aceptacion:
- `login.py` y `registrar.py` quedan como orquestadores ligeros (UI/IO + llamadas a casos de uso).

## 2. Desacoplar fallback PKL de login

Objetivo: encapsular compatibilidad legacy.

1. Crear adaptador `src/infrastructure/persistence/pkl_repository.py`.
2. Crear estrategia de carga en `application`:
- primero SQLite,
- luego PKL solo si SQLite no tiene biometria.
3. Evitar que `login.py` manipule archivos directamente.

Criterio de aceptacion:
- el fallback funciona igual que hoy, pero desde servicio/caso de uso.

## 3. Fortalecer pruebas unitarias de negocio

Objetivo: cubrir reglas funcionales clave sin dependencias de camara.

1. Agregar tests para `login_use_case`:
- acceso concedido,
- acceso denegado,
- cooldown evita logs duplicados.
2. Agregar tests para `registration_use_case`:
- rostro unico -> registro exitoso,
- cero o multiples rostros -> error controlado.
3. Mantener pruebas existentes de servicios e integracion SQLite.

Comando:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Criterio de aceptacion:
- suite completa en verde.

## 4. Estandarizar configuracion

Objetivo: unificar parametros operativos.

1. Consolidar parametros de tolerancia/cooldown/escala en `src/core/config.py`.
2. Evitar valores magicos en scripts y modulos.
3. Documentar variables de entorno nuevas en `README.md`.

Criterio de aceptacion:
- los umbrales operativos salen de configuracion central.

## 5. Cierre de migracion de arquitectura

Objetivo: dejar estructura final clara y mantenible.

1. Revisar imports para que `application` dependa solo de puertos (`src/domain/ports.py`).
2. Confirmar que infraestructura implemente esos puertos sin acoplar dominio.
3. Actualizar `README.md` con diagrama de capas (resumen textual).

Criterio de aceptacion:
- dependencias entre capas coherentes (dominio/application independientes de implementaciones concretas).

## 6. Checklist de verificacion final

1. Compilar proyecto:

```bash
python -m compileall src database tests login.py registrar.py
```

2. Ejecutar pruebas:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

3. Probar flujo manual:
- `python registrar.py`
- `python login.py`

Criterio de aceptacion:
- sin errores en compilacion,
- pruebas en verde,
- registro y login operativos.
