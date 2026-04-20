# Analisis de la base de datos (SQLite)

Fecha del analisis: 2026-04-19
Proyecto: face-recognition

## 1. Resumen ejecutivo

La capa de base de datos esta bien separada por responsabilidades y conectada a la arquitectura modular por puertos/adaptadores. Sin embargo, hay un problema critico en el esquema SQL (`database/script.sql`): el DDL esta duplicado en el mismo archivo y provoca fallo en la inicializacion de una BD nueva (`sqlite3.OperationalError: table grupos already exists`).

Esto impacta directamente el arranque en ambientes limpios, pruebas de integracion y despliegues nuevos.

## 2. Componentes y funcionamiento

### 2.1 Rutas y conexion

- `database/sqlite/paths.py`
  - Define:
    - `DB_PATH`: `database/face_recognition.db`
    - `SCHEMA_PATH`: `database/script.sql`
- `database/sqlite/connection.py`
  - Abre conexion SQLite y ejecuta `PRAGMA foreign_keys = ON` en cada conexion.

### 2.2 Inicializacion y migraciones

- `database/sqlite/migrations.py`
  - `initialize_database()`:
    - Crea directorio si no existe.
    - Si no existe tabla `grupos`, ejecuta todo `script.sql`.
    - Si ya existe, ejecuta `migrate_local_schema(conn)`.
  - `migrate_local_schema(conn)`:
    - Limpia tablas antiguas (`estudiante_tutor`, `tutores`, `dispositivos_raspberry`).
    - Migra estructura legacy de `estudiantes` (eliminando campos `matricula`, `nombre`, `apellidos` si existen).
    - Migra estructura legacy de `logs_acceso` (eliminando `id_dispositivo` si existe).
    - Garantiza indices `ux_datos_biometricos_usuario` e `ix_logs_acceso_usuario_fecha`.

### 2.3 Operaciones de dominio de datos

- `database/sqlite/students.py`
  - `create_student(grado, letra, turno)`:
    - Asegura grupo (`grupos`) y crea estudiante activo.
  - `save_student_biometric(id_estudiante, encoding)`:
    - Serializa embedding facial a JSON (`encoding_to_text`) y hace reemplazo (delete + insert) en `datos_biometricos` para evitar duplicados por estudiante.
  - `load_student_biometrics()`:
    - Hace join entre `datos_biometricos`, `estudiantes`, `grupos` y retorna encodings + etiquetas + ids activos.
  - `migrate_pickle_biometrics(...)`:
    - Migra archivos `.pkl` a SQLite, reutilizando IDs si el archivo es `est_<id>.pkl` y el estudiante existe.

- `database/sqlite/access.py`
  - `log_access(...)`:
    - Inserta en `logs_acceso`.
    - Valida `tipo_usuario` en `ESTUDIANTE` o `PERSONAL`.

- `database/sqlite_manager.py`
  - Fachada compatible hacia atras; reexporta funciones de `database/sqlite/*`.

### 2.4 Integracion con la arquitectura modular

- `src/infrastructure/persistence/sqlite_repository.py`
  - Adaptador hacia casos de uso (`AuthService`, `RegistrationService`).
- `login.py`
  - Carga biometria desde SQLite como fuente principal.
  - Si no hay datos en SQLite, `LoginUseCase` puede caer a `PklRepository` (compatibilidad).
  - Loguea acceso exitoso con cooldown.
- `registrar.py`
  - Registra estudiante en SQLite y guarda respaldo `.pkl`.

## 3. Modelo de datos actual

### 3.1 Tablas observadas en `database/face_recognition.db`

- `grupos`
- `estudiantes`
- `personal_administrativo`
- `datos_biometricos`
- `logs_acceso`
- `sqlite_sequence`

### 3.2 Relaciones e integridad

- FK activa:
  - `estudiantes.id_grupo -> grupos.id_grupo` (`ON DELETE RESTRICT`)
- Sin FK declarada:
  - `datos_biometricos(id_usuario_ref)` (polimorfica por `tipo_usuario`)
  - `logs_acceso(id_usuario_ref)` (polimorfica por `tipo_usuario`)

### 3.3 Indices

- `ux_datos_biometricos_usuario` (UNIQUE): `(tipo_usuario, id_usuario_ref)`
- `ix_logs_acceso_usuario_fecha`: `(tipo_usuario, id_usuario_ref, fecha_hora DESC)`
- Indices unicos auto de `personal_administrativo` por `num_empleado` y `correo`.

## 4. Hallazgos clave

## Hallazgo critico 1: DDL duplicado en `database/script.sql`

Se detectaron sentencias duplicadas de creacion de tablas/indices en el mismo archivo:

- `CREATE TABLE grupos` aparece dos veces.
- `CREATE TABLE estudiantes` aparece dos veces.
- `CREATE TABLE logs_acceso` aparece dos veces.
- `CREATE UNIQUE INDEX ux_datos_biometricos_usuario` aparece dos veces.

Impacto:

- La inicializacion de una BD nueva falla con:
  - `sqlite3.OperationalError: table grupos already exists`
- Falla el flujo de pruebas de integracion SQLite.

Evidencia ejecutada:

- Comando:
  - `python -m unittest tests.test_sqlite_students_integration tests.test_sqlite_access_integration -v`
- Resultado:
  - 3 pruebas en error por el mismo problema al ejecutar `conn.executescript(schema_file.read())`.

## Hallazgo alto 2: Inconsistencia de esquema en `estudiantes`

En el primer bloque de `script.sql`, `estudiantes` incluye columna `nombre`; en el segundo bloque no existe.

Impacto:

- Ambiguedad de contrato de datos.
- Riesgo de errores segun el bloque que se intente aplicar.

## Hallazgo medio 3: Modelo polimorfico sin FK en biometria y logs

`datos_biometricos` y `logs_acceso` no tienen FK sobre entidad concreta (por diseno polimorfico).

Impacto:

- Se pueden generar referencias huerfanas si no hay validaciones de aplicacion.
- Es un trade-off valido, pero requiere controles estrictos a nivel de servicios.

## 5. Fortalezas detectadas

- Separacion clara de responsabilidades (`connection`, `migrations`, `students`, `access`, `encoding`).
- Migraciones locales defensivas para limpiar legado y estandarizar indices.
- Integracion correcta con puertos y adaptadores de la capa application/domain.
- Estrategia de compatibilidad con `.pkl` para continuidad operativa.
- Indices adecuados para consultas frecuentes de autenticacion y auditoria.

## 6. Recomendaciones

1. Corregir `database/script.sql` de inmediato:
   - Eliminar bloque duplicado.
   - Dejar un unico DDL canonico.
2. Definir contrato final de `estudiantes`:
   - Confirmar si la columna `nombre` debe existir o no.
   - Alinear `script.sql`, migraciones y codigo de negocio.
3. Endurecer inicializacion:
   - Opcionalmente envolver `executescript` con manejo de error y rollback + log explicito para diagnostico rapido.
4. Reforzar pruebas:
   - Mantener tests de integracion SQLite en CI para detectar regresiones de esquema.
5. Para modelo polimorfico:
   - Documentar regla de integridad aplicativa para `datos_biometricos` y `logs_acceso`.
   - Evaluar triggers de validacion si se desea mayor consistencia dentro de SQLite.

## 7. Conclusion

El diseno de la capa de persistencia es bueno y extensible, pero el estado actual del archivo de esquema bloquea la creacion limpia de base de datos. La prioridad tecnica inmediata es normalizar `database/script.sql`; despues de eso, la arquitectura actual puede operar de forma estable para registro, login y bitacora de accesos.
