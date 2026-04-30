import pytest

from tests.auth.helpers import login


pytestmark = [pytest.mark.auth]


@pytest.mark.smoke
def test_login_success(client, user_payload, created_user):
    response = login(client, user_payload["email"], user_payload["password"])

    assert response.status_code == 200, response.text

    data = response.json()
    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"].lower() == "bearer"


@pytest.mark.parametrize(
    "email,password",
    [
        pytest.param("wrong@example.com", "wrongpassword", id="unknown-user"),
        pytest.param("wrong@example.com", "12345678", id="unknown-user-valid-password"),
    ],
)
def test_login_invalid_credentials(client, email, password):
    response = login(client, email, password)

    assert response.status_code in (400, 401), response.text


def test_login_wrong_password_for_existing_user(client, created_user):
    response = login(client, created_user["email"], "wrongpassword")

    assert response.status_code in (400, 401), response.text


def test_login_missing_password(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com"},
    )

    assert response.status_code == 422, response.text