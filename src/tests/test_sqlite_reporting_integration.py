import os
import shutil
import tempfile
import unittest

import numpy as np

from database.sqlite import connection, migrations
from database.sqlite.access import log_access
from database.sqlite.reporting import list_access_logs, list_failed_attempts, list_students
from database.sqlite.students import create_student, save_student_biometric


class SQLiteReportingIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sqlite_reporting_test_")
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

    def test_list_students_and_filters(self):
        student_id_1 = create_student("Ana Lopez", 1, "A", "MATUTINO")
        student_id_2 = create_student("Bruno Diaz", 2, "B", "VESPERTINO")

        save_student_biometric(student_id_1, np.array([0.1, 0.2, 0.3], dtype=float))
        save_student_biometric(student_id_2, np.array([0.4, 0.5, 0.6], dtype=float))

        all_rows = list_students(limit=10)
        self.assertEqual(2, len(all_rows))

        filtered = list_students(grado="2", grupo="B", turno="VESPERTINO", nombre_contains="Bruno", limit=10)
        self.assertEqual(1, len(filtered))
        self.assertEqual("Bruno Diaz", filtered[0]["nombre"])

    def test_list_logs_and_failed_attempts(self):
        student_id = create_student("Carla Ruiz", 3, "C", "MATUTINO")

        log_access(student_id, True, tipo_evento="Entrada", tipo_usuario="ESTUDIANTE")
        log_access(student_id, False, tipo_evento="Salida", tipo_usuario="ESTUDIANTE")

        logs = list_access_logs(tipo_usuario="ESTUDIANTE", limit=10)
        self.assertEqual(2, len(logs))

        failed = list_failed_attempts(tipo_usuario="ESTUDIANTE", limit=10)
        self.assertEqual(1, len(failed))
        self.assertEqual(student_id, failed[0]["id_usuario_ref"])


if __name__ == "__main__":
    unittest.main()
