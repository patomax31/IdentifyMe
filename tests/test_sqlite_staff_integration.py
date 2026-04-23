import os
import shutil
import sqlite3
import tempfile
import unittest

import numpy as np

from database.sqlite import connection, migrations
from database.sqlite.staff import (
    count_active_staff,
    create_staff,
    get_staff_identity,
    load_staff_biometrics,
    save_staff_biometric,
    verify_password,
)


class SQLiteStaffIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sqlite_staff_test_")
        self.db_path = os.path.join(self.temp_dir, "face_recognition_test.db")
        self.schema_path = os.path.join(self.temp_dir, "script.sql")

        project_schema = os.path.join(os.getcwd(), "database", "script.sql")
        shutil.copyfile(project_schema, self.schema_path)

        self._orig_connection_db_path = connection.DB_PATH
        self._orig_migrations_db_path = migrations.DB_PATH
        self._orig_migrations_schema_path = migrations.SCHEMA_PATH

        connection.DB_PATH = self.db_path
        migrations.DB_PATH = self.db_path
        migrations.SCHEMA_PATH = self.schema_path

    def tearDown(self):
        connection.DB_PATH = self._orig_connection_db_path
        migrations.DB_PATH = self._orig_migrations_db_path
        migrations.SCHEMA_PATH = self._orig_migrations_schema_path
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_staff_updates_active_count_and_hashes_password(self):
        self.assertEqual(0, count_active_staff())

        staff_id = create_staff(
            num_empleado="adm001",
            nombre_completo="Maria Admin",
            rol="superadmin",
            correo="maria@school.edu",
            password_plain="Segura123",
        )

        self.assertGreater(staff_id, 0)
        self.assertEqual(1, count_active_staff())

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT num_empleado, rol, correo, password_hash FROM personal_administrativo WHERE id_personal = ?",
                (staff_id,),
            ).fetchone()

        self.assertEqual("ADM001", row[0])
        self.assertEqual("SUPERADMIN", row[1])
        self.assertEqual("maria@school.edu", row[2])
        self.assertTrue(row[3].startswith("pbkdf2_sha256$"))
        self.assertTrue(verify_password("Segura123", row[3]))

    def test_save_and_load_staff_biometrics(self):
        staff_id = create_staff(
            num_empleado="adm002",
            nombre_completo="Pedro Registro",
            rol="ADMIN_REGISTRO",
            correo="pedro@school.edu",
            password_plain="ClaveFuerte99",
        )
        encoding = np.array([0.11, 0.22, 0.33], dtype=float)

        save_staff_biometric(staff_id, encoding)
        encodings, labels, ids, roles = load_staff_biometrics()

        self.assertEqual([staff_id], ids)
        self.assertEqual([f"Pedro Registro (ADMIN_REGISTRO) #{staff_id}"], labels)
        self.assertEqual(["ADMIN_REGISTRO"], roles)
        self.assertEqual(1, len(encodings))
        self.assertTrue(np.allclose(encoding, encodings[0]))

    def test_get_staff_identity_returns_active_staff(self):
        staff_id = create_staff(
            num_empleado="adm003",
            nombre_completo="Laura Operadora",
            rol="OPERADOR",
            correo="laura@school.edu",
            password_plain="ClaveFuerte99",
        )

        identity = get_staff_identity(staff_id)

        self.assertIsNotNone(identity)
        self.assertEqual(str(staff_id), identity["id_personal"])
        self.assertEqual("ADM003", identity["num_empleado"])
        self.assertEqual("Laura Operadora", identity["nombre_completo"])
        self.assertEqual("OPERADOR", identity["rol"])
        self.assertEqual("laura@school.edu", identity["correo"])


if __name__ == "__main__":
    unittest.main()
