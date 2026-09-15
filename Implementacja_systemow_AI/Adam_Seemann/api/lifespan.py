"""Application lifespan: runs DB migrations and opens the shared connection."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.database import create_database_session
from data.db import initialize_database

logger = logging.getLogger("agpw.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    app.state.db_session = create_database_session()
    logger.info("Database ready: migrations applied and shared connection opened")
    try:
        yield
    finally:
        app.state.db_session.connection.close()
