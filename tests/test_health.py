def test_health_ok(client, monkeypatch):
    class Connection:
        def execute(self, *_args, **_kwargs):
            return None

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

    class HealthyEngine:
        def connect(self):
            return Connection()

    monkeypatch.setattr("app.main.engine", HealthyEngine())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up"}


def test_health_database_down(client, monkeypatch):
    class BrokenEngine:
        def connect(self):
            raise RuntimeError("down")

    monkeypatch.setattr("app.main.engine", BrokenEngine())

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection failed"
