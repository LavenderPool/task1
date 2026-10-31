import datetime
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.ddl import CreateColumn

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app

@compiles(CreateColumn, "sqlite")
def _compile_sqlite_column(element, compiler, **kwargs) -> str:
    """SQLite allows a function default only inside parentheses: DEFAULT (now())."""
    rendered = compiler.get_column_specification(element.element, **kwargs)
    return rendered.replace("DEFAULT now()", "DEFAULT (now())")


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def _sqlite_setup(dbapi_conn, _connection_record) -> None:
    dbapi_conn.create_function(
        "now",
        0,
        lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
