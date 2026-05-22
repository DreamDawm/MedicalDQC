"""
Test configuration for the DataQC backend.

Uses SQLite with StaticPool so tests run without a real PostgreSQL instance.
The postgresql.UUID dialect type is patched to work transparently with SQLite.
"""
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Patch postgresql.UUID to work with SQLite
# ---------------------------------------------------------------------------

# 1. Teach the SQLite DDL compiler to render UUID columns as VARCHAR(36)
SQLiteTypeCompiler.visit_UUID = lambda self, type_, **kw: "VARCHAR(36)"

# 2. Convert uuid.UUID → str when binding parameters on SQLite
_orig_bind_processor = PG_UUID.bind_processor


def _patched_bind_processor(self, dialect):
    if dialect.name == "sqlite":

        def process(value):
            return str(value) if value is not None else None

        return process
    return _orig_bind_processor(self, dialect)


PG_UUID.bind_processor = _patched_bind_processor

# 3. Convert str → uuid.UUID when reading results from SQLite
_orig_result_processor = PG_UUID.result_processor


def _patched_result_processor(self, dialect, coltype):
    if dialect.name == "sqlite":

        def process(value):
            return uuid.UUID(value) if value else None

        return process
    return _orig_result_processor(self, dialect, coltype)


PG_UUID.result_processor = _patched_result_processor

# ---------------------------------------------------------------------------
# Import app modules AFTER the patch so models pick up the patched type
# ---------------------------------------------------------------------------
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(autouse=True)
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
