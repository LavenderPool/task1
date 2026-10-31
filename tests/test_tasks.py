def _create_project(client, name: str = "Alpha") -> int:
    response = client.post("/v1/projects", json={"name": name})
    assert response.status_code == 201
    return response.json()["id"]


def test_task_crud_and_filters(client):
    project_id = _create_project(client)
    other_project_id = _create_project(client, "Beta")

    created = client.post(
        "/v1/tasks",
        json={"project_id": project_id, "title": "Write report", "priority": "high"},
    )
    assert created.status_code == 201
    task = created.json()
    task_id = task["id"]
    assert task["project_id"] == project_id
    assert task["title"] == "Write report"
    assert task["status"] == "open"
    assert task["priority"] == "high"
    assert task["assignee_id"] is None
    assert task["label_id"] is None

    other = client.post(
        "/v1/tasks",
        json={"project_id": other_project_id, "title": "Other", "status": "done"},
    )
    assert other.status_code == 201

    listed = client.get("/v1/tasks")
    assert listed.status_code == 200
    assert len(listed.json()) == 2

    by_project = client.get("/v1/tasks", params={"project_id": project_id})
    assert [item["id"] for item in by_project.json()] == [task_id]

    by_status = client.get("/v1/tasks", params={"status": "open"})
    assert [item["id"] for item in by_status.json()] == [task_id]

    fetched = client.get(f"/v1/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Write report"

    updated = client.patch(f"/v1/tasks/{task_id}", json={"status": "in_progress"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "in_progress"

    deleted = client.delete(f"/v1/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get(f"/v1/tasks/{task_id}").status_code == 404


def test_create_task_missing_project(client):
    response = client.post("/v1/tasks", json={"project_id": 999, "title": "Orphan"})
    assert response.status_code == 409
    assert isinstance(response.json()["detail"], str)


def test_create_task_invalid_status(client):
    project_id = _create_project(client)
    response = client.post(
        "/v1/tasks",
        json={"project_id": project_id, "title": "Bad", "status": "archived"},
    )
    assert response.status_code == 422


def test_delete_project_removes_tasks(client):
    project_id = _create_project(client)
    created = client.post("/v1/tasks", json={"project_id": project_id, "title": "Gone"})
    assert created.status_code == 201
    task_id = created.json()["id"]

    deleted = client.delete(f"/v1/projects/{project_id}")
    assert deleted.status_code == 204
    assert client.get(f"/v1/tasks/{task_id}").status_code == 404


def test_get_missing_task(client):
    response = client.get("/v1/tasks/999")
    assert response.status_code == 404
