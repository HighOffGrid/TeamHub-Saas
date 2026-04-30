from sqlmodel import select

from app.models.membership import Membership
from app.models.organization import Organization


def test_create_organization_success(client, auth_headers, session):
    payload = {
        "name": "Test Organization",
        "slug": "test-organization",
        "description": "A test organization",
    }

    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["slug"] == payload["slug"]
    assert data["description"] == payload["description"]

    org = session.exec(
        select(Organization).where(Organization.id == data["id"])
    ).first()
    assert org is not None

    membership = session.exec(
        select(Membership).where(Membership.organization_id == org.id)
    ).first()
    assert membership is not None
    assert membership.role == "admin"


def test_create_organization_unauthorized(client):
    payload = {
        "name": "Unauthorized Org",
        "slug": "unauthorized-org",
        "description": "Should fail",
    }

    response = client.post("/api/v1/organizations/", json=payload)

    assert response.status_code == 401, response.text


def test_list_my_organizations_returns_empty(client, auth_headers):
    response = client.get("/api/v1/organizations/", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_list_my_organizations_returns_only_user_orgs(client, auth_headers):
    payload_1 = {
        "name": "Org 1",
        "slug": "org-1",
        "description": "First org",
    }

    payload_2 = {
        "name": "Org 2",
        "slug": "org-2",
        "description": "Second org",
    }

    create_1 = client.post(
        "/api/v1/organizations/",
        json=payload_1,
        headers=auth_headers,
    )

    create_2 = client.post(
        "/api/v1/organizations/",
        json=payload_2,
        headers=auth_headers,
    )

    assert create_1.status_code == 201, create_1.text
    assert create_2.status_code == 201, create_2.text

    response = client.get("/api/v1/organizations/", headers=auth_headers)

    assert response.status_code == 200, response.text

    data = response.json()
    slugs = [org["slug"] for org in data]

    assert "org-1" in slugs
    assert "org-2" in slugs
    assert len(data) == 2


def test_list_my_organizations_unauthorized(client):
    response = client.get("/api/v1/organizations/")

    assert response.status_code == 401, response.text