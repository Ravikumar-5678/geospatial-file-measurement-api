from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_unknown_file_id() -> None:
    response = client.get("/api/files/unknown-id/")
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"
