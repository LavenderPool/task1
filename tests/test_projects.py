def test_project_crud(client):
    created = client.post(
        "/v1/projects",
        json={"name": "Alpha", "description": "First project"},
    )
    assert created.status_code == 201
    body = created.json()
    project_id = body["id"]
    assert body["name"] == "Alpha"
    assert body["description"] == "First project"
    assert "created_at" in body

    listed = client.get("/v1/projects")
    assert listed.status_code == 200
    assert [project["id"] for project in listed.json()] == [project_id]

    fetched = client.get(f"/v1/projects/{project_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Alpha"

    updated = client.patch(
        f"/v1/projects/{project_id}",
        json={"name": "Alpha Updated", "description": None},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Alpha Updated"
    assert updated.json()["description"] is None

    deleted = client.delete(f"/v1/projects/{project_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/v1/projects/{project_id}")
    assert missing.status_code == 404


def test_get_missing_project(client):
    response = client.get("/v1/projects/999")
    assert response.status_code == 404
