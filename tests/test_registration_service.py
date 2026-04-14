import unittest

from src.application.registration_service import RegistrationService


class FakeRepo:
    def __init__(self):
        self.initialized = False
        self.created = []
        self.saved = []
        self.next_id = 1

    def initialize(self):
        self.initialized = True

    def create_student(self, grado, letra, turno):
        self.created.append((grado, letra, turno))
        student_id = self.next_id
        self.next_id += 1
        return student_id

    def save_student_biometric(self, student_id, encoding):
        self.saved.append((student_id, encoding))


class RegistrationServiceTests(unittest.TestCase):
    def test_initialize_delegates_to_repository(self):
        repo = FakeRepo()
        service = RegistrationService(repo)

        service.initialize()

        self.assertTrue(repo.initialized)

    def test_register_student_with_encoding_creates_and_saves(self):
        repo = FakeRepo()
        service = RegistrationService(repo)
        encoding = [0.1, 0.2, 0.3]

        student_id = service.register_student_with_encoding(2, "B", "VESPERTINO", encoding)

        self.assertEqual(1, student_id)
        self.assertEqual([(2, "B", "VESPERTINO")], repo.created)
        self.assertEqual([(1, encoding)], repo.saved)


if __name__ == "__main__":
    unittest.main()
