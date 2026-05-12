"""Detección simple de parpadeo con landmarks de face_recognition (EAR)."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import face_recognition


def _dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _eye_aspect_ratio(eye: List[Tuple[float, float]]) -> float:
    """EAR clásico para 6 puntos del ojo (orden dlib / face_recognition)."""
    if len(eye) < 6:
        return 0.28
    v1 = _dist(eye[1], eye[5])
    v2 = _dist(eye[2], eye[4])
    h = _dist(eye[0], eye[3])
    if h < 1e-6:
        return 0.28
    return (v1 + v2) / (2.0 * h)


def mean_ear_from_landmarks(landmarks: Dict[str, Any]) -> Optional[float]:
    left = landmarks.get("left_eye") or []
    right = landmarks.get("right_eye") or []
    if len(left) < 6 or len(right) < 6:
        return None
    return (_eye_aspect_ratio(left) + _eye_aspect_ratio(right)) / 2.0


def ear_from_frame_bgr(frame_bgr: Any) -> Optional[float]:
    """Calcula EAR promedio si hay exactamente un rostro en el frame."""
    import cv2

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    locs = face_recognition.face_locations(rgb, model="hog")
    if len(locs) != 1:
        return None
    marks = face_recognition.face_landmarks(rgb, locs)
    if not marks:
        return None
    return mean_ear_from_landmarks(marks[0])


@dataclass
class BlinkSessionState:
    created: float = field(default_factory=time.monotonic)
    verified: bool = False
    verified_until: float = 0.0
    # Máquina de estados simple: ojo abierto -> cerrado -> abierto = 1 parpadeo
    saw_open: bool = False
    saw_closed: bool = False
    closed_streak: int = 0
    blinks: int = 0

    OPEN_TH: float = 0.26
    CLOSED_TH: float = 0.19
    CLOSED_FRAMES: int = 2

    def push_ear(self, ear: Optional[float]) -> str:
        """Devuelve estado legible: no_face, tracking, need_blink, ready."""
        if ear is None:
            return "no_face"

        if not self.saw_open and ear >= self.OPEN_TH:
            self.saw_open = True

        if ear <= self.CLOSED_TH:
            self.closed_streak += 1
        else:
            self.closed_streak = 0

        if self.saw_open and self.closed_streak >= self.CLOSED_FRAMES:
            self.saw_closed = True

        if self.saw_closed and ear >= self.OPEN_TH:
            self.blinks += 1
            self.saw_closed = False
            self.closed_streak = 0

        if self.blinks >= 1:
            self.verified = True
            self.verified_until = time.monotonic() + 15.0
            return "ready"

        if not self.saw_open:
            return "tracking"
        return "need_blink"

    def is_verification_valid(self) -> bool:
        return self.verified and time.monotonic() <= self.verified_until


_LIVENESS: Dict[str, BlinkSessionState] = {}


def cleanup_liveness_sessions(max_age: float = 180.0) -> None:
    now = time.monotonic()
    dead = [sid for sid, st in _LIVENESS.items() if now - st.created > max_age]
    for sid in dead:
        _LIVENESS.pop(sid, None)


def start_liveness_session() -> str:
    import secrets

    cleanup_liveness_sessions()
    sid = secrets.token_urlsafe(12)
    _LIVENESS[sid] = BlinkSessionState()
    return sid


def push_liveness_frame(session_id: str, frame_bgr: Any) -> Tuple[str, str]:
    """
    Procesa un frame. Devuelve (estado, mensaje_ui).
    estado: no_face | tracking | need_blink | ready
    """
    cleanup_liveness_sessions()
    st = _LIVENESS.get(session_id)
    if st is None:
        return "error", "Sesión de liveness inválida. Reinicia la cámara."

    ear = ear_from_frame_bgr(frame_bgr)
    state = st.push_ear(ear)
    if state == "no_face":
        return "no_face", "Coloca un solo rostro frente a la cámara."
    if state == "tracking":
        return "tracking", "Mantén los ojos abiertos un momento…"
    if state == "need_blink":
        return "need_blink", "Parpadea de forma natural (un parpadeo)."
    if state == "ready":
        return "ready", "Listo. Identificando…"
    return "need_blink", "Parpadea de forma natural (un parpadeo)."


def liveness_session_ready(session_id: str) -> bool:
    st = _LIVENESS.get(session_id)
    if st is None:
        return False
    return st.is_verification_valid()
