"""Minimal SQL-file migration runner (Goose-style: one .sql file per migration).

Each migration file is named `NNNN_description.sql` (e.g. `0001_initial_schema.sql`).
Applied migrations are tracked in the `schema_migrations` table, so on every
startup only the migrations newer than the highest applied version are executed,
in ascending order.
"""

import logging
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

MIGRATION_FILENAME_RE = re.compile(r"^(\d+)_.*\.sql$")


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path


def _discover_migrations(migrations_dir: Path) -> list[Migration]:
    migrations = []
    for file_path in migrations_dir.glob("*.sql"):
        match = MIGRATION_FILENAME_RE.match(file_path.name)
        if not match:
            logger.warning("Skipping migration file with unexpected name: %s", file_path.name)
            continue
        migrations.append(Migration(version=int(match.group(1)), name=file_path.name, path=file_path))
    return sorted(migrations, key=lambda m: m.version)


def _ensure_migrations_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.commit()


def _applied_versions(connection: sqlite3.Connection) -> set[int]:
    rows = connection.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def run_migrations(connection: sqlite3.Connection, migrations_dir: Path) -> list[int]:
    """Apply all pending migrations from `migrations_dir` to `connection`.

    Returns the list of newly applied migration versions, in the order applied.
    Raises the underlying exception (and stops at the failing migration) if any
    migration fails, leaving `schema_migrations` reflecting the last good state.
    """
    _ensure_migrations_table(connection)
    applied = _applied_versions(connection)
    pending = [m for m in _discover_migrations(migrations_dir) if m.version not in applied]

    applied_now: list[int] = []
    for migration in pending:
        sql = migration.path.read_text(encoding="utf-8")
        try:
            connection.executescript(sql)
            connection.execute(
                "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                (migration.version, migration.name),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            logger.exception("Migration %s (%s) failed", migration.version, migration.name)
            raise
        logger.info("Applied migration %s (%s)", migration.version, migration.name)
        applied_now.append(migration.version)

    if not applied_now:
        logger.info("Database schema is up to date (no pending migrations)")
    return applied_now
