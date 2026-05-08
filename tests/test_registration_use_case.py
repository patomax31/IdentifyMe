import unittest

from src.application.registration_use_case import RegistrationUseCase


class FakeRegistrationService:
    def __init__(self):
        self.initialized = False
        self.calls = []
        self.next_id = 1
        self.error = None

    def initialize(self):
        self.initialized = True

    def register_student_with_encoding(self, nombre, grado, letra, turno, encoding):
        if self.error is not None:
            raise self.error
        self.calls.append((nombre, grado, letra, turno, encoding))
        student_id = self.next_id
        self.next_id += 1
        return student_id


class FakePklRepository:
    def __init__(self):
        self.saved = []

    def load_student_biometrics(self):
        return [], [], []

    def save_student_biometric(self, id_estudiante, encoding):
        self.saved.append((id_estudiante, encoding))


class RegistrationUseCaseTests(unittest.TestCase):
    def test_unique_face_registers_successfully(self):
        service = FakeRegistrationService()
        pkl = FakePklRepository()
        use_case = RegistrationUseCase(service, pkl)

        result = use_case.register_from_detected_faces("Juan Perez", 2, "B", "VESPERTINO", ["enc_1"])

        self.assertTrue(result.success)
        self.assertEqual(1, result.student_id)
        self.assertEqual([("Juan Perez", 2, "B", "VESPERTINO", "enc_1")], service.calls)
        self.assertEqual([(1, "enc_1")], pkl.saved)

    def test_zero_faces_returns_controlled_error(self):
        service = FakeRegistrationService()
        pkl = FakePklRepository()
        use_case = RegistrationUseCase(service, pkl)

        result = use_case.register_from_detected_faces("Juan Perez", 2, "B", "VESPERTINO", [])

        self.assertFalse(result.success)
        self.assertIsNone(result.student_id)
        self.assertIn("ningun rostro", result.message)
        self.assertEqual([], service.calls)
        self.assertEqual([], pkl.saved)

    def test_multiple_faces_returns_controlled_error(self):
        service = FakeRegistrationService()
        pkl = FakePklRepository()
        use_case = RegistrationUseCase(service, pkl)

        result = use_case.register_from_detected_faces("Juan Perez", 2, "B", "VESPERTINO", ["enc_1", "enc_2"])

        self.assertFalse(result.success)
        self.assertIsNone(result.student_id)
        self.assertIn("multiples rostros", result.message)
        self.assertEqual([], service.calls)
        self.assertEqual([], pkl.saved)

    def test_duplicate_student_returns_controlled_error(self):
        service = FakeRegistrationService()
        service.error = ValueError("El estudiante ya existe en la base de datos.")
        pkl = FakePklRepository()
        use_case = RegistrationUseCase(service, pkl)

        result = use_case.register_from_detected_faces("Juan Perez", 2, "B", "VESPERTINO", ["enc_1"])

        self.assertFalse(result.success)
        self.assertIsNone(result.student_id)
        self.assertIn("ya existe", result.message)
        self.assertEqual([], service.calls)
        self.assertEqual([], pkl.saved)


if __name__ == "__main__":
    unittest.main()
