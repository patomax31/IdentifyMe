# Diagrama Relacional de la Base de Datos

Este diagrama representa el esquema definido en `database/script.sql`.

```mermaid
erDiagram
    GRADOS {
        INTEGER id_grado PK
        TEXT clave UK
        TEXT nombre UK
    }

    GRUPOS {
        INTEGER id_grupo PK
        TEXT clave UK
    }

    TURNOS {
        INTEGER id_turno PK
        TEXT clave UK
        TEXT nombre UK
    }

    ESTUDIANTES {
        INTEGER id_estudiante PK
        TEXT nombre
        INTEGER id_grado FK
        INTEGER id_grupo FK
        INTEGER id_turno FK
        INTEGER estado_activo
    }

    PERSONAL_ADMINISTRATIVO {
        INTEGER id_personal PK
        TEXT num_empleado UK
        TEXT nombre_completo
        TEXT rol
        TEXT correo UK
        TEXT password_hash
        INTEGER estado_activo
    }

    DATOS_BIOMETRICOS {
        INTEGER id_biometria PK
        TEXT tipo_usuario
        INTEGER id_usuario_ref
        TEXT vector_facial
        DATETIME fecha_registro
    }

    LOGS_ACCESO {
        INTEGER id_log PK
        TEXT tipo_usuario
        INTEGER id_usuario_ref
        DATETIME fecha_hora
        TEXT tipo_evento
        INTEGER acceso_concedido
    }

    ESTUDIANTES }o--|| GRADOS : "id_grado"
    ESTUDIANTES }o--|| GRUPOS : "id_grupo"
    ESTUDIANTES }o--|| TURNOS : "id_turno"

    %% Relaciones polimorficas (logicas, no FK fisica en SQLite)
    DATOS_BIOMETRICOS }o..o| ESTUDIANTES : "tipo_usuario=ESTUDIANTE, id_usuario_ref"
    DATOS_BIOMETRICOS }o..o| PERSONAL_ADMINISTRATIVO : "tipo_usuario=PERSONAL, id_usuario_ref"

    LOGS_ACCESO }o..o| ESTUDIANTES : "tipo_usuario=ESTUDIANTE, id_usuario_ref"
    LOGS_ACCESO }o..o| PERSONAL_ADMINISTRATIVO : "tipo_usuario=PERSONAL, id_usuario_ref"
```

## Notas

- Relaciones fuertes (con `FOREIGN KEY`): `estudiantes` con `grados`, `grupos` y `turnos`.
- Relaciones de `datos_biometricos` y `logs_acceso` son polimorficas por diseno (`tipo_usuario` + `id_usuario_ref`), sin FK declarada en SQLite.
- Vistas de apoyo (no incluidas como entidades): `vw_estudiantes`, `vw_logs_acceso`, `vw_intentos_fallidos`.
