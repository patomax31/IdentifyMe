import base64
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, jsonify, render_template, request

try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.application.auth_service import AuthService
from src.application.login_use_case import LoginUseCase
from src.application.registration_service import RegistrationService
from src.application.registration_use_case import RegistrationUseCase
from src.core.config import get_recognition_settings
from src.infrastructure.persistence.pkl_repository import PklRepository
from src.infrastructure.persistence.sqlite_repository import SQLiteRepository

RUNTIME_ERROR = None
try:
    from src.infrastructure.recognition.face_engine import detect_face_encodings_from_frame
    from src.infrastructure.recognition.matcher_adapter import FaceMatcherAdapter
except Exception as exc:
    detect_face_encodings_from_frame = None
    FaceMatcherAdapter = None
    RUNTIME_ERROR = str(exc)


app = Flask(__name__)
recognition_settings = get_recognition_settings()


class WebFaceEngine:
    def __init__(self) -> None:
        if RUNTIME_ERROR is not None:
            raise RuntimeError(RUNTIME_ERROR)

        self.login_use_case = LoginUseCase(
            auth_service=AuthService(SQLiteRepository()),
            matcher=FaceMatcherAdapter(),
            pkl_repository=PklRepository(),
            tolerance=recognition_settings.tolerance,
            cooldown_seconds=recognition_settings.access_cooldown_seconds,
        )
        self.login_use_case.initialize()

        self.registration_use_case = RegistrationUseCase(
            registration_service=RegistrationService(SQLiteRepository()),
            pkl_repository=PklRepository(),
        )
        self.registration_use_case.initialize()

        self.known_encodings = []
        self.known_labels = []
        self.known_ids = []
        self.refresh_known_students()

    def refresh_known_students(self) -> None:
        encodings, labels, ids = self.login_use_case.load_known_students()
        self.known_encodings = encodings
        self.known_labels = labels
        self.known_ids = ids


engine = None
ENGINE_ERROR = None
try:
    engine = WebFaceEngine()
except Exception as exc:
    ENGINE_ERROR = str(exc)


def _runtime_check() -> Optional[str]:
    if cv2 is None or np is None:
        return "Faltan dependencias: instala opencv-python y numpy en el entorno activo."
    if RUNTIME_ERROR is not None:
        return f"Dependencias de reconocimiento no disponibles: {RUNTIME_ERROR}"
    if ENGINE_ERROR is not None:
        return f"No se pudo inicializar el motor facial: {ENGINE_ERROR}"
    if engine is None:
        return "Motor facial no inicializado."
    return None


