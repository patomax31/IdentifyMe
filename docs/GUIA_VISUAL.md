# 🎨 GUÍA VISUAL - Interfaz de Usuario

## Pantalla Principal de Verificación

### Estado 1: Iniciando

```
╔═══════════════════════════════════════════════════════════╗
║                     [ × ]                                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║    Inicializando sistema de acceso facial                 ║
║                                                            ║
║                   ┌─────────────┐                          ║
║                   │             │                          ║
║                   │      ◐      │   ← Círculo animado      ║
║                   │             │     (rotación suave)    ║
║                   └─────────────┘                          ║
║                                                            ║
║           ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%       ║
║                                                            ║
║    Verificaciones                                          ║
║    ─────────────────────────────────────────────────────  ║
║    ◐ cv2 (OpenCV)           Verificando...               ║
║    • NumPy                  Pendiente...                  ║
║    • dlib                   Pendiente...                  ║
║    • PIL (Pillow)           Pendiente...                  ║
║    • face_recognition       Pendiente...                  ║
║    • Tkinter                Pendiente...                  ║
║    • Cámara                 Pendiente...                  ║
║    • Pantalla               Pendiente...                  ║
║    • Servomotor             Pendiente...                  ║
║    • Base de Datos          Pendiente...                  ║
║                                                            ║
║                                                            ║
║                    [Reintentar]  [Continuar]             ║
║                    (deshabilitados)                        ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝

Leyenda:
✓ = Éxito (Azul Marino #1f5b9f)
✗ = Error (Gris #808080)
◐ = Verificando (Azul Claro #87ceeb)
• = Pendiente (Gris claro)
```

---

### Estado 2: Verificación en Progreso (50%)

```
╔═══════════════════════════════════════════════════════════╗
║                     [ × ]                                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║    Inicializando sistema de acceso facial                 ║
║                                                            ║
║                   ┌─────────────┐                          ║
║                   │             │                          ║
║                   │      ◐      │   ← Sigue rotando       ║
║                   │             │                          ║
║                   └─────────────┘                          ║
║                                                            ║
║    ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 50%  ║
║                                                            ║
║    Verificaciones                                          ║
║    ─────────────────────────────────────────────────────  ║
║    ✓ cv2 (OpenCV)           OK                           ║
║    ✓ NumPy                  OK                           ║
║    ✓ dlib                   OK                           ║
║    ◐ PIL (Pillow)           Verificando...               ║
║    ◐ face_recognition       Verificando...               ║
║    • Tkinter                Pendiente...                  ║
║    • Cámara                 Pendiente...                  ║
║    • Pantalla               Pendiente...                  ║
║    • Servomotor             Pendiente...                  ║
║    • Base de Datos          Pendiente...                  ║
║                                                            ║
║                    [Reintentar]  [Continuar]             ║
║                    (deshabilitados)                        ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝

Colores:
✓ = Verde/Azul Marino (éxito)
◐ = Azul Claro (verificando)
```

---

### Estado 3: Todo Completado - Éxito ✓

```
╔═══════════════════════════════════════════════════════════╗
║                     [ × ]                                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║    Inicializando sistema de acceso facial                 ║
║                                                            ║
║                   ┌─────────────┐                          ║
║                   │             │                          ║
║                   │      ✓      │   ← Detiene y muestra   ║
║                   │             │     marca de éxito      ║
║                   └─────────────┘                          ║
║                                                            ║
║    ████████████████████████████████████████████████████100%║
║                 ✓ Sistema listo                            ║
║                                                            ║
║    Verificaciones                                          ║
║    ─────────────────────────────────────────────────────  ║
║    ✓ cv2 (OpenCV)           OK                           ║
║    ✓ NumPy                  OK                           ║
║    ✓ dlib                   OK                           ║
║    ✓ PIL (Pillow)           OK                           ║
║    ✓ face_recognition       OK                           ║
║    ✓ Tkinter                OK                           ║
║    ✓ Cámara                 OK                           ║
║    ✓ Pantalla               OK                           ║
║    ✓ Servomotor             OK (Simulado)                ║
║    ✓ Base de Datos          OK                           ║
║                                                            ║
║                    [Reintentar]  [✓ Continuar]            ║
║                    (deshabilitado) (habilitado)            ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝

Todas las validaciones en VERDE = Éxito
Botón "Continuar" se habilita automáticamente
```

---

### Estado 4: Con Errores ✗

