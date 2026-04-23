import unittest
from types import SimpleNamespace
from unittest.mock import patch

import registrar


class FakeRegistrationUseCase:
    def __init__(self, registration_service=None, pkl_repository=None):
        self.initialized = False

    def initialize(self):
        self.initialized = True


class RegistrarAdminFlowTests(unittest.TestCase):
    def test_autenticar_personal_returns_bootstrap_when_no_active_staff(self):
        settings = SimpleNamespace(tolerance=0.5)

        with patch("registrar.count_active_staff", return_value=0):
            actor = registrar._autenticar_personal_para_registro(settings)

        self.assertIsNotNone(actor)
        self.assertTrue(actor["bootstrap"])
        self.assertEqual("SUPERADMIN", actor["rol"])

    def test_autenticar_personal_returns_none_when_no_staff_biometrics(self):
        settings = SimpleNamespace(tolerance=0.5)

        with patch("registrar.count_active_staff", return_value=1), patch(
            "registrar.load_staff_biometrics", return_value=([], [], [], [])
        ):
            actor = registrar._autenticar_personal_para_registro(settings)

        self.assertIsNone(actor)

    def test_autenticar_personal_success_logs_access(self):
        settings = SimpleNamespace(tolerance=0.5)

        fake_matcher = SimpleNamespace(find_first_match=lambda known, candidate, tolerance: 0)

        with patch("registrar.count_active_staff", return_value=1), patch(
            "registrar.load_staff_biometrics",
            return_value=(["enc_admin"], ["Ana Admin (SUPERADMIN) #7"], [7], ["SUPERADMIN"]),
        ), patch("registrar._capturar_encoding_desde_camara", return_value="enc_frame"), patch(
            "registrar.FaceMatcherAdapter", return_value=fake_matcher
        ), patch("registrar.log_access") as log_access_mock:
            actor = registrar._autenticar_personal_para_registro(settings)

        self.assertIsNotNone(actor)
        self.assertEqual(7, actor["id_personal"])
        self.assertEqual("SUPERADMIN", actor["rol"])
        self.assertFalse(actor["bootstrap"])
        log_access_mock.assert_called_once_with(7, True, tipo_usuario="PERSONAL")

    def test_registrar_usuario_bootstrap_calls_register_staff(self):
        state_messages = []

        with patch("registrar.get_recognition_settings", return_value=SimpleNamespace()), patch(
            "registrar._autenticar_personal_para_registro",
            return_value={"bootstrap": True, "rol": "SUPERADMIN", "nombre": "BOOTSTRAP", "id_personal": 0},
        ), patch("registrar._registrar_personal") as registrar_personal_mock:
            registrar.registrar_usuario(state_callback=state_messages.append)

        registrar_personal_mock.assert_called_once()
        self.assertIn("Registro biometrico finalizado.", state_messages)

    def test_registrar_usuario_denies_operador_registering_staff(self):
        state_messages = []

        with patch("registrar.get_recognition_settings", return_value=SimpleNamespace()), patch(
            "registrar._autenticar_personal_para_registro",
            return_value={"bootstrap": False, "rol": "OPERADOR", "nombre": "Operador 1", "id_personal": 9},
        ), patch("registrar.RegistrationUseCase", FakeRegistrationUseCase), patch(
            "builtins.input", side_effect=["2", "Q"]
        ), patch("registrar._registrar_personal") as registrar_personal_mock:
            registrar.registrar_usuario(state_callback=state_messages.append)

        registrar_personal_mock.assert_not_called()
        self.assertIn("No tienes permisos para registrar personal administrativo.", state_messages)


if __name__ == "__main__":
    unittest.main()
