import os

import pytest
from dotenv import dotenv_values
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# Load the dedicated test database URL.
env_values = dotenv_values(Path(__file__).resolve().parents[2] / ".env")
TEST_DATABASE_URL = env_values.get("TEST_DATABASE_URL")


if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not configured")


# Safety check: never allow tests to use the development database.
if "predictive_maintenance_test" not in TEST_DATABASE_URL:
    raise RuntimeError("Tests must use predictive_maintenance_test")


# Create a separate SQLAlchemy engine for tests.
test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def db_engine():
    with test_engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()

        if database_name != "predictive_maintenance_test":
            raise RuntimeError(
                f"Unsafe test database: {database_name}"
            )

    yield test_engine

    test_engine.dispose()


@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()