import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "database", "face_recognition.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "script.sql")
