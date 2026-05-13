import unittest

from src.application.auth_service import AuthService


class FakeRepo:
    def __init__(self):
        self.initialized = False
        self.logged = []
        self.known_students = (["enc1"], ["1A-MATUTINO #1"], [1])

    def initialize(self):
        self.initialized = True

    def load_active_student_biometrics(self):
        return self.known_students

    def log_student_access(self, student_id, granted):
        self.logged.append((student_id, granted))


class AuthServiceTests(unittest.TestCase):
    def test_initialize_delegates_to_repository(self):
        repo = FakeRepo()
        service = AuthService(repo)

        service.initialize()

        self.assertTrue(repo.initialized)

    def test_load_known_students_returns_repository_data(self):
        repo = FakeRepo()
        service = AuthService(repo)

        known = service.load_known_students()

        self.assertEqual(repo.known_students, known)

    def test_log_access_delegates_with_arguments(self):
        repo = FakeRepo()
        service = AuthService(repo)

        service.log_access(7, True)

        self.assertEqual([(7, True)], repo.logged)


if __name__ == "__main__":
    unittest.main()
