import cv2
import face_recognition


def detect_face_encodings_from_frame(frame, scale=0.25):
    """Return face locations and encodings from a BGR frame."""
    small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb_small)
    encodings = face_recognition.face_encodings(rgb_small, boxes)
    return boxes, encodings


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
