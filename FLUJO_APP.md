# Flujo de la App (Face Recognition)

Este diagrama resume el flujo principal de ejecucion y las decisiones clave del sistema.

```mermaid
flowchart TD
    A[Inicio] --> B[main.py]
    B --> C[StateManager / UI]
    C --> D{Menu principal}

    D -->|Login| E[login.py]
    D -->|Registro| F[registrar.py]

    %% LOGIN
    E --> E1[Cargar settings de reconocimiento]
    E1 --> E2[Cargar biometria de PERSONAL]
    E2 --> E3[Cargar biometria de ESTUDIANTE]
    E3 --> E4{Hay biometria?}
    E4 -->|No| E5[Mostrar mensaje y terminar]
    E4 -->|Si| E6[Abrir camara]
    E6 --> E7[Detectar rostro por frame]
    E7 --> E8{Match con PERSONAL?}
    E8 -->|Si| E9[Acceso personal concedido]
    E9 --> E10[Registrar log tipo PERSONAL]
    E8 -->|No| E11{Hay base de estudiantes?}
    E11 -->|No| E12[Acceso denegado]
    E11 -->|Si| E13[Validar contra ESTUDIANTE]
    E13 --> E14{Match estudiante?}
    E14 -->|Si| E15[Acceso estudiante concedido]
    E15 --> E16[Registrar log tipo ESTUDIANTE]
    E14 -->|No| E12
    E10 --> E17[Continuar hasta Q]
    E16 --> E17
    E12 --> E17

    %% REGISTRO
    F --> F1[Cargar settings de reconocimiento]
    F1 --> F2{Existe personal activo?}
    F2 -->|No| F3[Modo bootstrap]
    F3 --> F4[Permitir solo alta de primer SUPERADMIN]
    F4 --> F5[Capturar biometria de personal]
    F5 --> F6[Crear personal + guardar biometria]
    F6 --> F7[Fin registro]

    F2 -->|Si| F8[Autenticar personal por biometria]
    F8 --> F9{Autenticacion valida?}
    F9 -->|No| F10[Denegar registro y finalizar]
    F9 -->|Si| F11[Mostrar menu de tipo de registro]
    F11 --> F12{Tipo?}

    F12 -->|Estudiante| F13[Solicitar datos estudiante]
    F13 --> F14[Capturar biometria]
    F14 --> F15[Crear estudiante + guardar biometria]
    F15 --> F7

    F12 -->|Personal administrativo| F16{Rol permite alta de personal?}
    F16 -->|No| F17[Denegar por permisos]
    F17 --> F11
    F16 -->|Si| F18[Solicitar datos de personal]
    F18 --> F19[Capturar biometria]
    F19 --> F20[Crear personal + guardar biometria]
    F20 --> F7

    %% SCRIPT DE ARRANQUE INICIAL
    G[bootstrap_admin.py] --> G1{Existe personal activo?}
    G1 -->|Si| G2[Cancelar bootstrap]
    G1 -->|No| G3[Solicitar datos primer admin]
    G3 --> G4[Capturar biometria]
    G4 --> G5[Crear SUPERADMIN + guardar biometria]
```

## Notas rapidas

- En login, PERSONAL siempre se valida antes de ESTUDIANTE.
- En registro, primero se autentica personal administrativo.
- Si no existe personal activo, se habilita bootstrap para crear el primer SUPERADMIN.
- Los accesos se registran en `logs_acceso` con `tipo_usuario` correspondiente.
