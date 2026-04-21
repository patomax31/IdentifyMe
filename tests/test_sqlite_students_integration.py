import os
import shutil
import tempfile
import unittest

import numpy as np

from database.sqlite import connection, migrations
from database.sqlite.students import create_student, load_student_biometrics, save_student_biometric


class SQLiteStudentsIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sqlite_students_test_")
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

    def test_create_and_load_student_biometrics(self):
        student_id = create_student(1, "A", "MATUTINO")
        encoding = np.array([0.1, 0.2, 0.3], dtype=float)
        save_student_biometric(student_id, encoding)

        encodings, labels, ids = load_student_biometrics()

        self.assertEqual([student_id], ids)
        self.assertEqual([f"1A-MATUTINO #{student_id}"], labels)
        self.assertEqual(1, len(encodings))
        self.assertTrue(np.allclose(encoding, encodings[0]))


if __name__ == "__main__":
    unittest.main()
