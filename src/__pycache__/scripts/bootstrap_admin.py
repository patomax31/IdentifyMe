import cv2
from getpass import getpass

from database.sqlite_manager import count_active_staff, create_staff, save_staff_biometric
from src.core.config import get_recognition_settings
from src.infrastructure.camera.opencv_camera import open_camera
from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame


def solicitar_datos_primer_admin():
    print("Bootstrap de primer personal administrativo")

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

    return num_empleado, nombre_completo, correo, password


def capturar_encoding_unico(recognition_settings):
    cap = open_camera()
    if cap is None:
        print("No se pudo acceder a la camara. Cierra otras apps que la usen e intenta de nuevo.")
        return None

    print("Alinea el rostro y presiona 'S' para capturar biometria. Presiona 'Q' para cancelar.")

    encoding = None
    window_title = "Bootstrap Primer Admin"
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

            encoding = encodings[0]
            break

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return encoding


def main():
    if count_active_staff() > 0:
        print("Ya existe personal administrativo activo. Bootstrap cancelado.")
        return

    recognition_settings = get_recognition_settings()
    num_empleado, nombre_completo, correo, password = solicitar_datos_primer_admin()

    encoding = capturar_encoding_unico(recognition_settings)
    if encoding is None:
        print("No se capturo biometria. Bootstrap cancelado.")
        return

    try:
        id_personal = create_staff(
            num_empleado=num_empleado,
            nombre_completo=nombre_completo,
            rol="SUPERADMIN",
            correo=correo,
            password_plain=password,
        )
        save_staff_biometric(id_personal, encoding)
    except ValueError as exc:
        print(str(exc))
        return

    print(f"Primer SUPERADMIN creado correctamente. ID interno: {id_personal}.")


if __name__ == "__main__":
    main()
