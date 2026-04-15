import os
import pickle
from typing import List, Tuple


class PklRepository:
    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = base_dir

    def load_student_biometrics(self) -> Tuple[List, List[str], List[int]]:
        encodings = []
        labels = []
        ids = []

        if not os.path.isdir(self.base_dir):
            return encodings, labels, ids

        for filename in os.listdir(self.base_dir):
            if not filename.endswith(".pkl"):
                continue

            path = os.path.join(self.base_dir, filename)
            with open(path, "rb") as file_obj:
                encoding = pickle.load(file_obj)

            label = filename.replace(".pkl", "")
            student_id = self._extract_student_id(filename)

            encodings.append(encoding)
            labels.append(label)
            ids.append(student_id)

        return encodings, labels, ids

    def save_student_biometric(self, id_estudiante: int, encoding) -> None:
        os.makedirs(self.base_dir, exist_ok=True)
        path = os.path.join(self.base_dir, f"est_{id_estudiante}.pkl")
        with open(path, "wb") as file_obj:
            pickle.dump(encoding, file_obj)

    @staticmethod
    def _extract_student_id(filename: str) -> int:
        if filename.startswith("est_") and filename.endswith(".pkl"):
            raw = filename.replace("est_", "").replace(".pkl", "")
            if raw.isdigit():
                return int(raw)
        return 0