def _decode_image_data_uri(image_data: str):
    runtime_issue = _runtime_check()
    if runtime_issue is not None:
        return None

    if not image_data:
        return None

    payload = image_data
    if "," in image_data:
        payload = image_data.split(",", 1)[1]

    try:
        binary = base64.b64decode(payload)
    except (ValueError, TypeError):
        return None

    nparr = np.frombuffer(binary, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame


def _parse_user_data(label: str, student_id: int) -> Dict[str, Any]:
    # Label format from SQLite: "NOMBRE (2A-MATUTINO) #15"
    pattern = re.compile(r"^(?P<name>.+?)\s*\((?P<classroom>.+?)\)\s*#(?P<id>\d+)$")
    match = pattern.match(label.strip())
    if match:
        return {
            "nombre": match.group("name"),
            "salon": match.group("classroom"),
            "edad": "---",
            "id": int(match.group("id")),
        }

    return {
        "nombre": label,
        "salon": "---",
        "edad": "---",
        "id": student_id,
    }


@app.get("/")
def home() -> str:
    return render_template("home.html")


@app.get("/login")
def login_page() -> str:
    return render_template("login.html")


@app.get("/registro")
def register_page() -> str:
    return render_template("register.html")


@app.get("/api/login/status")
def login_status():
    runtime_issue = _runtime_check()
    if runtime_issue is not None:
        return jsonify({"users_count": 0, "ready": False, "message": runtime_issue})

    engine.refresh_known_students()
    return jsonify(
        {
            "users_count": len(engine.known_ids),
            "ready": len(engine.known_ids) > 0,
            "message": "Listo" if engine.known_ids else "No hay usuarios registrados",
        }
    )


@app.post("/api/login/verify")
def verify_face():
    runtime_issue = _runtime_check()
    if runtime_issue is not None:
        return jsonify({"ok": False, "state": "error", "message": runtime_issue}), 500

    payload = request.get_json(silent=True) or {}
    frame = _decode_image_data_uri(payload.get("image", ""))
    if frame is None:
        return jsonify({"ok": False, "state": "error", "message": "Imagen invalida"}), 400

    engine.refresh_known_students()
    if not engine.known_encodings:
        return jsonify(
            {
                "ok": False,
                "state": "error",
                "message": "ERROR: No hay usuarios registrados",
            }
        ), 400

    _, encodings = detect_face_encodings_from_frame(frame, scale=recognition_settings.scale)

    if len(encodings) == 0:
        return jsonify(
            {
                "ok": True,
                "state": "waiting",
                "message": "ESPERANDO ROSTRO...",
                "user": None,
            }
        )

    if len(encodings) > 1:
        return jsonify(
            {
                "ok": True,
                "state": "positioning",
                "message": "CENTRA TU ROSTRO",
                "user": None,
            }
        )

    result = engine.login_use_case.process_frame(
        [encodings[0]],
        engine.known_encodings,
        engine.known_labels,
        engine.known_ids,
    )

    if "ACCESO CONCEDIDO" in result.message:
        idx = engine.login_use_case.matcher.find_first_match(
            engine.known_encodings,
            encodings[0],
            tolerance=recognition_settings.tolerance,
        )
        user_data = None
        if idx >= 0 and idx < len(engine.known_labels):
            user_data = _parse_user_data(engine.known_labels[idx], engine.known_ids[idx])

        return jsonify(
            {
                "ok": True,
                "state": "granted",
                "message": result.message,
                "user": user_data,
            }
        )

    return jsonify(
        {
            "ok": True,
            "state": "denied",
            "message": result.message,
            "user": None,
        }
    )


@app.post("/api/registro")
def register_face():
    runtime_issue = _runtime_check()
    if runtime_issue is not None:
        return jsonify({"ok": False, "message": runtime_issue}), 500

    payload = request.get_json(silent=True) or {}

    nombre = str(payload.get("nombre", "")).strip()
    grado_raw = str(payload.get("grado", "")).strip()
    letra = str(payload.get("letra", "")).strip().upper()
    turno = str(payload.get("turno", "")).strip().upper()

    if not nombre:
        return jsonify({"ok": False, "message": "Dato invalido. El nombre es obligatorio."}), 400

    if grado_raw not in {"1", "2", "3"}:
        return jsonify({"ok": False, "message": "Dato invalido. El grado debe ser 1, 2 o 3."}), 400

    if len(letra) != 1 or not letra.isalpha():
        return jsonify({"ok": False, "message": "Dato invalido. Ingresa una sola letra (A-Z)."}), 400

    if turno not in {"MATUTINO", "VESPERTINO"}:
        return jsonify({"ok": False, "message": "Dato invalido. Usa MATUTINO o VESPERTINO."}), 400

    frame = _decode_image_data_uri(payload.get("image", ""))
    if frame is None:
        return jsonify({"ok": False, "message": "Imagen invalida"}), 400

    _, encodings = detect_face_encodings_from_frame(frame, scale=recognition_settings.scale)
    result = engine.registration_use_case.register_from_detected_faces(
        nombre,
        int(grado_raw),
        letra,
        turno,
        encodings,
    )

    if not result.success:
        return jsonify({"ok": False, "message": result.message}), 400

    engine.refresh_known_students()
    return jsonify({"ok": True, "message": result.message, "student_id": result.student_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
