"""Shared, lifespan-managed SQLite connection for the API.

A single SQLite connection is opened once when the app starts (see `lifespan` in
`api/server.py`) and reused for every request, instead of opening/closing a new
connection per request. Because FastAPI runs sync endpoints in a threadpool, the
connection is opened with `check_same_thread=False` and all access is serialized
through a `threading.Lock` to keep it safe across threads.
"""

import threading
from collections.abc import Sequence
from dataclasses import dataclass
from sqlite3 import Connection, Row

from fastapi import Request

from data.db import connect_db


@dataclass
class DatabaseSession:
    """A SQLite connection paired with the lock that must guard every use of it."""

    connection: Connection
    lock: threading.Lock

    def execute(self, sql: str, parameters: Sequence = ()) -> list[Row]:
        with self.lock:
            return self.connection.execute(sql, parameters).fetchall()

    def execute_one(self, sql: str, parameters: Sequence = ()) -> Row | None:
        with self.lock:
            return self.connection.execute(sql, parameters).fetchone()


def create_database_session(path=None) -> DatabaseSession:
    connection = connect_db(path, check_same_thread=False)
    return DatabaseSession(connection=connection, lock=threading.Lock())


def get_db_session(request: Request) -> DatabaseSession:
    """FastAPI dependency exposing the app-wide shared `DatabaseSession`."""
    return request.app.state.db_session
