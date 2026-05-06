import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import login


class FakeCap:
    def __init__(self, frame):
        self._frame = frame
        self.released = False
        self._reads = 0

    def read(self):
        self._reads += 1
        if self._reads == 1:
            return True, self._frame
        return False, None

    def release(self):
        self.released = True


class FakeLoginUseCase:
    def __init__(self, known_students, process_result):
        self._known_students = known_students
        self._process_result = process_result
        self.initialized = False
        self.process_calls = []

    def initialize(self):
        self.initialized = True

    def load_known_students(self):
        return self._known_students

    def process_frame(self, encodings, known_encodings, known_labels, known_ids):
        self.process_calls.append((encodings, known_encodings, known_labels, known_ids))
        return self._process_result


class LoginAdminPriorityTests(unittest.TestCase):
    def _patch_cv2_drawing(self):
        return patch.multiple(
            "login.cv2",
            ellipse=Mock(),
            rectangle=Mock(),
            putText=Mock(),
            imshow=Mock(),
            destroyAllWindows=Mock(),
            waitKey=Mock(return_value=ord("q")),
        )

    def test_login_prioritizes_staff_before_students(self):
        frame = SimpleNamespace(shape=(480, 640, 3))
        fake_cap = FakeCap(frame)
        recognition_settings = SimpleNamespace(tolerance=0.5, access_cooldown_seconds=0.0, scale=0.25)

        use_case = FakeLoginUseCase(
            known_students=(["enc_student"], ["Student A #1"], [1]),
            process_result=SimpleNamespace(message="ACCESO CONCEDIDO: STUDENT", color=(0, 255, 0)),
        )

        matcher = Mock()
        matcher.find_first_match.return_value = 0

        with patch("login.get_recognition_settings", return_value=recognition_settings), patch(
            "login.LoginUseCase", return_value=use_case
        ), patch("login.FaceMatcherAdapter", return_value=matcher), patch(
            "login.load_staff_biometrics",
            return_value=(["enc_staff"], ["Admin Principal (SUPERADMIN) #7"], [7], ["SUPERADMIN"]),
        ), patch("login.detect_face_encodings_from_frame", return_value=([], ["enc_frame"])), patch(
            "login.open_camera", return_value=fake_cap
        ), patch("login.log_access") as log_access_mock, self._patch_cv2_drawing():
            login.login()

        self.assertTrue(use_case.initialized)
        self.assertEqual([], use_case.process_calls)
        log_access_mock.assert_called_once_with(7, True, tipo_usuario="PERSONAL")
        self.assertTrue(fake_cap.released)

    def test_login_falls_back_to_students_when_staff_does_not_match(self):
        frame = SimpleNamespace(shape=(480, 640, 3))
        fake_cap = FakeCap(frame)
        recognition_settings = SimpleNamespace(tolerance=0.5, access_cooldown_seconds=0.0, scale=0.25)

        use_case = FakeLoginUseCase(
            known_students=(["enc_student"], ["Student A #1"], [1]),
            process_result=SimpleNamespace(message="ACCESO CONCEDIDO: STUDENT", color=(0, 255, 0)),
        )

        matcher = Mock()
        matcher.find_first_match.return_value = -1

        with patch("login.get_recognition_settings", return_value=recognition_settings), patch(
            "login.LoginUseCase", return_value=use_case
        ), patch("login.FaceMatcherAdapter", return_value=matcher), patch(
            "login.load_staff_biometrics",
            return_value=(["enc_staff"], ["Admin Principal (SUPERADMIN) #7"], [7], ["SUPERADMIN"]),
        ), patch("login.detect_face_encodings_from_frame", return_value=([], ["enc_frame"])), patch(
            "login.open_camera", return_value=fake_cap
        ), patch("login.log_access") as log_access_mock, self._patch_cv2_drawing():
            login.login()

        self.assertEqual(1, len(use_case.process_calls))
        encodings, known_encodings, known_labels, known_ids = use_case.process_calls[0]
        self.assertEqual(["enc_frame"], encodings)
        self.assertEqual(["enc_student"], known_encodings)
        self.assertEqual(["Student A #1"], known_labels)
        self.assertEqual([1], known_ids)
        log_access_mock.assert_not_called()
        self.assertTrue(fake_cap.released)

    def test_login_returns_early_when_no_biometrics_exist(self):
        recognition_settings = SimpleNamespace(tolerance=0.5, access_cooldown_seconds=0.0, scale=0.25)
        use_case = FakeLoginUseCase(
            known_students=([], [], []),
            process_result=SimpleNamespace(message="", color=(255, 255, 255)),
        )
        state_messages = []

        with patch("login.get_recognition_settings", return_value=recognition_settings), patch(
            "login.LoginUseCase", return_value=use_case
        ), patch("login.FaceMatcherAdapter", return_value=Mock()), patch(
            "login.load_staff_biometrics", return_value=([], [], [], [])
        ), patch("login.open_camera") as open_camera_mock:
            login.login(state_callback=state_messages.append)

        open_camera_mock.assert_not_called()
        self.assertIn(
            "No hay biometria registrada. Ejecuta primero bootstrap_admin.py o registrar.py",
            state_messages,
        )


if __name__ == "__main__":
    unittest.main()
