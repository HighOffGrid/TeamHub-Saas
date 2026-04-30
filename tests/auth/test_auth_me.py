import pytest

from tests.auth.helpers import me


pytestmark = [pytest.mark.auth]


def test_get_current_user_success(client, created_user, access_token):
    response = me(client, access_token)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == created_user["email"]


def test_get_current_user_without_token(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401, response.text


def test_get_current_user_with_invalid_token(client):
    response = me(client, "invalid.token.here")

    assert response.status_code == 401, response.text


def test_get_current_user_with_malformed_header(client):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Token abc123"},
    )

    assert response.status_code == 401, response.text