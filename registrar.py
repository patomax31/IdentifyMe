import cv2
from getpass import getpass
from typing import Callable, Optional

from database.sqlite_manager import count_active_staff, create_staff, load_staff_biometrics, log_access, save_staff_biometric
from src.application.registration_service import RegistrationService
from src.application.registration_use_case import RegistrationUseCase
from src.core.config import get_recognition_settings
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame
from src.infrastructure.recognition.matcher_adapter import FaceMatcherAdapter


def solicitar_datos_estudiante_y_grupo():
    while True:
        nombre = input("Nombre del estudiante: ").strip()
        if nombre:
            break
        print("Dato invalido. El nombre es obligatorio.")

    while True:
        grado_raw = input("Grado del estudiante (1-3): ").strip()
        if grado_raw in {"1", "2", "3"}:
            grado = int(grado_raw)
            break
        print("Dato invalido. El grado debe ser 1, 2 o 3.")

    while True:
        letra = input("Letra del grupo (A-Z): ").strip().upper()
        if len(letra) == 1 and letra.isalpha():
            break
        print("Dato invalido. Ingresa una sola letra (A-Z).")

    while True:
        turno = input("Turno (MATUTINO/VESPERTINO): ").strip().upper()
        if turno in {"MATUTINO", "VESPERTINO"}:
            break
        print("Dato invalido. Usa MATUTINO o VESPERTINO.")

    return nombre, grado, letra, turno


def solicitar_datos_personal():
    while True:
        num_empleado = input("Numero de empleado: ").strip().upper()
        if num_empleado:
            break
        print("Dato invalido. El numero de empleado es obligatorio.")

    while True:
        nombre_completo = input("Nombre completo: ").strip()
        if nombre_completo:
            break
        print("Dato invalido. El nombre completo es obligatorio.")

    while True:
        rol = input("Rol (SUPERADMIN/ADMIN_REGISTRO/OPERADOR): ").strip().upper()
        if rol in {"SUPERADMIN", "ADMIN_REGISTRO", "OPERADOR"}:
            break
        print("Dato invalido. Usa SUPERADMIN, ADMIN_REGISTRO u OPERADOR.")

    while True:
        correo = input("Correo institucional: ").strip().lower()
        if "@" in correo:
            break
        print("Dato invalido. El correo no es valido.")

    while True:
        password = getpass("Contrasena (minimo 8 caracteres): ").strip()
        if len(password) < 8:
            print("Dato invalido. Debe tener al menos 8 caracteres.")
            continue

        confirm = getpass("Confirmar contrasena: ").strip()
        if password == confirm:
            break

        print("Las contrasenas no coinciden. Intenta de nuevo.")

    return num_empleado, nombre_completo, rol, correo, password

def _notify(state_callback: Optional[Callable[[str], None]], message: str) -> None:
    if state_callback is not None:
        state_callback(message)


