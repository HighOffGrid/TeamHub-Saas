import uuid


def unique_email():
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


def register_user(client, name="User", email=None, password="12345678"):
    email = email or unique_email()
    payload = {
        "name": name,
        "email": email,
        "password": password,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code in (200, 201), response.text
    return response.json(), payload


def login_user(client, email, password):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_org(client, auth_headers, name="Membership Org", slug=None):
    slug = slug or f"membership-org-{uuid.uuid4().hex[:8]}"
    payload = {
        "name": name,
        "slug": slug,
        "description": "Membership tests org",
    }
    response = client.post(
        "/api/v1/organizations/",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def add_membership(
    client,
    auth_headers,
    organization_id,
    user_email,
    role="member",
):
    response = client.post(
        f"/api/v1/organizations/{organization_id}/memberships",
        json={
            "user_email": user_email,
            "role": role,
        },
        headers=auth_headers,
    )
    return response


def list_memberships(client, auth_headers, organization_id):
    return client.get(
        f"/api/v1/organizations/{organization_id}/memberships",
        headers=auth_headers,
    )


def update_membership(client, auth_headers, membership_id, role):
    return client.patch(
        f"/api/v1/memberships/{membership_id}",
        json={"role": role},
        headers=auth_headers,
    )


def delete_membership(client, auth_headers, membership_id):
    return