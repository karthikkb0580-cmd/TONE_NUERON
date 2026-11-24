import pytest

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import Base, get_db

from backend.app.models.user import User, UserPreferences
from backend.app.models.email_otp import EmailOTP
from backend.app.models.refresh_token import RefreshToken
from backend.app.models.used_refresh_token import UsedRefreshToken
from backend.app.models.security_event import SecurityEvent

from backend.app.core.config import settings
from backend.app.services import otp_service


TEST_DATABASE_NAME = "tone_neuron_test"

TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=TEST_DATABASE_NAME,
)

assert TEST_DATABASE_URL.database == TEST_DATABASE_NAME


@pytest.fixture(scope="session")
def test_engine():

    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
    )

    # Reset only the dedicated test database.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine):

    connection = test_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def sent_otps():
    return []


@pytest.fixture
def client(db_session, monkeypatch, sent_otps):

    def fake_send_verification_email(
        recipient_email: str,
        otp: str,
    ):
        sent_otps.append({
            "email": recipient_email,
            "otp": otp,
        })

    monkeypatch.setattr(
        otp_service,
        "send_verification_email",
        fake_send_verification_email,
    )

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)