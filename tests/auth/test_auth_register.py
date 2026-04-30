import pytest

from tests.auth.helpers import register
from tests.factories import unique_email, make_user_payload


pytestmark = [pytest.mark.auth]


@pytest.mark.smoke
def test_register_success(client):
    payload = make_user_payload()

    response = register(client, payload)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["name"] == payload["name"]
    assert "password" not in data


def test_register_duplicate_email(client):
    payload = make_user_payload()

    first = register(client, payload)
    second = register(client, payload)

    assert first.status_code == 201, first.text
    assert second.status_code in (400, 409), second.text


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {"name": "Bad Email", "email": "invalid-email", "password": "12345678"},
            id="invalid-email",
        ),
        pytest.param(
            {"email": unique_email(), "password": "12345678"},
            id="missing-name",
        ),
        pytest.param(
            {"name": "No Password", "email": unique_email()},
            id="missing-password",
        ),
    ],
)
def test_register_validation_errors(client, payload):
    response = register(client, payload)

    assert response.status_code == 422, response.text