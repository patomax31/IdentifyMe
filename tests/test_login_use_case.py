import unittest

from src.application.login_use_case import LoginUseCase


class FakeAuthService:
    def __init__(self):
        self.initialized = False
        self.known_students = (["enc_known"], ["1A-MATUTINO #1"], [1])
        self.logged = []

    def initialize(self):
        self.initialized = True

    def load_known_students(self):
        return self.known_students

    def log_access(self, student_id, granted):
        self.logged.append((student_id, granted))


class FakeMatcher:
    def __init__(self, result_index):
        self.result_index = result_index

    def find_first_match(self, known_encodings, candidate_encoding, tolerance):
        return self.result_index


class FakePklRepository:
    def __init__(self, encodings=None, labels=None, ids=None):
        self.encodings = encodings or []
        self.labels = labels or []
        self.ids = ids or []

    def load_student_biometrics(self):
        return self.encodings, self.labels, self.ids

    def save_student_biometric(self, id_estudiante, encoding):
        pass


class LoginUseCaseTests(unittest.TestCase):
    def test_access_granted_when_match_exists(self):
        auth = FakeAuthService()
        use_case = LoginUseCase(
            auth_service=auth,
            matcher=FakeMatcher(result_index=0),
            tolerance=0.5,
            cooldown_seconds=8.0,
        )

        result = use_case.process_frame(["enc_frame"], ["enc_known"], ["1A-MATUTINO #1"], [1])

        self.assertEqual("ACCESO CONCEDIDO: 1A-MATUTINO #1", result.message)
        self.assertEqual((0, 255, 0), result.color)
        self.assertEqual([(1, True)], auth.logged)

    def test_access_denied_when_no_match(self):
        auth = FakeAuthService()
        use_case = LoginUseCase(
            auth_service=auth,
            matcher=FakeMatcher(result_index=-1),
            tolerance=0.5,
            cooldown_seconds=8.0,
        )

        result = use_case.process_frame(["enc_frame"], ["enc_known"], ["1A-MATUTINO #1"], [1])

        self.assertEqual("ACCESO DENEGADO", result.message)
        self.assertEqual((0, 0, 255), result.color)
        self.assertEqual([], auth.logged)

    def test_cooldown_prevents_duplicate_logs(self):
        auth = FakeAuthService()
        use_case = LoginUseCase(
            auth_service=auth,
            matcher=FakeMatcher(result_index=0),
            tolerance=0.5,
            cooldown_seconds=8.0,
        )

        use_case.process_frame(["enc_frame"], ["enc_known"], ["1A-MATUTINO #1"], [1])
        use_case.process_frame(["enc_frame"], ["enc_known"], ["1A-MATUTINO #1"], [1])

        self.assertEqual([(1, True)], auth.logged)

    def test_load_known_students_uses_pkl_fallback(self):
        auth = FakeAuthService()
        auth.known_students = ([], [], [])
        pkl_repo = FakePklRepository(
            encodings=["enc_pkl"],
            labels=["est_9"],
            ids=[9],
        )

        use_case = LoginUseCase(
            auth_service=auth,
            matcher=FakeMatcher(result_index=0),
            pkl_repository=pkl_repo,
        )

        encodings, labels, ids = use_case.load_known_students()

        self.assertEqual(["enc_pkl"], encodings)
        self.assertEqual(["est_9"], labels)
        self.assertEqual([9], ids)


if __name__ == "__main__":
    unittest.main()
