"""Backward-compatible facade for SQLite operations.

This module keeps the original public API while delegating implementation
into database/sqlite/* specialized modules.
"""

from database.sqlite.paths import BASE_DIR, DB_PATH, SCHEMA_PATH
from database.sqlite.migrations import initialize_database
from database.sqlite.students import (
    create_student,
    load_student_biometrics,
    migrate_pickle_biometrics,
    save_student_biometric,
)
from database.sqlite.access import log_access

__all__ = [
    "BASE_DIR",
    "DB_PATH",
    "SCHEMA_PATH",
    "initialize_database",
    "create_student",
    "save_student_biometric",
    "load_student_biometrics",
    "log_access",
    "migrate_pickle_biometrics",
]
