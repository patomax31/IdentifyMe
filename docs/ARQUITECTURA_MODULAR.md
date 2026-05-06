# Arquitectura Modular del Sistema

Este documento describe el funcionamiento de cada modulo y como se conectan entre si dentro del proyecto.

## 1. Vision general por capas

El sistema sigue una arquitectura en capas con principio de inversion de dependencias:

- `domain`: define contratos (puertos), no implementaciones.
- `application`: contiene casos de uso y servicios de negocio.
- `infrastructure`: implementa integraciones concretas (SQLite, PKL, camara, reconocimiento facial).
- `entrypoints`: scripts de ejecucion (`login.py`, `registrar.py`) que coordinan UI/IO.
- `database`: detalles tecnicos de acceso a SQLite.

## 2. Modulos y responsabilidad

### 2.1 Entrypoints

- `login.py`
  - Abre camara.
  - Captura frames y renderiza interfaz OpenCV.
  - Delega decisiones de autenticacion al caso de uso `LoginUseCase`.

- `registrar.py`
  - Solicita datos del grupo (grado, letra, turno).
  - Abre camara y captura frame al presionar `S`.
  - Delega validacion y registro al caso de uso `RegistrationUseCase`.

### 2.2 Capa application

- `src/application/auth_service.py`
  - Servicio delgado que delega en puerto de autenticacion.
  - Expone inicializacion, carga de estudiantes y log de accesos.

- `src/application/registration_service.py`
  - Servicio delgado para crear estudiante y guardar biometria.

- `src/application/login_use_case.py`
  - Orquesta autenticacion por frame.
  - Evalua coincidencias faciales usando `FaceMatcherPort`.
  - Construye resultado de UI (mensaje + color).
  - Aplica cooldown para evitar logs duplicados de acceso.
  - Implementa estrategia de carga: primero SQLite, luego PKL como fallback.

- `src/application/registration_use_case.py`
  - Valida resultado de deteccion facial:
    - 0 rostros -> error controlado.
    - >1 rostro -> error controlado.
    - 1 rostro -> registro exitoso.
  - Registra estudiante en SQLite via servicio.
  - Guarda respaldo PKL via puerto.

### 2.3 Capa domain

- `src/domain/ports.py`
  - Define contratos para repositorios y adaptadores:
    - `AuthRepositoryPort`
    - `RegistrationRepositoryPort`
    - `PklBiometricRepositoryPort`
    - `FaceMatcherPort`
  - Estos puertos permiten que `application` dependa de abstracciones, no de implementaciones concretas.

### 2.4 Capa infrastructure

- `src/infrastructure/camera/opencv_camera.py`
  - Inicializa camara con perfiles (`AUTO`, `WINDOWS_STABLE`, `RASPBERRY_PI`).

- `src/infrastructure/recognition/face_engine.py`
  - Deteccion y encoding facial.
  - Comparacion de encodings (`find_first_match`).

- `src/infrastructure/recognition/matcher_adapter.py`
  - Adaptador que implementa `FaceMatcherPort` usando `face_engine`.

- `src/infrastructure/persistence/sqlite_repository.py`
  - Adaptador SQLite que implementa puertos de `domain`.
  - Delega operaciones reales a `database/sqlite_manager.py`.

- `src/infrastructure/persistence/pkl_repository.py`
  - Adaptador para cargar y guardar biometria en `data/*.pkl`.
  - Se usa como compatibilidad legacy y respaldo.

### 2.5 Capa database

- `database/sqlite_manager.py`
  - Fachada de compatibilidad para operaciones SQLite.

- `database/sqlite/connection.py`
  - Conexion a base de datos.

- `database/sqlite/migrations.py`
  - Inicializacion y migraciones.

- `database/sqlite/students.py`
  - Operaciones de estudiantes y biometria.

- `database/sqlite/access.py`
  - Bitacora de accesos.

- `database/sqlite/encoding.py`
  - Serializacion/deserializacion de vectores faciales.

- `database/sqlite/paths.py`
  - Rutas de base de datos y esquema.

### 2.6 Capa core

- `src/core/config.py`
  - Configuracion centralizada por variables de entorno:
    - Camara: `CAMERA_INDEX`, `CAMERA_PROFILE`, `CAMERA_WIDTH`, `CAMERA_HEIGHT`, `CAMERA_FPS`
    - Reconocimiento: `RECOGNITION_SCALE`, `RECOGNITION_TOLERANCE`, `ACCESS_COOLDOWN_SECONDS`

## 3. Flujo de interconexion

## 3.1 Flujo de registro

1. `registrar.py` solicita datos de grupo y abre camara.
2. Obtiene encodings del frame actual con `face_engine.detect_face_encodings_from_frame`.
3. Llama `RegistrationUseCase.register_from_detected_faces(...)`.
4. El caso de uso valida cantidad de rostros.
5. Si hay un solo rostro:
   - usa `RegistrationService` para crear estudiante y guardar biometria en SQLite.
   - usa `PklRepository` para guardar respaldo PKL.
6. Retorna resultado (`success`, `message`, `student_id`) y el script lo muestra en pantalla/consola.

## 3.2 Flujo de login

1. `login.py` abre camara y carga estudiantes conocidos via `LoginUseCase.load_known_students()`.
2. `LoginUseCase` intenta primero SQLite (via `AuthService` + `SQLiteRepository`).
3. Si SQLite no tiene biometria, usa fallback PKL (`PklRepository`).
4. Por cada frame, `login.py` extrae encodings y llama `LoginUseCase.process_frame(...)`.
5. `LoginUseCase` busca match con `FaceMatcherAdapter`.
6. Si hay match:
   - retorna mensaje de acceso concedido.
   - registra bitacora con cooldown para evitar duplicados.
7. Si no hay match, retorna acceso denegado.
8. `login.py` solo renderiza UI (ovalo, texto, color) y controla cierre por tecla `q`.

## 4. Reglas de dependencia

Regla principal:

- `domain` no depende de nadie.
- `application` depende de `domain`.
- `infrastructure` depende de `domain` para implementar puertos.
- `entrypoints` componen dependencias concretas y llaman a `application`.

Esto facilita:

- pruebas unitarias con dobles/fakes,
- cambios de infraestructura sin romper negocio,
- mantenibilidad y evolucion progresiva.

## 5. Pruebas y validacion

- Pruebas de servicios:
  - `tests/test_auth_service.py`
  - `tests/test_registration_service.py`

- Pruebas de casos de uso:
  - `tests/test_login_use_case.py`
  - `tests/test_registration_use_case.py`

- Integracion SQLite:
  - `tests/test_sqlite_students_integration.py`
  - `tests/test_sqlite_access_integration.py`

Con esto, la arquitectura modular queda documentada a nivel de responsabilidad y colaboracion entre modulos.
