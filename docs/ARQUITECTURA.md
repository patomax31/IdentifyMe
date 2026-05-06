<<<<<<< HEAD
# Arquitectura de Software - Sistema de Reconocimiento Facial

## 📋 Índice
1. [Descripción General](#descripción-general)
2. [Estructura de Módulos](#estructura-de-módulos)
3. [Flujo de Procesos](#flujo-de-procesos)
4. [Componentes Clave](#componentes-clave)
5. [Análisis Técnico Profundo](#análisis-técnico-profundo)
6. [Stack Tecnológico](#stack-tecnológico)
7. [Persistencia de Datos](#persistencia-de-datos)

--- 

## 🎯 Descripción General

El sistema es una **solución biométrica embebida** diseñada para:
- **Registro de rostros**: Capturar y almacenar encodings faciales de estudiantes
- **Autenticación**: Verificar identidad mediante reconocimiento facial
- **Control de acceso**: Permitir o denegar entrada basado en identificación facial
- **Auditoría**: Mantener registro de accesos (entrada/salida) con timestamps

**Objetivo**: Implementar un sistema de control de asistencia y acceso para instituciones educativas usando **visión computacional** sin necesidad de conexión a internet.

---

## 🏗️ Estructura de Módulos

```
face-recognition/
├── login.py                          # Script principal de autenticación
├── registrar.py                      # Script de registro de nuevos usuarios
├── test.py                           # Validación de dependencias
├── data/                             # Cache local de encodings (formato .pkl)
│   ├── dominic.pkl
│   ├── kevin0.pkl
│   └── ... (respaldos de vectores faciales)
├── database/
│   ├── script.sql                    # Esquema SQLite (definición de tablas)
│   ├── sqlite_manager.py             # Capa de abstracción de BD
│   └── face_recognition.db           # Base de datos SQLite (generada)
├── README.md                         # Documentación de uso
├── SETUP_RASPBERRY.md                # Guía de instalación en RPi
└── GUIA_INSTALACION_WINDOWS.md       # Guía de instalación en Windows
=======
# 🏗️ ARQUITECTURA - Sistema de Verificación de Dependencias

## Diagrama General de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                     APLICACIÓN USUARIO                          │
│                                                                  │
│              python test_setup.py                              │
│                       ↓                                         │
│              ┌─────────────────────┐                            │
│              │  SystemCheckUI      │ (tk.Tk)                  │
│              │  (Interfaz Gráfica) │                            │
│              └──────────┬──────────┘                            │
│                        ↓                                         │
│          ┌──────────────────────────────┐                       │
│          │    Thread de Validaciones    │                       │
│          └───────────┬──────────────────┘                       │
│                      ↓                                           │
│          ┌──────────────────────────────┐                       │
│          │   SystemValidator            │                       │
│          │   - Dependencias             │                       │
│          │   - Hardware                 │                       │
│          │   - Base de Datos            │                       │
│          └───────────┬──────────────────┘                       │
│                      ↓                                           │
│     ┌────────────────┴──────────────────┬────────────────┐     │
│     ↓                                    ↓                ↓     │
│  Validar              Validar             Validar              │
│  Dependencias         Hardware            BD                   │
│  (6 módulos)          (3 componentes)   (SQLite)              │
│                                                                 │
│         Resultados → UI Update → Mostrar Estado               │
│                                                                 │
│     ¿TODO OK?                                                  │
│     ├─→ SÍ → Habilitar "Continuar"                            │
│     └─→ NO → Habilitar "Reintentar"                           │
│                                                                 │
│              ↓                          ↓                       │
│    [Continuar]                  [Reintentar]                   │
│         ↓                             ↓                         │
│      Abrir              Reiniciar ValidacionesThread          │
│      FaceLoginUI                                               │
└─────────────────────────────────────────────────────────────────┘
>>>>>>> 2e2d95e (UI de la cargainicial de dependencias test_setup.py)
```

---

<<<<<<< HEAD
## 🔄 Flujo de Procesos

### 1️⃣ **Proceso de Registro (`registrar.py`)**

```
┌─────────────────┐
│  Inicia Script  │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│ Inicializa Base de Datos     │
│ - Conecta a SQLite           │
│ - Crea tablas si no existen  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Solicita Datos Educativos    │
│ - Grado (1, 2, 3)            │
│ - Letra del Grupo (A-Z)      │
│ - Turno (MATUTINO/VESPERTINO)│
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ Abre Cámara                      │
│ - Configura resolución (640x480) │
│ - Ajusta FPS (20 fps)            │
│ - Activa captura de video        │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│ Loop de Captura                              │
│ - Muestra óvalo guía en pantalla             │
│ - Presionar 'S' = Capturar y procesar rostro │
│ - Presionar 'Q' = Salir                      │
└────────┬─────────────────────────────────────┘
         │
         ▼ (Usuario presiona 'S')
┌──────────────────────────────────────┐
│ Detecta y Encoda Rostro              │
│ - Busca faces en frame (dlib)        │
│ - Genera vector de 128 dimensiones   │
│ - Valida que hay exactamente 1 cara  │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│ Almacena Encoding en Dos Ubicaciones    │
│ 1. SQLite: tabla datos_biometricos       │
│ 2. Fallback: archivo PKL en data/        │
│    (Formato: est_<id>.pkl)               │
└────────┬─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Crea Registro de Estudiante │
│ - Inserta en tabla grupos   │
│ - Inserta en tabla estudiantes
└─────────────────────────────┘
```

### 2️⃣ **Proceso de Login (`login.py`)**

```
┌─────────────────┐
│  Inicia Script  │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│ Carga Biometría Registrada   │
│ - Lee de SQLite DB           │
│ - Fallback a PKL si necesario │
│ - Carga lista de encodings   │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│ Abre Cámara                  │
│ (misma configuración que     │
│  registro)                   │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Loop Continuo de Reconocimiento      │
│ - Captura frame de cámara            │
│ - Escala a 1/4 para optimizar        │
│ - Detecta rostros presentes en frame │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│ Comparación de Encodings                │
│ - Para cada rostro detectado:           │
│   • Calcula distancia euclidiana        │
│   • Compara contra todos los registrados│
│   • Usa threshold de tolerancia (0.6)   │
└────────┬─────────────────────────────────┘
         │
         ▼ (Coincidencia encontrada)
┌────────────────────────────────────────────────┐
│ Determina Identidad del Usuario               │
│ - Obtiene ID del estudiante matched           │
│ - Recupera grupo: grado, letra, turno         │
│ - Marca color oval en VERDE                   │
│ - Muestra: "ACCESO CONCEDIDO - [DATOS]"       │
└────────┬───────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Implementa Cooldown                  │
│ - Evita múltiples registros          │
│ - Espera 8 segundos sin redetectar   │
│ (Previene logs duplicados)           │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Registra en Log de Acceso            │
│ - Tipo: ENTRADA                      │
│ - ID Usuario: id_estudiante          │
│ - Acceso Concedido: 1 (verdadero)    │
│ - Timestamp: CURRENT_TIMESTAMP       │
=======
## Estructura de Clases

```
┌──────────────────────────────────────┐
│         Enumeraciones                │
├──────────────────────────────────────┤
│ • CheckStatus                        │
│   - PENDING                          │
│   - CHECKING                         │
│   - SUCCESS                          │
│   - ERROR                            │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│       Dataclasses                    │
├──────────────────────────────────────┤
│ • CheckResult                        │
│   - name: str                        │
│   - category: str                    │
│   - status: CheckStatus              │
│   - message: str                     │
│   - error_details: str               │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│      SystemValidator                │
├──────────────────────────────────────┤
│ __init__(callback)                   │
│ validate_dependencies()              │
│ validate_camera()                    │
│ validate_display()                   │
│ validate_servo()                     │
│ validate_database()                  │
│ run_all_checks()                     │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│      LoadingCircle(tk.Canvas)        │
├──────────────────────────────────────┤
│ __init__(parent, size, color)        │
│ start()                              │
│ stop()                               │
│ _animate()                           │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│    CheckItemWidget(tk.Frame)         │
├──────────────────────────────────────┤
│ __init__(parent, result)             │
│ update_status(result)                │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│     SystemCheckUI(tk.Tk)             │
├──────────────────────────────────────┤
│ __init__()                           │
│ _configure_styles()                  │
│ _create_widgets()                    │
│ _start_validation()                  │
│ _on_check_result(result)             │
│ _update_check_result(result)         │
│ _on_validation_complete()            │
│ _on_continue()                       │
>>>>>>> 2e2d95e (UI de la cargainicial de dependencias test_setup.py)
└──────────────────────────────────────┘
```

---

<<<<<<< HEAD
## 🔧 Componentes Clave

### 1. **Módulo de Captura de Video (`abrir_camara()`)**

**Ubicación**: `login.py`, `registrar.py`

**Funcionalidad**:
- Detección automática de SO (Windows/Linux)
- Selección de backend de captura:
  - **Windows**: DirectShow (CAP_DSHOW)
  - **Raspberry Pi**: Video4Linux2 (CAP_V4L2)
- Configuración de parámetros vía variables de entorno:
  ```
  CAMERA_INDEX=0          # Índice de cámara (0 o 1)
  CAMERA_PROFILE=AUTO     # Perfil de captura
  CAMERA_WIDTH=640        # Resolución ancho
  CAMERA_HEIGHT=480       # Resolución alto
  CAMERA_FPS=20           # Fotogramas por segundo
  ```

**Razón de optimización**: Raspberry Pi tiene recursos limitados; reducir resolución y FPS mejora rendimiento sin comprometer precisión.

---

### 2. **Módulo de Reconocimiento Facial**

**Librerías usadas**:
- **`face_recognition`**: Abstracción de dlib, calcula encodings de 128 dimensiones
- **`dlib`**: Motor de red neuronal preentrenada (modelo CNN)
- **`cv2` (OpenCV)**: Procesamiento de imagen y captura de video

**Algoritmo de detección**:
```python
small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)  # Escala 1/4
rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)   # BGR → RGB
boxes = face_recognition.face_locations(rgb_small)         # Bounding boxes
encodings = face_recognition.face_encodings(rgb_small, boxes)  # Vectores
```

**Matching**:
```python
distance = face_recognition.face_distance(rostros_registrados, encoding_capturado)
if distance < THRESHOLD (0.6):
    ACCESO_CONCEDIDO
else:
    ACCESO_DENEGADO
```

---

### 3. **Capa de Persistencia (`database/sqlite_manager.py`)**

**Responsabilidades**:
- **Inicialización**: Crear BD y tablas en primer uso
- **Migración**: Actualizar esquema sin perder datos
- **CRUD de usuarios**: Crear estudiantes y personal
- **CRUD de biometría**: Almacenar/recuperar encodings faciales
- **Auditoría**: Registrar accesos en log

**Funciones principales**:

| Función | Propósito |
|---------|-----------|
| `initialize_database()` | Crea BD y ejecuta migraciones |
| `create_student()` | Inserta nuevo estudiante en tabla |
| `save_student_biometric()` | Guarda encoding facial en BD |
| `load_student_biometrics()` | Carga todos los encodings registrados |
| `log_access()` | Registra entrada/salida en log |
| `_encoding_to_text()` | Convierte array numpy → JSON |
| `_text_to_encoding()` | Convierte JSON → array numpy |

---

### 4. **Base de Datos SQLite (`database/script.sql`)**

**Tablas principales**:

#### `grupos`
```sql
CREATE TABLE grupos (
    id_grupo INTEGER PRIMARY KEY,
    grado INTEGER (1, 2, 3),
    letra TEXT,
    turno TEXT (MATUTINO, VESPERTINO)
);
```
**Uso**: Clasificación educativa de estudiantes (Ej: Grado 2, letra A, turno matutino)

#### `estudiantes`
```sql
CREATE TABLE estudiantes (
    id_estudiante INTEGER PRIMARY KEY,
    id_grupo INTEGER NOT NULL,
    estado_activo INTEGER (0 o 1),
    FOREIGN KEY (id_grupo) REFERENCES grupos
);
```
**Uso**: Registro de cada estudiante, vinculado a su grupo

#### `datos_biometricos`
```sql
CREATE TABLE datos_biometricos (
    id_biometria INTEGER PRIMARY KEY,
    tipo_usuario TEXT ('ESTUDIANTE', 'PERSONAL'),
    id_usuario_ref INTEGER,
    vector_facial TEXT (JSON de 128 floats),
    fecha_registro DATETIME
);
```
**Uso**: Almacena encodings de rostro como vectores de 128 dimensiones

#### `logs_acceso`
```sql
CREATE TABLE logs_acceso (
    id_log INTEGER PRIMARY KEY,
    tipo_usuario TEXT ('ESTUDIANTE', 'PERSONAL'),
    id_usuario_ref INTEGER,
    fecha_hora DATETIME,
    tipo_evento TEXT ('Entrada', 'Salida'),
    acceso_concedido INTEGER (0 o 1)
);
```
**Uso**: Auditoría completa de accesos con timestamp

#### `personal_administrativo`
```sql
CREATE TABLE personal_administrativo (
    id_personal INTEGER PRIMARY KEY,
    num_empleado TEXT UNIQUE,
    nombre_completo TEXT,
    rol TEXT,
    correo TEXT UNIQUE,
    password_hash TEXT,
    estado_activo INTEGER
);
```
**Uso**: Registro de personal (futuro para autenticación adicional)

---

## 2.5 Análisis Técnico Profundo

Esta sección profundiza en las decisiones arquitectónicas y la integración de subsistemas a nivel técnico.

### 2.4.1 Arquitectura de Capas

El sistema utiliza una **arquitectura de capas** donde Python actúa como orquestador central integrado con subsistemas compilados:

```
CAPA DE PRESENTACIÓN
─────────────────────────────
    (OpenCV GUI)
          │
CAPA DE ORQUESTACIÓN
─────────────────────────────
    Python (Control, decisiones)
    │  │  │  │
    ├──┼──┼──┴─ Subsistemas
    │  │  │
CAPA DE LIBRERÍAS NATIVAS
─────────────────────────────
OpenCV  face_recog  RPi.GPIO  SQLite
 (C++)    (dlib)    (kernel)   (C)
```

### 2.4.2 Python como Lenguaje Orquestador

La adopción de Python como lenguaje orquestador se fundamenta en su naturaleza interpretada, su alto nivel de abstracción y su capacidad para integrar múltiples subsistemas heterogéneos dentro de una misma aplicación.

A diferencia de lenguajes compilados, Python opera mediante un intérprete que permite ejecutar instrucciones de forma directa sin necesidad de compilación previa. Esta característica facilita el **desarrollo iterativo**, la **depuración** y la **rápida integración de módulos** – aspectos clave en sistemas embebidos.

#### Dualidad de Roles

Python desempeña dos papeles simultáneamente:

**1. Intérprete de Lógica de Control**: Ejecuta el flujo de condicionales, loops e integración:
```python
while True:  # ← Controlado por Python (interpretado)
    ret, frame = cap.read()
    if faces_detected:
        send_to_recognition()
    update_hardware()
    log_to_db()
```

**2. Orquestador de Subsistemas**: Coordina OpenCV, dlib, GPIO, SQLite delegando operaciones intensivas:
```
Python maneja:           Las librerías nativas manejan:
├─ Flujo de control     ├─ Algoritmos intensivos (50-150ms)
├─ Decisiones lógicas   ├─ Están compiladas en C/C++
└─ ~ 5ms (1%)          └─ ~ 300ms (98%)
```

#### Overhead de Interpretación

Aunque Python es interpretado, su overhead es negligible optimizándolo con delegación:

```
Ciclo típico de reconocimiento facial:

Operación                          Tiempo      Ejecutor    %
──────────────────────────────────────────────────────────
Python (control + decisiones)      5 ms        Intérprete  1.6%
cap.read() (captura)               30-50 ms    OpenCV C++  15%
detectMultiScale() (Haar)          50-100 ms   OpenCV C++  32%
face_encodings() (CNN dlib)        100-150 ms  dlib C++    50%
Comparación numpy                  5-10 ms     NumPy C     2%
GPIO/SQLite                        5-10 ms     Nativas     2%
──────────────────────────────────────────────────────────
TOTAL CICLO: 190-320 ms → 3-5 FPS
PYTHON OVERHEAD: < 5% ✓
```

**Conclusión**: Un aspecto crítico es que Python **no ejecuta directamente** los algoritmos más costosos (visión, IA), sino que actúa como **wrapper sobre librerías en C/C++**. Esto permite lograr un **equilibrio entre productividad de desarrollo y rendimiento cercano a C++**.

De esta manera, **Python maneja el flujo de control, decisiones lógicas y orquestación**, mientras que **OpenCV maneja los algoritmos intensivos compilados en C++**.

### 2.4.3 OpenCV y la Elección del Enfoque Clásico

Si bien el estado del arte en reconocimiento facial utiliza Redes Neuronales Convolucionales (CNN) profundas (como ResNet), la implementación de estas arquitecturas en una Raspberry Pi sin GPU discreta genera latencias inasumibles y sobrecalentamiento rápido.

Por ello, se seleccionó OpenCV focalizado en sus **algoritmos clásicos de visión computacional**, que son altamente eficientes. 

#### Comparativa de Enfoques

| Método | Latencia | Precisión | RPi 5 FPS | Nota |
|--------|----------|-----------|-----------|------|
| **Haar Cascades** | 50-100 ms | 85-90% | 10-15 | ✓ Actual (detección) |
| **LBPH** | 10-20 ms | 80-85% | 20-30 | ✓ Propuesto (mejora) |
| **dlib CNN** | 100-150 ms | 92-95% | 3-5 | ✓ Actual (encoding) |
| **YuNet ONNX** | 50-80 ms | 88-92% | 8-12 | 🔄 2.5x más rápido |
| **CNN Profunda** | 500ms-2s | 96-98% | <0.5 | ✗ Imposible en RPi |

#### Por Qué LBPH es Excelente para Futuro

En lugar de generar embeddings mediante redes neuronales complejas, **una mejora futura propone usar Local Binary Patterns Histograms (LBPH)**, que ofrece un equilibrio robusto:

```
¿Cómo funciona LBPH?

1. Local Binary Patterns (LBP):
   └─ Compara cada píxel con sus 8 vecinos → patrón binario
   └─ Sin redes neuronales, solo comparaciones lógicas
   └─ Extremadamente rápido

2. Histogramas:
   └─ Divide imagen en regiones (4x4 o 8x8)
   └─ Calcula histograma LBP de cada región
   └─ Concatena histogramas → descriptor compacto

Ventajas LBPH:
✓ Extremadamente rápido (10-20 ms)
✓ CPU-only, sin GPU
✓ Robusto a variaciones de iluminación
✓ Bajo consumo de memoria
✓ Ideal para Raspberry Pi
```

**LBPH ofrece un equilibrio robusto entre precisión y consumo de recursos, siendo capaz de operar en tiempo real (>15 FPS) de manera fluida utilizando únicamente la CPU ARM de la placa.**

### 2.4.4 Face Recognition

`face_recognition` es una librería Python que simplifica el reconocimiento facial mediante un wrapper sobre **dlib** (compilado en C++):

```python
import face_recognition

# API simple en Python
image = face_recognition.load_image_file("foto.jpg")
face_encoding = face_recognition.face_encodings(image)[0]
# Retorna vector de 128 dimensiones

# Comparación
matches = face_recognition.compare_faces(
    known_encodings,  # Lista de BD
    face_encoding,    # Usuario actual
    tolerance=0.5     # Threshold
)
```

#### Flujo Interno: Tres Pasos

**1. Detección de Puntos Clave (HOG)**
- Busca 68 puntos de referencia en el rostro (ojos, nariz, boca)
- Tiempo: 50-100 ms

**2. Generación de Encodings (CNN dlib)**
- Genera vector de 128 dimensiones único para cada rostro
- Basado en arquitectura CNN profunda
- Tiempo: 100-150 ms (paso más costoso)

**3. Comparación (Distancia Euclidiana)**
- Calcula distancia entre embeddings
- Si distancia < `tolerance=0.5`: MATCH
- Tiempo: 5-10 ms

#### El Parámetro tolerance=0.5

```
tolerance = 0.3    MUY ESTRICTO
               → Rechaza usuarios legítimos con ángulos diferentes

tolerance = 0.5    EQUILIBRADO ← RECOMENDADO
               → Balance seguridad/usabilidad

tolerance = 0.8    MUY PERMISIVO
               → Acepta usuarios falsificados
```

**Distribución de distancias típicas**:
- Mismo usuario: 0.2 - 0.4 (media: 0.3)
- Usuario diferente: 0.5 - 1.0 (media: 0.7)
- Zona crítica [0.45-0.55]: Requiere validación

---

## 📦 Stack Tecnológico

| Componente | Librería/Versión | Propósito |
|-----------|------------------|----------|
| **Captura de Video** | OpenCV (cv2) | Acceso a cámara, procesamiento de frames |
| **IA/ML** | face_recognition 1.3.0+ | Detección y encoding de rostros |
| **Backend ML** | dlib 19.20+ | Red neuronal CNN preentrenada |
| **Computación** | NumPy | Operaciones matriciales, distancias |
| **Database** | SQLite 3 | Almacenamiento local sin servidor |
| **Lenguaje** | Python 3.7+ | Desarrollo cross-platform |
| **Serialización** | pickle + JSON | Respaldo de encodings |

---

## 💾 Persistencia de Datos

### Modelo Dual de Almacenamiento

```
┌──────────────────────────────────────────────────┐
│         ENCODINGS FACIALES (VECTORES)            │
├──────────────────────────────────────────────────┤
│  Ubicación 1: SQLite (Primaria)                  │
│  ├─ Tabla: datos_biometricos                     │
│  ├─ Formato: JSON (texto)                        │
│  ├─ Ventaja: Consultas SQL, no requiere serialización
│  └─ Velocidad: Más rápido en Raspberry Pi        │
│                                                  │
│  Ubicación 2: Archivos PKL (Fallback)            │
│  ├─ Ubicación: data/est_<id>.pkl                 │
│  ├─ Formato: Serialización pickle                │
│  ├─ Ventaja: Compatibilidad retroactiva          │
│  └─ Nota: Usado solo si BD está vacía            │
└──────────────────────────────────────────────────┘
```

### Conversión de Datos

```python
# Guardar en BD
vector_numpy = face_recognition.face_encodings(...)[0]
vector_json = json.dumps(vector_numpy.tolist())
# INSERT INTO datos_biometricos (vector_facial) VALUES (vector_json)

# Cargar desde BD
vector_json = row[0]  # SELECT vector_facial FROM ...
vector_numpy = np.array(json.loads(vector_json))
```

---

## 🔐 Seguridad Actual

**Medidas implementadas**:
- ✅ Índices UNIQUE en datos biométricos (evita duplicados)
- ✅ Foreign keys habilitadas en SQLite
- ✅ Validación de entrada (grado 1-3, turno válido)
- ✅ Check constraints en tablas
- ⚠️ **Sin encriptación de vectores** (Mejora necesaria)
- ⚠️ **Sin autenticación de admin** (Mejora necesaria)

---

## 📊 Diagrama de Entidades (ER)

```
┌──────────────┐
│   grupos     │
├──────────────┤
│ id_grupo ◄───────┐
│ grado           │
│ letra           │
│ turno           │ 1:N
└──────────────┘  │
                  │
┌──────────────┐  │
│ estudiantes  │  │
├──────────────┤  │
│ id_estudiante├──┘
│ id_grupo ────┘
│ estado_activo
└──────────────┘
        │
        │ 1:1
        ▼
┌──────────────────┐
│datos_biometricos │
├──────────────────┤
│id_biometria      │
│tipo_usuario='EST'
│id_usuario_ref───┼──→ id_estudiante
│vector_facial    │
│fecha_registro   │
└──────────────────┘
        │
        │ 1:N
        ▼
┌──────────────────┐
│  logs_acceso     │
├──────────────────┤
│id_log            │
│tipo_usuario      │
│id_usuario_ref    │
│fecha_hora        │
│tipo_evento       │
│acceso_concedido  │
└──────────────────┘
=======
## Flujo de Datos

### 1. Inicialización
```
SystemCheckUI.__init__()
    ↓
_configure_styles()  (Cargar colores)
    ↓
_create_widgets()    (Construir UI)
    ├─ Título
    ├─ LoadingCircle
    ├─ Barra de Progreso
    ├─ Container de verificaciones
    └─ Botones
    ↓
after(500ms) → _start_validation()
```

### 2. Validaciones
```
_start_validation()
    ↓
Thread.start()
    └─ SystemValidator.run_all_checks()
        ├─ validate_dependencies()
        │   ├─ Intenta importar cv2
        │   ├─ Llama callback(result)
        │   └─ after() → _update_check_result()
        │
        ├─ validate_camera()
        │   ├─ cv2.VideoCapture(0)
        │   └─ after() → _update_check_result()
        │
        ├─ validate_display()
        │   └─ Crear Tk temporal
        │
        ├─ validate_servo()
        │   └─ Simulado
        │
        └─ validate_database()
            ├─ sqlite3.connect()
            └─ after() → _update_check_result()
    ↓
_on_validation_complete()
```

### 3. Actualización de UI (Thread-Safe)
```
Callback desde Thread
    ↓
self.after(0, lambda: _update_check_result())
    ↓
MainThread
    ├─ CheckItemWidget.update_status()
    ├─ Actualizar ícono/color
    ├─ Actualizar texto
    ├─ Calcular progreso
    └─ Llamar _on_validation_complete() si termina
>>>>>>> 2e2d95e (UI de la cargainicial de dependencias test_setup.py)
```

---

<<<<<<< HEAD
## 🚀 Flujo de Ejecución Resumido

1. **Usuario ejecuta `registrar.py`**
   - Solicita datos educativos
   - Abre cámara
   - Captura rostro (presiona 'S')
   - Genera encoding de 128 dimensiones
   - Almacena en SQLite y PKL

2. **Usuario ejecuta `login.py`**
   - Carga todos los encodings registrados
   - Abre cámara
   - Compara rostro en vivo contra base de datos
   - Si coincide (distancia < 0.6): ACCESO CONCEDIDO
   - Registra en log_acceso con timestamp
   - Si no coincide: ACCESO DENEGADO

3. **Datos se persisten en SQLite**
   - Consultables offline
   - No requiere internet
   - Optimizado para Raspberry Pi

---

## 📈 Métricas de Rendimiento (Estimadas)

| Métrica | Windows 10 (i7) | Raspberry Pi 5 (4GB) |
|---------|-----------------|----------------------|
| **Detección de rostro** | ~30-50ms | ~100-200ms |
| **Encoding de rostro** | ~50-100ms | ~200-400ms |
| **Comparación (100 usuarios)** | ~5-10ms | ~20-50ms |
| **Frame rate** | 20-30 fps | 8-15 fps |
| **Resolución óptima** | 1280x720 | 640x480 |

---

## ✅ Fortalezas Actuales

✅ Diseño modular y escalable  
✅ Sin dependencia de internet  
✅ Base de datos robusta con migraciones  
✅ Dual storage (SQLite + PKL)  
✅ Perfil de cámara adaptable (Windows/RPi)  
✅ Índices optimizados para queries frecuentes  
✅ Validación de integridad referencial  

---

## ⚠️ Limitaciones Actuales

⚠️ Interfaz CLI (sin UI gráfica)  
⚠️ Sin integración con hardware (servomotores, buzzer)  
⚠️ Modelo de IA estático (no reentrenamiento)  
⚠️ Sin encriptación de datos  
⚠️ Sin gestión multiusuario de admin  
⚠️ Sin reportes visuales de asistencia  
⚠️ Rendimiento limitado en Raspberry Pi  

---

**Documento generado**: Marzo 2026  
**Versión**: 1.0  
**Estado**: Arquitectura base funcional
=======
## Estados y Transiciones

### Estados de Verificación Individual

```
     ┌──────────────┐
     │   PENDING    │
     │  • No hace    │
     │    nada aún  │
     └──────┬───────┘
            │
            │ Comenzar validación
            ↓
     ┌──────────────┐
     │  CHECKING    │ ← Ícono: ◐ (azul claro)
     │ • Ejecutando │
     │   validación │
     └──────┬───────┘
            │
      ¿Validación OK?
      ├─→ SÍ          ├─→ NO
      │                │
      ↓                ↓
┌──────────────┐  ┌──────────────┐
│  SUCCESS     │  │  ERROR       │
│ Ícono: ✓     │  │ Ícono: ✗     │
│ Color: Azul  │  │ Color: Gris  │
│ Marino       │  │              │
└──────────────┘  └──────────────┘
```

### Estados de la Aplicación

```
Inicial
  ↓
Validando (Progress: 0-100%)
  ├─→ [Si completa exitoso]
  │   ├─ Mostrar: "✓ Sistema listo"
  │   ├─ Habilitar: Botón "Continuar"
  │   └─ Opción: Abrir FaceLoginUI
  │
  └─→ [Si hay errores]
      ├─ Mostrar: "✗ N errores"
      ├─ Habilitar: Botón "Reintentar"
      └─ Opción: Corregir e reintentar
```

---

## Integración con Componentes Externos

```
┌────────────────────────────────────────────────┐
│          test_setup.py (Principal)             │
│                                                │
│  Valida existencia de:                         │
│  ├─ cv2              ← NECESARIO               │
│  ├─ face_recognition ← NECESARIO               │
│  ├─ numpy            ← NECESARIO               │
│  ├─ dlib             ← NECESARIO               │
│  ├─ PIL              ← NECESARIO               │
│  ├─ tkinter          ← NECESARIO               │
│  ├─ Puerto cámara    ← NECESARIO               │
│  └─ database/        ← NECESARIO               │
│                                                │
│       ↓                                        │
│  [Si todo OK]                                  │
│       ↓                                        │
│  ┌──────────────────────┐                      │
│  │ Intenta importar:    │                      │
│  │ from login_ui import │                      │
│  │   FaceLoginUI        │                      │
│  └─────────┬────────────┘                      │
│            │                                   │
│     ¿Existe?                                   │
│     ├─ SÍ → Abrir FaceLoginUI                 │
│     └─ NO → Mostrar mensaje y cerrar          │
└────────────────────────────────────────────────┘
```

---

## Threading Seguro

### Operación No Thread-Safe ❌
```python
# INCORRECTO - Acceso directo desde thread:
validator_thread:
    resultado = validar()
    self.label.config(text="OK")  # ❌ RuntimeError
```

### Operación Thread-Safe ✓
```python
# CORRECTO - Usar after() para actualizar desde main thread:
validator_thread:
    resultado = validar()
    self.after(0, lambda: self.label.config(text="OK"))  # ✓
```

### Implementación en el Código
```python
def validate_camera(self) -> CheckResult:
    # En thread secundario
    result = CheckResult(...)
    
    # Notificar UI de forma segura
    self.callback(result)  # → self._on_check_result()
    # Que llamará:
    # self.after(0, lambda: self._update_check_result(result))

def _on_check_result(self, result):
    # Desde el thread que llamó callback()
    self.after(0, lambda: self._update_check_result(result))
    # Ahora SÍ se puede actualizar UI con seguridad
```

---

## Puntos de Personalización

```
SystemCheckUI
│
├─ Colores (_configure_styles)
│  └─ self.colors["success"]
│  └─ self.colors["error"]
│  └─ self.colors["checking"]
│
├─ Validaciones (SystemValidator.run_all_checks)
│  └─ validate_dependencies()
│  └─ validate_camera()
│  └─ validate_display()
│  └─ validate_servo()
│  └─ validate_database()
│  └─ + TUS PROPIAS VALIDACIONES
│
├─ Mensajes (_create_widgets)
│  └─ Título de ventana
│  └─ Título de verificación
│  └─ Textos de botones
│
├─ UI (LoadingCircle, CheckItemWidget)
│  └─ Tamaño del círculo
│  └─ Velocidad de animación
│  └─ Estilos de items
│
└─ Comportamiento (_on_validation_complete)
   └─ Acción al completar
   └─ Integración con FaceLoginUI
```

---

## Colores y Temas

### Tema Azul (Por Defecto)
```python
"success": "#1f5b9f"     # Azul Marino
"error": "#808080"       # Gris
"checking": "#87ceeb"    # Azul Claro
```

### Tema Morado/Cian (Alternativo)
```python
"success": "#06b6d4"     # Cian
"error": "#a855f7"       # Morado
"checking": "#60a5fa"    # Azul Claro
```

### Tema Naranja/Gris (Profesional)
```python
"success": "#f76707"     # Naranja
"error": "#6e7781"       # Gris
"checking": "#ffa657"    # Naranja Claro
```

---

## Manejo de Errores

```
Try/Except en cada validación:

    try:
        # Validación específica
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            result.status = SUCCESS
    
    except ImportError as e:
        result.status = ERROR
        result.error_details = "Módulo no instalado"
    
    except Exception as e:
        result.status = ERROR
        result.error_details = str(e)  ← Específico del error
```

---

## Rendimiento

### Tiempos Estimados
```
Validación                  Tiempo
├─ Cada módulo              ~0.3s
├─ Cámara                   ~0.3s
├─ Pantalla                 ~0.3s
├─ Servomotor               ~0.5s
├─ Base de Datos            ~0.4s
│
└─ Total estimado:          ~3-5 segundos
  (sin contar UI rendering y animations)
```

### Threading
- ✓ UI nunca se bloquea
- ✓ Animación continúa durante validaciones
- ✓ Barra de progreso se actualiza suavemente
- ✓ Usuario puede cerrar aplicación en cualquier momento

---

## Seguridad

```
✓ Sin inyección SQL
  └─ SQLite sin queries dinámicas
  └─ Solo se verifica conexión

✓ Sin imports peligrosos
  └─ Solo importa módulos por nombre
  └─ Try/except alrededor de cada import

✓ Sin ejecución de código arbitrario
  └─ No usa eval() ni exec()
  └─ Todas las rutas de código conocidas

✓ Sin acceso de archivos peligrosos
  └─ Solo crea en database/sqlite/
  └─ Con permisos mínimos necesarios
```

---

## Escalabilidad

### Agregar Nueva Validación
```
Complejidad: O(1)

Pasos:
1. Crear método validate_nuevo()
2. Agregar a run_all_checks()
3. Método automáticamente se integra en UI
4. Threading se maneja automáticamente
5. Callbacks se procesan correctamente
```

### Agregar Nueva Categoría
```
Las categorías son dinámicas.
Simplemente crear nuevo CheckResult con:
    category="Nueva Categoría"
    
Se agrupan automáticamente en la UI
```

---

## Diagrama de Clases (UML Simplificado)

```
┌─────────────────────┐
│   CheckStatus       │ ◄─────┐
│  (Enum)             │       │
│ • PENDING           │       │
│ • CHECKING          │       │
│ • SUCCESS           │       │
│ • ERROR             │       │
└─────────────────────┘       │
                              │
┌─────────────────────┐       │
│   CheckResult       │───────┤
│  (Dataclass)        │       │
│ • name              │       │
│ • category          │       │ Usa
│ • status ───────────┼───────┘
│ • message           │
│ • error_details     │
└─────────────────────┘

┌──────────────────────┐
│  SystemValidator     │
├──────────────────────┤
│ - callback()         │
│ - results[]          │
├──────────────────────┤
│ validate_*(method)   │ Retorna
│ run_all_checks()     │ CheckResult[]
└──────────┬───────────┘

       Crea
       │
       ↓

┌──────────────────────┐
│ SystemCheckUI(tk.Tk) │
├──────────────────────┤
│ - colors             │
│ - validator          │
│ - check_items{}      │
├──────────────────────┤
│ _create_widgets()    │
│ _start_validation()  │
│ _on_check_result()   │
│ _on_validation_()    │
│ _on_continue()       │
└──────────┬───────────┘

       Contiene
       │
       ├──► LoadingCircle(Canvas)
       ├──► CheckItemWidget(Frame)[]
       ├──► ProgressBar
       └──► Buttons
```

---

## Summary

Esta arquitectura proporciona:

✅ **Separación de Responsabilidades**
- Validaciones en SystemValidator
- UI en SystemCheckUI
- Widgets especializados

✅ **Thread-Safety**
- Callbacks seguros
- Actualizaciones UI con `.after()`

✅ **Extensibilidad**
- Fácil agregar validaciones
- Personalización de colores
- Soporta múltiples temas

✅ **Mantenibilidad**
- Código modular y limpio
- Comentarios completos
- Estructura intuitiva

✅ **Performance**
- Validaciones rápidas (~5s)
- UI nunca se bloquea
- Animaciones suaves
>>>>>>> 2e2d95e (UI de la cargainicial de dependencias test_setup.py)
