from sqlmodel import select

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.project import Project


def create_org(client, auth_headers,  name="Test Org", slug="test-org", description="A test organization"):
    payload = {
        "name": name,
        "slug": slug,
        "description": description,
    }

    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text
    return response.json()


def test_create_project_success(client, auth_headers):
    org = create_org(client, auth_headers)

    payload = {
        "name": "Test Project",
        "description": "A test project",
        "organization_id": org["id"],
    }

    response = client.post(
        "/api/v1/projects/",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["organization_id"] == payload["organization_id"]


def test_create_project_organization_not_found(client, auth_headers):
    payload = {
        "name": "Test Project",
        "description": "A test project",
        "organization_id": "non-existent-org-id",
    }

    response = client.post(
        "/api/v1/projects/",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Organization not found"


def test_create_project_unauthorized(client):
    payload = {
        "name": "Unauthorized Project",
        "description": "Should fail",
        "organization_id": "some-org-id",
    }

    response = client.post("/api/v1/projects/", json=payload)

    assert response.status_code == 401, response.text


def test_list_projects_success(client, auth_headers):
    org = create_org(client, auth_headers, name="List Projects Org", slug="list-projects-org")

    # Create multiple projects
    for i in range(3):
        payload = {
            "name": f"Project {i+1}",
            "description": f"Description for project {i+1}",
            "organization_id": org["id"],
        }
        response = client.post(
            "/api/v1/projects/",
            json=payload,
            headers=auth_headers,
        )
        assert response.status_code == 201, response.text

    # List projects
    response = client.get(
        f"/api/v1/projects/?organization_id={org['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 3
    assert all(project["organization_id"] == org["id"] for project in data)


def test_list_projects_unauthorized(client):
    response = client.get("/api/v1/projects/?organization_id=some-org-id")

    assert response.status_code == 401, response.text


def test_update_project_success(client, auth_headers):
    org = create_org(client, auth_headers, name="Update Project Org", slug="update-project-org")

    create_response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Original Project Name",
            "description": "Original description",
            "organization_id": org["id"],
        },
        headers=auth_headers,
        
    )
    assert create_response.status_code == 201, create_response.text

    project = create_response.json()

    response = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={
            "name": "Updated Project Name",
            "description": "Updated description",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Updated Project Name"


def test_update_project_not_found(client, auth_headers):
    response = client.patch(
        "/api/v1/projects/non-existent-project-id",
        json={"name": "New Name"},
        headers=auth_headers,
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Project not found"


def test_create_project_forbidden_for_non_member(
    client, auth_headers, other_user_headers
):
    org = create_org(
        client,
        auth_headers,
        name="Private Org",
        slug="private-org",
    )

    payload = {
        "name": "Forbidden Project",
        "description": "Should not be created",
        "organization_id": org["id"],
    }

    response = client.post(
        "/api/v1/projects",
        json=payload,
        headers=other_user_headers,
    )

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == (
        "You are not a member of this organization"
    )

    owner_response = client.get(
        "/api/v1/projects",
        params={"organization_id": org["id"]},
        headers=auth_headers,
    )
    assert owner_response.status_code == 200, owner_response.text
    assert owner_response.json() == []


def test_list_projects_forbidden_for_non_member(
    client, auth_headers, other_user_headers
):
    org = create_org(
        client,
        auth_headers,
        name="Private List Org",
        slug="private-list-org",
    )

    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Private Project",
            "description": "Must not be visible to non-members",
            "organization_id": org["id"],
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201, create_response.text

    response = client.get(
        "/api/v1/projects",
        params={"organization_id": org["id"]},
        headers=other_user_headers,
    )

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == (
        "You are not a member of this organization"
    )


def test_update_project_forbidden_for_non_member(
    client, auth_headers, other_user_headers
):
    org = create_org(
        client,
        auth_headers,
        name="Private Update Org",
        slug="private-update-org",
    )

    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Protected Project",
            "description": "Original description",
            "organization_id": org["id"],
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201, create_response.text
    original_project = create_response.json()

    response = client.patch(
        f"/api/v1/projects/{original_project['id']}",
        json={
            "name": "Unauthorized change",
            "description": "Must not be saved",
        },
        headers=other_user_headers,
    )

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == (
        "You are not a member of this organization"
    )

    owner_response = client.get(
        "/api/v1/projects",
        params={"organization_id": org["id"]},
        headers=auth_headers,
    )
    assert owner_response.status_code == 200, owner_response.text

    projects = owner_response.json()
    assert len(projects) == 1
    assert projects[0] == original_project


def test_update_project_updates_updated_at(client, auth_headers):
    org = create_org(
        client,
        auth_headers,
        name="Updated At Org",
        slug="updated-at-org",
    )

    create_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Timestamp Project",
            "description": "Original description",
            "organization_id": org["id"],
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201, create_response.text

    original_project = create_response.json()
    original_updated_at = original_project["updated_at"]

    update_response = client.patch(
        f"/api/v1/projects/{original_project['id']}",
        json={"name": "Updated Timestamp Project"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200, update_response.text

    updated_project = update_response.json()

    assert updated_project["name"] == "Updated Timestamp Project"
    assert updated_project["updated_at"] > original_updated_at