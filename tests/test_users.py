def test_user_crud(client):
    created = client.post(
        "/v1/users",
        json={"email": "alice@example.com", "display_name": "Alice", "role": "admin"},
    )
    assert created.status_code == 201
    body = created.json()
    user_id = body["id"]
    assert body["email"] == "alice@example.com"
    assert body["display_name"] == "Alice"
    assert body["role"] == "admin"
    assert "created_at" in body

    listed = client.get("/v1/users")
    assert listed.status_code == 200
    assert [user["id"] for user in listed.json()] == [user_id]

    fetched = client.get(f"/v1/users/{user_id}")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "alice@example.com"

    updated = client.patch(
        f"/v1/users/{user_id}",
        json={"display_name": "Alice Updated", "role": "operator"},
    )
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Alice Updated"
    assert updated.json()["role"] == "operator"

    deleted = client.delete(f"/v1/users/{user_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""

    missing = client.get(f"/v1/users/{user_id}")
    assert missing.status_code == 404


def test_get_missing_user(client):
    response = client.get("/v1/users/999")
    assert response.status_code == 404


def test_create_user_invalid_email(client):
    response = client.post(
        "/v1/users",
        json={"email": "not-an-email", "display_name": "Bob"},
    )
    assert response.status_code == 422


def test_create_user_duplicate_email(client):
    first = client.post(
        "/v1/users",
        json={"email": "alice@example.com", "display_name": "Alice"},
    )
    assert first.status_code == 201

    conflict = client.post(
        "/v1/users",
        json={"email": "alice@example.com", "display_name": "Other"},
    )
    assert conflict.status_code == 409
    assert isinstance(conflict.json()["detail"], str)
