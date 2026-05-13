import unittest

from database.sqlite.staff import hash_password, verify_password


class StaffSecurityTests(unittest.TestCase):
    def test_hash_password_and_verify_success(self):
        password_hash = hash_password("Segura123")

        self.assertTrue(password_hash.startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password("Segura123", password_hash))

    def test_verify_password_fails_with_wrong_password(self):
        password_hash = hash_password("Segura123")

        self.assertFalse(verify_password("Incorrecta456", password_hash))

    def test_hash_password_rejects_short_password(self):
        with self.assertRaises(ValueError):
            hash_password("1234567")

    def test_verify_password_rejects_invalid_hash_format(self):
        self.assertFalse(verify_password("Segura123", "hash_invalido"))


if __name__ == "__main__":
    unittest.main()
