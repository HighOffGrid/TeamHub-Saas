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
    response = client.post("/api/v1/organizations/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()


def add_membership(client, auth_headers, organization_id, user_email, role="member"):
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
    return client.delete(
        f"/api/v1/memberships/{membership_id}",
        headers=auth_headers,
    )


def test_list_memberships_success(client, auth_headers):
    org = create_org(client, auth_headers)

    extra_user, extra_payload = register_user(client, name="Extra Member")
    response = add_membership(client, auth_headers, org["id"], extra_payload["email"], "member")
    assert response.status_code == 201, response.text

    response = list_memberships(client, auth_headers, org["id"])

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 2


def test_list_memberships_forbidden_for_non_member(client, auth_headers):
    org = create_org(client, auth_headers)

    outsider, outsider_payload = register_user(client, name="Outsider")
    outsider_headers = login_user(client, outsider_payload["email"], outsider_payload["password"])

    response = list_memberships(client, outsider_headers, org["id"])

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == "You do not belong to this organization"


def test_add_membership_success_as_org_manager(client, auth_headers):
    org = create_org(client, auth_headers)

    user, payload = register_user(client, name="New Member")
    response = add_membership(client, auth_headers, org["id"], payload["email"], "member")

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["organization_id"] == org["id"]
    assert data["role"] == "member"
    assert data["user_id"] == user["id"]


def test_add_membership_duplicate_returns_409(client, auth_headers):
    org = create_org(client, auth_headers)

    _, payload = register_user(client, name="Duplicated")
    first = add_membership(client, auth_headers, org["id"], payload["email"], "member")
    second = add_membership(client, auth_headers, org["id"], payload["email"], "member")

    assert first.status_code == 201, first.text
    assert second.status_code == 409, second.text
    assert second.json()["detail"] == "User is already a member of this organization"


def test_add_membership_user_not_found(client, auth_headers):
    org = create_org(client, auth_headers)

    response = add_membership(client, auth_headers, org["id"], unique_email(), "member")

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "User not found"


def test_add_membership_unauthorized(client):
    response = client.post(
        f"/api/v1/organizations/{uuid.uuid4()}/memberships",
        json={"user_email": unique_email(), "role": "member"},
    )

    assert response.status_code == 401, response.text


def test_admin_cannot_create_admin_or_owner(client, auth_headers):
    org = create_org(client, auth_headers)

    target_user, target_payload = register_user(client, name="Target User")

    create_admin = add_membership(client, auth_headers, org["id"], target_payload["email"], "admin")
    create_owner = add_membership(client, auth_headers, org["id"], target_payload["email"], "owner")

    assert create_admin.status_code == 403, create_admin.text
    assert create_owner.status_code == 403, create_owner.text
    assert create_admin.json()["detail"] == "Admins cannot create admins or owners"


def test_update_membership_role_success_as_org_admin(client, auth_headers):
    org = create_org(client, auth_headers)

    _, payload = register_user(client, name="Promoted User")
    created = add_membership(client, auth_headers, org["id"], payload["email"], "member")
    assert created.status_code == 201, created.text

    membership = created.json()
    response = update_membership(client, auth_headers, membership["id"], "viewer")

    assert response.status_code == 200, response.text
    assert response.json()["role"] == "viewer"


def test_admin_cannot_promote_to_admin_or_owner(client, auth_headers):
    org = create_org(client, auth_headers)

    member_user, member_payload = register_user(client, name="Regular User")
    member_created = add_membership(client, auth_headers, org["id"], member_payload["email"], "member")
    assert member_created.status_code == 201, member_created.text

    membership = member_created.json()
    response = update_membership(client, auth_headers, membership["id"], "admin")

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == "Admins cannot promote users to admin or owner"


def test_delete_membership_success(client, auth_headers):
    org = create_org(client, auth_headers)

    _, payload = register_user(client, name="Delete User")
    created = add_membership(client, auth_headers, org["id"], payload["email"], "member")
    assert created.status_code == 201, created.text

    membership = created.json()
    response = delete_membership(client, auth_headers, membership["id"])

    assert response.status_code == 204, response.text


def test_admin_cannot_create_another_admin_for_future_removal_scenario(client, auth_headers):
    org = create_org(client, auth_headers)

    target_user, target_payload = register_user(client, name="Target User")
    response = add_membership(client, auth_headers, org["id"], target_payload["email"], "admin")

    assert response.status_code == 403, response.text
    assert response.json()["detail"] == "Admins cannot create admins or owners"


def test_creator_membership_is_not_owner_in_current_rule_set(client, auth_headers):
    org = create_org(client, auth_headers)

    response = list_memberships(client, auth_headers, org["id"])
    assert response.status_code == 200, response.text

    roles = [item["role"] for item in response.json()]
    assert "owner" not in roles