```
╔═══════════════════════════════════════════════════════════╗
║                     [ × ]                                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║    Inicializando sistema de acceso facial                 ║
║                                                            ║
║                   ┌─────────────┐                          ║
║                   │             │                          ║
║                   │      ✗      │   ← Indica error        ║
║                   │             │                          ║
║                   └─────────────┘                          ║
║                                                            ║
║    ████████████████████████████████████████████████████100%║
║            ✗ 2 error(es) encontrados                      ║
║                                                            ║
║    Verificaciones                                          ║
║    ─────────────────────────────────────────────────────  ║
║    ✓ cv2 (OpenCV)           OK                           ║
║    ✓ NumPy                  OK                           ║
║    ✗ dlib                   Error - Módulo no encontrado ║
║    ✓ PIL (Pillow)           OK                           ║
║    ✓ face_recognition       OK                           ║
║    ✓ Tkinter                OK                           ║
║    ✓ Cámara                 OK                           ║
║    ✗ Base de Datos          Error - Permiso denegado     ║
║    ✓ Pantalla               OK                           ║
║    ✓ Servomotor             OK (Simulado)                ║
║                                                            ║
║                    [✓ Reintentar]  [Continuar]            ║
║                    (habilitado)    (deshabilitado)         ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝

✗ = Rojo/Gris (error)
Botón "Reintentar" se habilita
Botón "Continuar" se deshabilita
```

---

## Cuadros de Diálogo

### Mensaje de Éxito (MessageBox)

```
╔════════════════════════════════════════╗
║          Sistema Listo                 ║
╠════════════════════════════════════════╣
║                                        ║
║  ✓ Todas las verificaciones fueron     ║
║    completadas correctamente.          ║
║                                        ║
║  Haz clic en 'Continuar' para          ║
║  acceder a la interfaz principal.      ║
║                                        ║
║              [ OK ]                    ║
║                                        ║
╚════════════════════════════════════════╝
```

---

### Mensaje de Error (MessageBox)

```
╔════════════════════════════════════════╗
║      Errores de Verificación          ║
╠════════════════════════════════════════╣
║                                        ║
║  Se encontraron los siguientes         ║
║  errores:                              ║
║                                        ║
║  • dlib: Módulo no encontrado          ║
║  • Base de Datos: Permiso denegado     ║
║                                        ║
║  Por favor, instala las dependencias   ║
║  faltantes e intenta nuevamente.       ║
║                                        ║
║              [ OK ]                    ║
║                                        ║
╚════════════════════════════════════════╝
```

---

## Componentes Visuales Detallados

### Círculo de Carga Animado

```
Frame 1        Frame 2        Frame 3        Frame 4
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│  ●  ○  │    │   ○  ● │    │  ○  ●  │    │  ●  ○  │
│ ○      │    │        │    │        │    │ ○      │
│  ○  ○  │    │  ○  ○  │    │  ●  ○  │    │  ○  ○  │
└────────┘    └────────┘    └────────┘    └────────┘

Rotación: 15° cada 50ms
Color: Azul Marino (#1f5b9f)
Tamaño: 80x80 pixels
```

---

### Barra de Progreso

```
Vacía (0%)
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

25%
████▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

50%
████████████████▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

75%
████████████████████████▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬

100%
████████████████████████████████████████

Color: Azul Marino (#1f5b9f)
Fondo: Gris claro (#f5f5f5)
```

---

### Items de Verificación

```
Pendiente:
• Componente           Pendiente...

Verificando:
◐ Componente           Verificando...

Éxito:
✓ Componente           OK

Error:
✗ Componente           Error - Descripción del error
```

---

## Paleta de Colores

### Colores Principales

| Color | Código | Uso |
|-------|--------|-----|
| Azul Marino | #1f5b9f | Éxito, botón principal |
| Gris | #808080 | Error |
| Azul Claro | #87ceeb | Verificando |
| Blanco | #ffffff | Fondo principal |
| Gris Claro | #f5f5f5 | Fondo secundario |
| Texto Oscuro | #333333 | Títulos |
| Texto Gris | #666666 | Texto secundario |

### Ejemplo Visual de Colores

```
Éxito:  ■ #1f5b9f (Azul Marino)
Error:  ■ #808080 (Gris)
Check:  ■ #87ceeb (Azul Claro)
BG:     ■ #ffffff (Blanco)
```

---

## Disposición de Elementos (Layout)

### Estructura Vertical

```
┌────────────────────────────────────────────┐
│  Título Principal                  [20px]  │
├────────────────────────────────────────────┤
│                                            │
│         Círculo de Carga              80px │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  Barra de Progreso + % completado     30px │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  Etiqueta "Verificaciones"            20px │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ ScrollArea con Items                 │  │
│  │                                      │  │
│  │ ✓ Item 1                      OK     │  │
│  │ ─────────────────────────────────    │  │
│  │ ✓ Item 2                      OK     │  │
│  │ ─────────────────────────────────    │  │
│  │ ✓ Item 3                      OK     │  │
│  │                                      │  │
│  └──────────────────────────────────────┘  │
│                              (Variable)    │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  [Reintentar]  [Continuar a UI]       40px │
│                                            │
└────────────────────────────────────────────┘
```

