import os

os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["RATE_LIMIT_FAIL_OPEN"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import uuid

from app.models.membership import Membership
from app.core.database import get_session
from app.main import app
from tests.auth.helpers import login, register
from tests.factories import make_user_payload


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user_payload():
    return make_user_payload()


@pytest.fixture
def created_user(client, user_payload):
    response = register(client, user_payload)
    assert response.status_code in (200, 201), response.text
    return response.json()


@pytest.fixture
def access_token(client, user_payload, created_user):
    response = login(client, user_payload["email"], user_payload["password"])
    assert response.status_code == 200, response.text
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def other_user_payload():
    return make_user_payload(
        name="Other User",
        email=f"other_{uuid.uuid4().hex[:8]}@example.com",
        password="12345678",
    )


@pytest.fixture
def other_created_user(client, other_user_payload):
    response = register(client, other_user_payload)
    assert response.status_code in (200, 201), response.text
    return response.json()


@pytest.fixture
def other_access_token(client, other_user_payload, other_created_user):
    response = login(
        client,
        other_user_payload["email"],
        other_user_payload["password"],
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def other_user_headers(other_access_token):
    return {"Authorization": f"Bearer {other_access_token}"}


@pytest.fixture
def membership_factory(session):
    def create_membership(*, user_id: str, organization_id: str, role: str):
        membership = Membership(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
        )
        session.add(membership)
        session.commit()
        session.refresh(membership)
        return membership

    return create_membership