def _capturar_encoding_desde_camara(
    recognition_settings,
    *,
    window_title: str,
    top_text: str,
) -> Optional[object]:
    cap = open_camera()
    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return None

    print(top_text)

    captured_encoding = None
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4))

        cv2.ellipse(frame, centro, ejes, 0, 0, 360, (255, 255, 0), 2)
        cv2.putText(
            frame,
            "Encuadra tu rostro aqui",
            (centro[0] - 120, centro[1] - ejes[1] - 20),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            (255, 255, 0),
            1,
        )
        cv2.putText(
            frame,
            "Presiona 'S' para capturar o 'Q' para salir",
            (10, alto - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

        cv2.imshow(window_title, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            _, encodings = detect_face_encodings_from_frame(frame, scale=recognition_settings.scale)
            if len(encodings) != 1:
                print("Captura invalida. Debe detectarse un solo rostro.")
                continue

            captured_encoding = encodings[0]
            break

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured_encoding


def _autenticar_personal_para_registro(recognition_settings) -> Optional[dict]:
    if count_active_staff() == 0:
        print("No hay personal administrativo activo. Se habilita modo bootstrap para primer SUPERADMIN.")
        return {
            "id_personal": 0,
            "nombre": "BOOTSTRAP",
            "rol": "SUPERADMIN",
            "bootstrap": True,
        }

    rostros_personal, nombres_personal, ids_personal, roles_personal = load_staff_biometrics()
    if not rostros_personal:
        print("No hay biometria de personal registrada. Ejecuta bootstrap_admin.py para inicializar.")
        return None

    matcher = FaceMatcherAdapter()
    encoding = _capturar_encoding_desde_camara(
        recognition_settings,
        window_title="Autenticacion Personal Administrativo",
        top_text="Autentica personal administrativo antes de registrar. Presiona 'S' para validar.",
    )
    if encoding is None:
        return None

    idx = matcher.find_first_match(
        rostros_personal,
        encoding,
        tolerance=recognition_settings.tolerance,
    )
    if idx < 0:
        print("Autenticacion denegada. No coincide con personal administrativo.")
        return None

    personal_id = ids_personal[idx]
    log_access(personal_id, True, tipo_usuario="PERSONAL")
    return {
        "id_personal": personal_id,
        "nombre": nombres_personal[idx],
        "rol": roles_personal[idx],
        "bootstrap": False,
    }


def _registrar_estudiante(use_case: RegistrationUseCase, recognition_settings, state_callback: Optional[Callable[[str], None]]) -> None:
    nombre, grado, letra, turno = solicitar_datos_estudiante_y_grupo()
    cap = open_camera()

    if cap is None:
        message = "No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo."
        print(message)
        _notify(state_callback, message)
        return

    start_message = f"Registrando a {nombre} en {grado}{letra}-{turno}. Presiona 'S' para capturar o 'Q' para salir."
    print(start_message)
    _notify(state_callback, start_message)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        alto, ancho, _ = frame.shape
        centro = (ancho // 2, alto // 2)
        ejes = (int(ancho * 0.25), int(alto * 0.4))

        cv2.ellipse(frame, centro, ejes, 0, 0, 360, (255, 255, 0), 2)
        cv2.putText(
            frame,
            "Encuadra tu rostro aqui",
            (centro[0] - 120, centro[1] - ejes[1] - 20),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            (255, 255, 0),
            1,
        )
        cv2.putText(
            frame,
            "Presiona 'S' para Guardar",
            (10, alto - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

        cv2.imshow("Registro Biometrico", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            _, encodings = detect_face_encodings_from_frame(frame, scale=recognition_settings.scale)
            result = use_case.register_from_detected_faces(nombre, grado, letra, turno, encodings)

            print(result.message)
            _notify(state_callback, result.message)
            if result.success:
                break

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def _registrar_personal(recognition_settings, state_callback: Optional[Callable[[str], None]]) -> None:
    num_empleado, nombre_completo, rol, correo, password = solicitar_datos_personal()
    encoding = _capturar_encoding_desde_camara(
        recognition_settings,
        window_title="Registro de Personal Administrativo",
        top_text=(
            f"Registrando personal {nombre_completo} ({rol}). "
            "Presiona 'S' para capturar biometria o 'Q' para cancelar."
        ),
    )
    if encoding is None:
        _notify(state_callback, "Registro de personal cancelado.")
        return

    try:
        id_personal = create_staff(
            num_empleado=num_empleado,
            nombre_completo=nombre_completo,
            rol=rol,
            correo=correo,
            password_plain=password,
        )
        save_staff_biometric(id_personal, encoding)
    except ValueError as exc:
        print(str(exc))
        _notify(state_callback, str(exc))
        return

    message = f"Personal administrativo registrado con exito. ID interno: {id_personal}."
    print(message)
    _notify(state_callback, message)


def registrar_usuario(state_callback: Optional[Callable[[str], None]] = None):
    _notify(state_callback, "Inicializando registro biometrico...")
    recognition_settings = get_recognition_settings()

    actor = _autenticar_personal_para_registro(recognition_settings)
    if actor is None:
        _notify(state_callback, "No fue posible autenticar personal administrativo.")
        return

    if actor["bootstrap"]:
        print("Modo bootstrap activo: solo se permite registrar el primer SUPERADMIN.")
        _registrar_personal(recognition_settings, state_callback)
        _notify(state_callback, "Registro biometrico finalizado.")
        return

    welcome = f"Personal autenticado: {actor['nombre']}"
    print(welcome)
    _notify(state_callback, welcome)

    use_case = RegistrationUseCase(
        registration_service=RegistrationService(SQLiteRepository()),
        pkl_repository=PklRepository(),
    )
    use_case.initialize()

    while True:
        print("\nSelecciona tipo de registro:")
        print("1) Estudiante")
        print("2) Personal administrativo")
        print("Q) Salir")
        choice = input("Opcion: ").strip().upper()

        if choice == "1":
            _registrar_estudiante(use_case, recognition_settings, state_callback)
            break

        if choice == "2":
            if actor["rol"] not in {"SUPERADMIN", "ADMIN_REGISTRO"}:
                denied = "No tienes permisos para registrar personal administrativo."
                print(denied)
                _notify(state_callback, denied)
                continue

            _registrar_personal(recognition_settings, state_callback)
            break

        if choice == "Q":
            break

        print("Opcion invalida. Usa 1, 2 o Q.")

    _notify(state_callback, "Registro biometrico finalizado.")

if __name__ == "__main__":
    registrar_usuario()