---

## Dimensiones

```
Ventana Principal:
├─ Ancho: 600px
└─ Altura: 700px (ajustable según contenido)

Elementos:
├─ Círculo: 80×80px
├─ Barra: 500px ancho
├─ Items: 100% ancho del container
└─ Botones: ~150px ancho c/u

Espaciado:
├─ Padding: 20px general
├─ Pady (vertical): 10-20px
└─ Espacios entre elementos: 5-15px
```

---

## Tipografía

```
Títulos:
├─ Fuente: Segoe UI
├─ Tamaño: 16pt
└─ Peso: Bold

Subtítulos:
├─ Fuente: Segoe UI
├─ Tamaño: 11pt
└─ Peso: Bold

Texto Normal:
├─ Fuente: Segoe UI
├─ Tamaño: 10pt
└─ Peso: Normal

Texto Secundario:
├─ Fuente: Segoe UI
├─ Tamaño: 9pt
└─ Peso: Normal
```

---

## Animaciones

### Círculo de Carga

```
Velocidad: 15° cada 50ms (1 rotación = ~1.2s)
Tipo: Rotación continua
Estado: Inactivo en inicio/fin
```

### Barra de Progreso

```
Animación: Suave (lineal)
Velocidad: Se actualiza según validaciones
Duración: ~3-5 segundos total
```

### Items

```
Animación: Fade in cuando aparecen
Color: Cambia al actualizar estado
Separador: Línea que divide items
```

---

## Estados de Botones

### Botón "Continuar"

```
Deshabilitado (por defecto):
┌──────────────────────┐
│ Continuar a UI...    │  ← Gris, no clickeable
└──────────────────────┘

Habilitado (si éxito):
┌──────────────────────┐
│ Continuar a UI...    │  ← Azul Marino, cursor mano
└──────────────────────┘
Hover: Más oscuro
Click: Abre FaceLoginUI
```

### Botón "Reintentar"

```
Deshabilitado (por defecto):
┌──────────────────────┐
│ Reintentar           │  ← Gris, no clickeable
└──────────────────────┘

Habilitado (si error):
┌──────────────────────┐
│ Reintentar           │  ← Gris oscuro, cursor mano
└──────────────────────┘
Hover: Más oscuro
Click: Reinicia validaciones
```

---

## Casos de Uso Visuales

### Caso 1: Usuario Espera Éxito
```
1. Inicia aplicación
2. Ve círculo rotando
3. Items aparecen con ✓
4. Barra sube al 100%
5. Botón "Continuar" se habilita
6. Hace click → Abre FaceLoginUI
```

### Caso 2: Usuario Tiene Errores
```
1. Inicia aplicación
2. Ve círculo rotando
3. Algunos items con ✗
4. Mensaje de error
5. Botón "Reintentar" se habilita
6. Hace click → Reinicia
```

### Caso 3: Usuario Cierra Ventana
```
1. En cualquier momento puede cerrar
2. Se detiene la validación
3. Thread se limpia
4. Aplicación se cierra
```

---

## Responsive Design

### Cuando la ventana se redimensiona

```
Ancho < 600px:
├─ Se desactiva el redimensionamiento
└─ Ancho mínimo: 600px

Alto < 700px:
├─ ScrollArea se ajusta
└─ Altura mínima: 700px (aproximado)

Zoom del usuario:
├─ Mantiene proporciones
└─ Todo se escala proporcionalmente
```

---

## Notificaciones (Dialogs)

### Pop-ups (MessageBox)

```
Título: Sistema Listo / Errores de Verificación
Tipo: Información o Error
Botón: OK
Cierre: Click OK o X

Se muestran cuando:
├─ Verificación completada exitosamente
└─ Se encuentran errores
```

---

## Resumen Visual

El diseño es:
- ✓ Moderno y limpio
- ✓ Profesional
- ✓ Intuitivo
- ✓ Responsive
- ✓ Accesible
- ✓ Rápido de comprender

Los colores transmiten:
- Azul Marino = Confianza, Éxito
- Gris = Neutral, Error
- Azul Claro = Actividad, Procesamiento
- Blanco = Limpieza, Espacio

La disposición permite:
- Fácil lectura del estado
- Seguimiento del progreso
- Identificación clara de errores
- Experiencia positiva del usuario

¡La interfaz está lista para impresionar! ✨
