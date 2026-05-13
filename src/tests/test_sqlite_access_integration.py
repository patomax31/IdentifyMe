import os
import shutil
import sqlite3
import tempfile
import unittest

from database.sqlite import connection, migrations
from database.sqlite.access import log_access


class SQLiteAccessIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sqlite_access_test_")
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

    def test_log_access_persists_row(self):
        log_access(99, True, tipo_evento="Entrada", tipo_usuario="ESTUDIANTE")

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT tipo_usuario, id_usuario_ref, tipo_evento, acceso_concedido FROM logs_acceso LIMIT 1"
            ).fetchone()

        self.assertEqual(("ESTUDIANTE", 99, "Entrada", 1), row)

    def test_log_access_rejects_invalid_tipo_usuario(self):
        with self.assertRaises(ValueError):
            log_access(1, True, tipo_usuario="INVITADO")


if __name__ == "__main__":
    unittest.main()
