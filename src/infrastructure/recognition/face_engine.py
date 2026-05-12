import cv2
import face_recognition


def detect_face_encodings_from_frame(frame, scale=0.25):
    """Return face locations and encodings from a BGR frame."""
    small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb_small)
    encodings = face_recognition.face_encodings(rgb_small, boxes)
    return boxes, encodings


def _registration_scales(base_scale: float):
    """Prueba primero escalas altas (cara más grande en píxeles): los perfiles se detectan mejor."""
    base = max(0.12, min(1.0, float(base_scale)))
    raw = [1.0, 0.85, 0.7, 0.55, max(0.35, base * 2.0), base]
    seen = set()
    out = []
    for x in raw:
        k = round(x, 4)
        if k not in seen and k >= 0.12:
            seen.add(k)
            out.append(k)
    return out


def detect_face_encodings_from_frame_robust(frame, base_scale: float = 0.25):
    """
    Igual que detect_face_encodings_from_frame pero reintenta con varias escalas y
    upsample en HOG. Pensado para registro (frente y perfiles): los perfiles suelen
    no aparecer si solo se analiza el frame muy pequeño.
    """
    if frame is None or frame.size == 0:
        return [], []

    for scale in _registration_scales(base_scale):
        if scale >= 0.999:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(
            rgb,
            number_of_times_to_upsample=1,
            model="hog",
        )
        encodings = face_recognition.face_encodings(rgb, boxes, num_jitters=1)
        if len(encodings) >= 1:
            return boxes, encodings

    return [], []


def encode_single_face_from_frame(frame):
    """Return encoding when exactly one face is present, otherwise None."""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb_frame)
    if len(boxes) != 1:
        return None
    return face_recognition.face_encodings(rgb_frame, boxes)[0]


def find_first_match(known_encodings, candidate_encoding, tolerance=0.5):
    """Return index of first match, or -1 when no match exists."""
    matches = face_recognition.compare_faces(known_encodings, candidate_encoding, tolerance=tolerance)
    if True in matches:
        return matches.index(True)
    return -1
