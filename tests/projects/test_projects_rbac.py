import pytest

from tests.auth.helpers import login


def create_org(client, auth_headers, name="RBAC Org", slug="rbac-org"):
    payload = {
        "name": name,
        "slug": slug,
        "description": "RBAC organzation",
    }
    response = client.post("/api/v1/organizations/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()


def get_token_for_other_user(client, other_user_payload):
    response = login(client, other_user_payload["email"],other_user_payload["password"])
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.mark.parametrize(
    "role,expected_status",
    [
        pytest.param("owner", 201, id="owner-can-create"),
        pytest.param("admin", 201, id="admin-can-create"),
        pytest.param("member", 403, id="member-cannot-create"),
        pytest.param("viewer", 403, id="viewer-cannot-create"),
    ],
)
def test_create_project_role_matrix(
    client,
    auth_headers,
    other_created_user,
    other_user_payload,
    membership_factory,
    other_user_headers,
    role,
    expected_status,
):
    org = create_org(client, auth_headers, name=f"{role} Org", slug=f"{role}-org")

    membership_factory(
    user_id=other_created_user["id"],
    organization_id=org["id"],
    role=role,
)

    payload= {
        "name": f"Project {role}",
        "description": "RBAC create test",
        "organization_id": org["id"],
    }

    response = client.post(
        "/api/v1/projects",
        json=payload,
        headers=other_user_headers,
    )

    assert response.status_code == expected_status, response.text


@pytest.mark.parametrize(
    "role",
    ["owner", "admin", "member", "viewer"],
    ids=["onwer-can-list", "admin-can-list", "member-can-list", "viewer-can-list"],
)
def test_list_projects_role_matrix(
    client,
    auth_headers,
    other_created_user,
    membership_factory,
    other_user_headers,
    role,
):
    org = create_org(client, auth_headers, name=f"list {role}", slug=f"list-{role}")

    create_project_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Visible Project",
            "description": "Should be listed",
            "organization_id": org["id"],
        },
        headers=auth_headers,
    )
    assert create_project_response.status_code == 201, create_project_response.text

    membership_factory(
        user_id=other_created_user["id"],
        organization_id=org["id"],
        role=role,
    )
     
    response = client.get(
        f"/api/v1/projects?organization_id={org['id']}",
        headers=other_user_headers,
     )
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Visible Project"


@pytest.mark.parametrize(
    "role,expected_status",
    [
        pytest.param("owner", 200, id="owner-can-update"),
        pytest.param("admin", 200, id="admin-can-update"),
        pytest.param("member", 403, id="member-cannot-update"),
        pytest.param("viewer", 403, id="viewer-cannot-update"),
    ],
)
def test_update_project_role_matrix(
    client,
    auth_headers,
    other_created_user,
    membership_factory,
    other_user_headers,
    role,
    expected_status,
):
    org = create_org(client, auth_headers, name=f"Update {role}", slug=f"update-{role}")

    create_project_response = client.post(
        "/api/v1/projects",
        json={
            "name": "Original Name",
            "description": "Original description",
            "organization_id": org["id"],
        },
        headers=auth_headers,
    )
    assert create_project_response.status_code == 201, create_project_response.text

    project = create_project_response.json()

    membership_factory(
        user_id=other_created_user["id"],
        organization_id=org["id"],
        role=role,
    )

    response = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": f"Updated by {role}"},
        headers=other_user_headers,
    )

    assert response.status_code == expected_status, response.text