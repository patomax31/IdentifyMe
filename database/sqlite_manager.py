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
from database.sqlite.staff import (
    count_active_staff,
    create_staff,
    load_staff_biometrics,
    save_staff_biometric,
)
from database.sqlite.access import log_access
from database.sqlite.reporting import list_access_logs, list_failed_attempts, list_students

__all__ = [
    "BASE_DIR",
    "DB_PATH",
    "SCHEMA_PATH",
    "initialize_database",
    "create_student",
    "save_student_biometric",
    "load_student_biometrics",
    "count_active_staff",
    "create_staff",
    "save_staff_biometric",
    "load_staff_biometrics",
    "log_access",
    "migrate_pickle_biometrics",
    "list_students",
    "list_access_logs",
    "list_failed_attempts",
]
