def _create_user(client, email: str = "author@example.com") -> int:
    response = client.post(
        "/v1/users",
        json={"email": email, "display_name": "Author"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_task(client) -> int:
    project = client.post("/v1/projects", json={"name": "Alpha"})
    assert project.status_code == 201
    task = client.post(
        "/v1/tasks",
        json={"project_id": project.json()["id"], "title": "Write report"},
    )
    assert task.status_code == 201
    return task.json()["id"]


def test_comment_crud_and_filter(client):
    author_id = _create_user(client)
    task_id = _create_task(client)
    other_task_id = _create_task(client)

    created = client.post(
        "/v1/comments",
        json={"task_id": task_id, "author_id": author_id, "body": "Started"},
    )
    assert created.status_code == 201
    body = created.json()
    comment_id = body["id"]
    assert body["task_id"] == task_id
    assert body["author_id"] == author_id
    assert body["body"] == "Started"
    assert "created_at" in body

    other = client.post(
        "/v1/comments",
        json={"task_id": other_task_id, "author_id": author_id, "body": "Other"},
    )
    assert other.status_code == 201

    listed = client.get("/v1/comments", params={"task_id": task_id})
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [comment_id]

    fetched = client.get(f"/v1/comments/{comment_id}")
    assert fetched.status_code == 200
    assert fetched.json()["body"] == "Started"

    updated = client.patch(f"/v1/comments/{comment_id}", json={"body": "Done"})
    assert updated.status_code == 200
    assert updated.json()["body"] == "Done"

    deleted = client.delete(f"/v1/comments/{comment_id}")
    assert deleted.status_code == 204
    assert client.get(f"/v1/comments/{comment_id}").status_code == 404


def test_create_comment_blank_body(client):
    response = client.post(
        "/v1/comments",
        json={"task_id": 1, "author_id": 1, "body": "   "},
    )
    assert response.status_code == 422


def test_create_comment_missing_task(client):
    author_id = _create_user(client)
    response = client.post(
        "/v1/comments",
        json={"task_id": 999, "author_id": author_id, "body": "Hello"},
    )
    assert response.status_code == 409
    assert isinstance(response.json()["detail"], str)


def test_delete_author_with_comment_conflicts(client):
    author_id = _create_user(client)
    task_id = _create_task(client)
    created = client.post(
        "/v1/comments",
        json={"task_id": task_id, "author_id": author_id, "body": "Hello"},
    )
    assert created.status_code == 201

    conflict = client.delete(f"/v1/users/{author_id}")
    assert conflict.status_code == 409
    assert isinstance(conflict.json()["detail"], str)
    assert client.get(f"/v1/users/{author_id}").status_code == 200


def test_delete_task_removes_comments(client):
    author_id = _create_user(client)
    task_id = _create_task(client)
    created = client.post(
        "/v1/comments",
        json={"task_id": task_id, "author_id": author_id, "body": "Hello"},
    )
    assert created.status_code == 201
    comment_id = created.json()["id"]

    deleted = client.delete(f"/v1/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get(f"/v1/comments/{comment_id}").status_code == 404


def test_get_missing_comment(client):
    response = client.get("/v1/comments/999")
    assert response.status_code == 404
