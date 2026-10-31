def test_label_crud(client):
    created = client.post("/v1/labels", json={"name": "bug", "color": "#ef4444"})
    assert created.status_code == 201
    body = created.json()
    label_id = body["id"]
    assert body["name"] == "bug"
    assert body["color"] == "#ef4444"

    listed = client.get("/v1/labels")
    assert listed.status_code == 200
    assert [label["id"] for label in listed.json()] == [label_id]

    fetched = client.get(f"/v1/labels/{label_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "bug"

    updated = client.patch(
        f"/v1/labels/{label_id}",
        json={"name": "defect", "color": "#22c55e"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "defect"
    assert updated.json()["color"] == "#22c55e"

    deleted = client.delete(f"/v1/labels/{label_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/v1/labels/{label_id}")
    assert missing.status_code == 404


def test_create_label_uses_default_color(client):
    response = client.post("/v1/labels", json={"name": "chore"})
    assert response.status_code == 201
    assert response.json()["color"] == "#6b7280"


def test_create_label_invalid_color(client):
    response = client.post("/v1/labels", json={"name": "bug", "color": "red"})
    assert response.status_code == 422


def test_create_label_duplicate_name(client):
    first = client.post("/v1/labels", json={"name": "bug"})
    assert first.status_code == 201

    conflict = client.post("/v1/labels", json={"name": "bug", "color": "#000000"})
    assert conflict.status_code == 409
    assert isinstance(conflict.json()["detail"], str)


def test_get_missing_label(client):
    response = client.get("/v1/labels/999")
    assert response.status_code == 404
