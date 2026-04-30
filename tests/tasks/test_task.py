import uuid


def create_org(client, auth_headers, name="Tasks Org", slug=None):
    slug = slug or f"tasks-org-{uuid.uuid4().hex[:8]}"
    payload = {
        "name": name,
        "slug": slug,
        "description": "Tasks test organization",
    }
    response = client.post("/api/v1/organizations/", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()


def create_project(client, auth_headers, organization_id, name="Tasks Project"):
    payload = {
        "name": name,
        "description": "Tasks test project",
        "organization_id": organization_id,
    }
    response = client.post("/api/v1/projects", json=payload, headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()


def create_task(client, auth_headers, project_id, title="First Task"):
    payload = {
        "title": title,
        "description": "Task created in test",
        "project_id": project_id,
        "priority": "medium",
    }
    response = client.post("/api/v1/tasks", json=payload, headers=auth_headers)
    return response, payload


def test_create_task_success(client, auth_headers):
    org = create_org(client, auth_headers)
    project = create_project(client, auth_headers, org["id"])

    response, payload = create_task(client, auth_headers, project["id"])

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["project_id"] == project["id"]
    assert data["priority"] == "medium"
    assert data["status"]


def test_create_task_project_not_found(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Ghost task",
            "description": "Should fail",
            "project_id": str(uuid.uuid4()),
            "priority": "medium",
        },
        headers=auth_headers,
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Project not found"


def test_create_task_unauthorized(client):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "No auth",
            "description": "Should fail",
            "project_id": str(uuid.uuid4()),
            "priority": "medium",
        },
    )

    assert response.status_code == 401, response.text


def test_list_tasks_success(client, auth_headers):
    org = create_org(client, auth_headers, slug=f"list-org-{uuid.uuid4().hex[:8]}")
    project = create_project(client, auth_headers, org["id"], name="List Tasks Project")

    first_response, _ = create_task(client, auth_headers, project["id"], title="Task A")
    second_response, _ = create_task(client, auth_headers, project["id"], title="Task B")

    assert first_response.status_code == 201, first_response.text
    assert second_response.status_code == 201, second_response.text

    response = client.get(
        "/api/v1/tasks",
        params={"project_id": project["id"]},
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 2
    titles = [item["title"] for item in data]
    assert "Task A" in titles
    assert "Task B" in titles


def test_list_tasks_unauthorized(client):
    response = client.get(
        "/api/v1/tasks",
        params={"project_id": str(uuid.uuid4())},
    )

    assert response.status_code == 401, response.text


def test_update_task_success(client, auth_headers):
    org = create_org(client, auth_headers, slug=f"update-org-{uuid.uuid4().hex[:8]}")
    project = create_project(client, auth_headers, org["id"], name="Update Tasks Project")
    create_response, _ = create_task(client, auth_headers, project["id"], title="Old Title")
    assert create_response.status_code == 201, create_response.text

    task = create_response.json()

    response = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={
            "title": "New Title",
            "status": "in_progress",
            "priority": "high",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "New Title"
    assert data["status"] == "in_progress"
    assert data["priority"] == "high"


def test_update_task_not_found(client, auth_headers):
    response = client.patch(
        f"/api/v1/tasks/{uuid.uuid4()}",
        json={"title": "Does not exist"},
        headers=auth_headers,
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Task not found"


def test_delete_task_success(client, auth_headers):
    org = create_org(client, auth_headers, slug=f"delete-org-{uuid.uuid4().hex[:8]}")
    project = create_project(client, auth_headers, org["id"], name="Delete Tasks Project")
    create_response, _ = create_task(client, auth_headers, project["id"], title="Delete Me")
    assert create_response.status_code == 201, create_response.text

    task = create_response.json()

    response = client.delete(
        f"/api/v1/tasks/{task['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 204, response.text

    get_after_delete = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"title": "Should not exist"},
        headers=auth_headers,
    )

    assert get_after_delete.status_code == 404, get_after_delete.text


def test_delete_task_not_found(client, auth_headers):
    response = client.delete(
        f"/api/v1/tasks/{uuid.uuid4()}",
        headers=auth_headers,
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "Task not found"