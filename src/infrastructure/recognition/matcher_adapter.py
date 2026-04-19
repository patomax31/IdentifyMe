from src.infrastructure.recognition.face_engine import find_first_match


class FaceMatcherAdapter:
    def find_first_match(self, known_encodings, candidate_encoding, tolerance: float) -> int:
        return find_first_match(known_encodings, candidate_encoding, tolerance=tolerance)
